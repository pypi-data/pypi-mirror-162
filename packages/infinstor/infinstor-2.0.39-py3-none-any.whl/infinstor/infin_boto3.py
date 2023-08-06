from datetime import datetime, timezone
import builtins
import boto3
from botocore.response import StreamingBody
import functools
import os
import sys
from os.path import expanduser
import json
import re
import mlflow
from mlflow.tracking import MlflowClient
from urllib.parse import urlparse, quote
from urllib.request import urlretrieve, urlopen
from requests.exceptions import HTTPError
import requests
import infinstor
from infinstor import bootstrap, tokenfile
import xmltodict


verbose = True
fuse_debug_handle = None
fuse_debug_file = "/tmp/fuse_debug.log"

def print_unbufferred(*args, **kwargs):
    global fuse_debug_handle
    if fuse_debug_handle is None:
        fuse_debug_handle = open(fuse_debug_file, "a")

    if verbose:
        binary_args = []
        for arg in args:
            binary_args.append(str(arg).encode('utf-8'))
        print(*binary_args, file=fuse_debug_handle, **kwargs)
        fuse_debug_handle.close()
        fuse_debug_handle = open(fuse_debug_file, "a")

class ListObjectsPaginator():
    def __init__(self, type2, infin_boto_client, infinsnap_buckets = [], non_infinsnap_buckets = []):
        self.type2 = type2
        self.infin_boto_client = infin_boto_client
        self.infinsnap_buckets = infinsnap_buckets
        self.non_infinsnap_buckets = non_infinsnap_buckets
        self.all_buckets = infinsnap_buckets + non_infinsnap_buckets
        self.next_token = None
        self.finished = False

    def paginate(self, **kwargs):
        if 'Bucket' not in kwargs:
            raise ValueError("Bucket must be specified for list-objects-v2 paginate")
        self.bucket = kwargs['Bucket']
        if self.bucket not in self.all_buckets:
            passthru = self.infin_boto_client.defaultClient.get_paginator('list_objects_v2')
            return passthru.paginate(**kwargs)
        else:
            self.kwargs = kwargs
            return self

    def __iter__(self):
        return self
    def __next__(self):
        if self.finished:
            raise StopIteration
        if (self.next_token):
            if self.type2:
                self.kwargs['ContinuationToken'] = self.next_token
            else:
                self.kwargs['Marker'] = self.next_token
        if self.type2:
            rv = self.infin_boto_client.list_objects_v2(None, **self.kwargs)
            if 'NextContinuationToken' in rv:
                self.next_token = rv['NextContinuationToken']
                del rv['NextContinuationToken']
            else:
                self.finished = True
            return rv
        else:
            rv = self.infin_boto_client.list_objects(None, **self.kwargs)
            if 'NextMarker' in rv:
                self.next_token = rv['NextMarker']
                del rv['NextMarker']
            else:
                self.finished = True
            return rv

class Bucket():
    def __init__(self, name):
        self.name = name

class BucketsCollection():
    def __init__(self, infinsnap_buckets, non_infinsnap_buckets):
        self._infinsnap_buckets = [Bucket(b) for b in infinsnap_buckets]
        self._non_infinsnap_buckets = [Bucket(b) for b in non_infinsnap_buckets]
    def all(self):
        return self._infinsnap_buckets + self._non_infinsnap_buckets
    def infinsnap_buckets(self):
        return self._infinsnap_buckets
    def non_infinsnap_buckets(self):
        return self._non_infinsnap_buckets

class S3ResourceMeta():
    def __init__(self, default_meta, infin_client):
        self.default_meta = default_meta
        self.infin_client = infin_client
    def __getattr__(self, attr):
        if attr == 'client':
            return self.infin_client
        else:
            return getattr(self.default_meta, attr)

class InfinBotoResource():
    def __init__(self, defaultResource, timespec_info):
        self.defaultResource = defaultResource
        self.timespec_info = timespec_info
        self.bucketscollection = BucketsCollection(timespec_info['infinsnap_buckets'], timespec_info['non_infinsnap_buckets'])
        self.s3_resource_meta = S3ResourceMeta(self.defaultResource.meta,
                InfinBotoClient(defaultResource.meta.client, timespec_info))

    def __getattr__(self, attr):
        if attr == 'buckets':
            return self.bucketscollection
        elif attr == 'meta':
            return self.s3_resource_meta
        else:
            return getattr(self.defaultResource, attr)

class InfinBotoClient():
    def __init__(self, defaultClient, timespec_info):
        # self.__class__ = type(baseObject.__class__.__name__,
        #                       (self.__class__, baseObject.__class__),
        #                       {})
        # self.__dict__ = baseObject.__dict__
        self.defaultClient = defaultClient
        self.timespec_info = timespec_info
        self.bucket = None
        self.prefix = None
        self.have_printed_greeting = False

    def list_objects(self, *args, **kwargs):
        if self.timespec_info['type'] == 'infinsnap' or self.timespec_info['type'] == 'infinslice':
            if self.bucket:
                request_bucket = self.bucket
                request_prefix = self.prefix
            elif kwargs['Bucket']:
                request_bucket = kwargs['Bucket']
                request_prefix = kwargs['Prefix']
            else:
                raise ValueError("bucket must be specified")
            if request_bucket in self.timespec_info['infinsnap_buckets']:
                kwargs['Bucket'] = request_bucket
                kwargs['Prefix'] = request_prefix
                return self.list_objects_at(False, *args, **kwargs)
            elif request_bucket in self.timespec_info['non_infinsnap_buckets']:
                kwargs['Bucket'] = request_bucket
                kwargs['Prefix'] = request_prefix
                run_id = self.parse_run_id(request_prefix)
                if run_id:
                    return self.list_objects_presigned(request_bucket, request_prefix, run_id)
                else:
                    return self.defaultClient.list_objects(**kwargs)
            else:
                return self.defaultClient.list_objects(**kwargs)
        else:
            return self.defaultClient.list_objects(**kwargs)

    def print_greeting(self):
        if not self.have_printed_greeting:
            try:
                print('infin_boto3: intercept activated for buckets='
                    + str(self.timespec_info['infinsnap_buckets'] + self.timespec_info['non_infinsnap_buckets']))
            except Exception as ex:
                pass
            self.have_printed_greeting = True

    def parse_run_id(self, prefix):
        #match pattern like /22/22-16547558543270000000139/
        run_id = None
        m = re.match("^.*\/(\d+)\/(\d+)-(\d{23})(\/|$)", prefix)
        if m:
            groups = m.groups()
            if groups and len(groups) >= 3 and groups[0] == groups[1] and len(groups[2]) == 23:
                run_id = groups[1] + '-' + groups[2]

        return run_id


    def to_json_response(self, response, content_key):
        respj = xmltodict.parse(response.content)
        respj = respj[content_key]
        if 'Contents' in respj:
            if type(respj['Contents']) != list:
                respj['Contents'] = [respj['Contents']]

        if 'CommonPrefixes' in respj:
            if type(respj['CommonPrefixes']) != list:
                respj['CommonPrefixes'] = [respj['CommonPrefixes']]

        return respj


    def list_objects_v2(self, *args, **kwargs):
        self.print_greeting()
        if self.timespec_info['type'] == 'infinsnap' or self.timespec_info['type'] == 'infinslice':
            if self.bucket:
                request_bucket = self.bucket
                request_prefix = self.prefix
            elif kwargs['Bucket']:
                request_bucket = kwargs['Bucket']
                request_prefix = kwargs['Prefix']
            else:
                raise ValueError("bucket must be specified")
            if request_bucket in self.timespec_info['infinsnap_buckets']:
                kwargs['Bucket'] = request_bucket
                kwargs['Prefix'] = request_prefix
                return self.list_objects_at(True, *args, **kwargs)
            elif request_bucket in self.timespec_info['non_infinsnap_buckets']:
                kwargs['Bucket'] = request_bucket
                kwargs['Prefix'] = request_prefix
                run_id = self.parse_run_id(request_prefix)
                if run_id:
                    return self.list_objects_v2_presigned(request_bucket, request_prefix, run_id)
                else:
                    return self.defaultClient.list_objects_v2(**kwargs)
            else:
                return self.defaultClient.list_objects_v2(**kwargs)
        else:
            return self.defaultClient.list_objects_v2(**kwargs)

    def download_file(self, *args, **kwargs):
        print_unbufferred('DEBUG download_file', args, kwargs)
        if self.timespec_info['type'] == 'infinsnap' or self.timespec_info['type'] == 'infinslice':
            request_bucket = args[0]
            request_file = args[1]
            if request_bucket in self.timespec_info['infinsnap_buckets']:
                self.print_greeting()
                versionId, presignedUrl = self.get_version_id(request_bucket, request_file)
                if (versionId != None):
                    if self.timespec_info['use_presigned_url_for_infinsnap']:
                        urlretrieve(presignedUrl, args[2])
                        return
                    else:
                        if 'ExtraArgs' in kwargs:
                            kwargs['ExtraArgs']['VersionId'] = versionId
                        else:
                            kwargs['ExtraArgs'] = {'VersionId': versionId}
                        return self.defaultClient.download_file(*args, **kwargs)
                else:
                    raise ValueError('download_file: versionId not present. Is InfinSnap enabled?')
            elif request_bucket in self.timespec_info['non_infinsnap_buckets']:
                run_id = self.parse_run_id(request_file)
                if run_id:
                    print_unbufferred("DEBUG: Download file using presigned url")
                    return self.download_file_presigned(request_bucket, request_file, run_id, args[2])
                else:
                    return self.defaultClient.download_file(*args, **kwargs)
            else:
                return self.defaultClient.download_file(*args, **kwargs)
        else:
            return self.defaultClient.download_file(*args, **kwargs)

    def get_auth_header(self, force=False):
        token = tokenfile.get_token(builtins.region, force)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': token
        }
        return headers

    def get_version_id(self, bucket, prefix):
        attempt = 0
        while attempt < 2:
            if attempt == 0:
                force = False
            else:
                print('get_version_id: attempt = ' + str(attempt) + ', force True')
                force = True
            attempt = attempt + 1
            token = tokenfile.get_token(builtins.region, force)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': token
                }

            url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/infinstor/s3meta'\
                    + '?prefix=' + quote(prefix.lstrip('/')) \
                    + '&op=get-filestatus&bucket=' + bucket\
                    + '&gets3url=true'
            if self.timespec_info['type'] == 'infinsnap':
                time_spec = self.timespec_info['time_spec']
                url = url + '&endTime=' + str(self.infinsnap_to_epoch(time_spec))
            elif self.timespec_info['type'] == 'infinslice':
                time_spec = self.timespec_info['time_spec']
                st, en = self.infinslice_to_epochs(time_spec)
                url = url + '&startTime=' + str(st) + '&endTime=' + str(en)
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except HTTPError as http_err:
                print('HTTP error occurred: ' + str(http_err))
                raise
            except Exception as err:
                print('Other error occurred: ' + str(err))
                raise
            if 'Login expired. Please login again' in response.text:
                continue
            js = response.json()
            if 'versionId' in js:
                return js['versionId'], js['s3url']
            else:
                print('get_version_id: versionId not present in response=' + json.dumps(js))
                return None, None
        print('get_version_id: Tried twice. Giving up')
        return None, None

    def get_presigned_url(self, prefix, run_id, method):
        headers = self.get_auth_header()
        url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/artifacts/getpresignedurl'
        url = url + '?run_id=' + run_id
        url = url + '&path=' + quote(prefix)
        url = url + '&method=' + method
        response = requests.get(url, headers=headers)
        respj = response.json()
        presigned_url = respj['presigned_url']
        return presigned_url

    def download_file_presigned(self, request_bucket, request_file, run_id, local_path):
        ps_url = self.get_presigned_url(request_file, run_id, 'get_object')
        try:
            urlretrieve(ps_url, local_path)
        except Exception as ex:
            raise Exception("Url retrieve failed")
        return

    def get_object_presigned(self, request_bucket, request_file, run_id):
        ps_url = self.get_presigned_url(request_file, run_id, 'get_object')
        response = urlopen(ps_url)
        clen = response.getheader('Content-Length')
        rv = {'Body': StreamingBody(response, clen),
              'ContentLength': int(clen),
              'ContentType': response.getheader('Content-Type')}
        if response.getheader('Last-Modified'):
            rv['LastModified'] = datetime.strptime(
                response.getheader('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z')
        return rv

    def list_objects_v2_presigned(self, request_bucket, request_prefix, run_id):
        ps_url = self.get_presigned_url(request_prefix, run_id, 'list_objects_v2')
        response = requests.get(ps_url)
        respj = self.to_json_response(response, 'ListBucketResult')
        return respj

    def list_objects_presigned(self, request_bucket, request_prefix, run_id):
        ps_url = self.get_presigned_url(request_prefix, run_id, 'list_objects')
        response = requests.get(ps_url)
        respj = self.to_json_response(response, 'ListBucketResult')
        return respj

    def list_objects_at(self, type2, *args, **kwargs):
        request_bucket = kwargs['Bucket']
        request_prefix = kwargs.get('Prefix')
        attempt = 0
        while attempt < 2:
            if attempt == 0:
                force = False
            else:
                force = True
            attempt = attempt + 1
            token = tokenfile.get_token(builtins.region, force)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': token
                }
            if type2:
                list_type = 2
            else:
                list_type = 1
            if not request_prefix:
                request_prefix = ''
            url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/infinstor/s3meta'\
                    + '?prefix=' + quote(request_prefix.lstrip('/')) \
                    + '&op=list-objects&bucket=' + request_bucket + '&list-type=' + str(list_type)\
                    + '&output-format=json'
            if self.timespec_info['type'] == 'infinsnap':
                time_spec = self.timespec_info['time_spec']
                url = url + '&endTime=' + str(self.infinsnap_to_epoch(time_spec))
            elif self.timespec_info['type'] == 'infinslice':
                time_spec = self.timespec_info['time_spec']
                st, en = self.infinslice_to_epochs(time_spec)
                url = url + '&startTime=' + str(st) + '&endTime=' + str(en)
            if ('Delimiter' in kwargs):
                url = url + '&Delimiter=' + kwargs['Delimiter']
            if ('Marker' in kwargs):
                url = url + '&Marker=' + kwargs['Marker']
            if ('ContinuationToken' in kwargs):
                url = url + '&ContinuationToken=' + kwargs['ContinuationToken']
            if ('StartAfter' in kwargs):
                url = url + '&StartAfter=' + kwargs['StartAfter']
            if ('MaxKeys' in kwargs):
                url = url + '&MaxKeys=' + str(kwargs['MaxKeys'])
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except HTTPError as http_err:
                print('HTTP error occurred: ' + str(http_err))
                raise
            except Exception as err:
                print('Other error occurred: ' + str(err))
                raise
            if 'Login expired. Please login again' in response.text:
                continue
            respj = response.json()
            if 'Contents' in respj:
                for one in respj['Contents']:
                    if 'LastModified' in one:
                        one['LastModified'] = datetime.fromtimestamp(one['LastModified']/1000)
            return respj
        print('list_objects_at: Tried twice. Giving up')
        return None

    def infinsnap_to_epoch(self, time_spec):
        if (len(time_spec) != 16 or not time_spec.startswith("tm")):
            raise ValueError('Incorrectly formatted infinsnap time_spec ' + time_spec)
        year = int(time_spec[2:6])
        month = int(time_spec[6:8])
        day = int(time_spec[8:10])
        hour = int(time_spec[10:12])
        minute = int(time_spec[12:14])
        second = int(time_spec[14:])
        dt = datetime(year, month, day, hour, minute, second, 0, tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000.0)

    def infinslice_to_epochs(self, time_spec):
        if (len(time_spec) != 33 or not time_spec.startswith("tm")):
            raise ValueError('Incorrectly formatted infinslice time_spec ' + time_spec)
        year = int(time_spec[2:6])
        month = int(time_spec[6:8])
        day = int(time_spec[8:10])
        hour = int(time_spec[10:12])
        minute = int(time_spec[12:14])
        second = int(time_spec[14:16])
        dt1 = datetime(year, month, day, hour, minute, second, 0, tzinfo=timezone.utc)
        year = int(time_spec[19:23])
        month = int(time_spec[23:25])
        day = int(time_spec[25:27])
        hour = int(time_spec[27:29])
        minute = int(time_spec[29:31])
        second = int(time_spec[31:])
        dt2 = datetime(year, month, day, hour, minute, second, 0, tzinfo=timezone.utc)
        return int(dt1.timestamp() * 1000.0), int(dt2.timestamp() * 1000.0)

    def get_object(self, **kwargs):
        if self.timespec_info['type'] == 'infinsnap' or self.timespec_info['type'] == 'infinslice':
            request_bucket = kwargs['Bucket']
            request_file = kwargs['Key']
            if request_bucket in self.timespec_info['infinsnap_buckets']:
                self.print_greeting()
                versionId, presignedUrl = self.get_version_id(request_bucket, request_file)
                if (versionId != None):
                    if self.timespec_info['use_presigned_url_for_infinsnap']:
                        print("Using presigned url for get_object", flush=True)
                        res = urlopen(presignedUrl)
                        clen = res.getheader('Content-Length')
                        rv = {'Body': StreamingBody(res, clen),
                              'ContentLength': int(clen),
                              'ContentType': res.getheader('Content-Type')}
                        if res.getheader('Last-Modified'):
                            rv['LastModified'] = datetime.strptime(
                                res.getheader('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z')
                        return rv
                    else:
                        print("Using versionid for get_object", flush=True)
                        kwargs['VersionId'] = versionId
                        return self.defaultClient.get_object(**kwargs)
                else:
                    raise ValueError('get_object: versionId not present. Is InfinSnap enabled?')
            elif request_bucket in self.timespec_info['non_infinsnap_buckets']:
                run_id = self.parse_run_id(request_file)
                if run_id:
                    return self.get_object_presigned(request_bucket, request_file, run_id)
                else:
                    return self.defaultClient.get_object(**kwargs)
            else:
                return self.defaultClient.get_object(**kwargs)
        else:
            return self.defaultClient.get_object(**kwargs)

    def get_paginator(self, operation_name):
        if operation_name == 'list_objects':
            self.print_greeting()
            return ListObjectsPaginator(False, self, self.timespec_info['infinsnap_buckets'], self.timespec_info['non_infinsnap_buckets'])
        elif operation_name == 'list_objects_v2':
            self.print_greeting()
            return ListObjectsPaginator(True, self, self.timespec_info['infinsnap_buckets'], self.timespec_info['non_infinsnap_buckets'])
        else:
            return self.defaultClient.get_paginator(operation_name)

    def __getattr__(self, attr):
        if attr == 'list_objects':
            return self.list_objects
        elif attr == 'list_objects_v2':
            return self.list_objects_v2
        elif attr == 'download_file':
            return self.download_file
        elif attr == 'get_object':
            return self.get_object
        elif attr == 'get_paginator':
            return self.get_paginator
        else:
            return getattr(self.defaultClient, attr)

# returns bucketlist, use_presigned_url_for_infinsnap
def get_customerinfo():
    token = tokenfile.get_token(builtins.region, False)
    payload = "ProductCode=9fcazc4rbiwp6ewg4xlt5c8fu"
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': token
            }

    url = 'https://' + builtins.apiserver + '/customerinfo'

    try:
        response = requests.post(url, data=payload+'&clientType=browser', headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return []
    except Exception as err:
        print(f'Other error occurred: {err}')
        return []
    else:
        rv = []
        rj = response.json()
        if 'InfinSnapBuckets' in rj:
            for onebucket in rj['InfinSnapBuckets']:
                rv.append(onebucket)
        if 'usePresignedUrlForInfinSnap' in rj and rj['usePresignedUrlForInfinSnap'] == 'true':
            print('get_customerinfo: usePresignedUrlForInfinSnap='
                    + str(rj['usePresignedUrlForInfinSnap']))
            use_presigned_url_for_infinsnap = True
        else:
            print('get_customerinfo: no usePresignedUrlForInfinSnap')
            use_presigned_url_for_infinsnap = False

        if 'usePresignedUrlForMLflow' in rj and rj['usePresignedUrlForMLflow'] == 'true':
            print('get_customerinfo: usePresignedUrlForMLflow='
                  + str(rj['usePresignedUrlForMLflow']))
            use_presigned_url_for_mlflow = True
        else:
            print('get_customerinfo: no usePresignedUrlForMLflow')
            use_presigned_url_for_mlflow = False

        return rv, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow

##Decorators are specific to functions

def is_infinsnap_bucket(onebucket):
    if 'ddbTable' in onebucket and onebucket['ddbTable'] is not None:
        return True
    else:
        return False

##Decorator for boto3.Session.client
def decorate_boto3_client(client_func):
    orig_func = client_func
    @functools.wraps(client_func)
    def wrapper(*args, **kwargs):
        if args[1] == 's3':
            if 'infinstor_time_spec' in kwargs:
                time_spec = kwargs['infinstor_time_spec']
                del kwargs['infinstor_time_spec']
                print('infinstor: Activating time_spec=' + time_spec)
                bucket_infos, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow = get_customerinfo()
                if (len(time_spec) == 33):
                    timespec_info = {
                        'type': 'infinslice',
                        'time_spec': time_spec,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                    }
                elif (len(time_spec) == 16):
                    timespec_info = {
                        'type': 'infinsnap',
                        'time_spec': time_spec,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                    }
                else:
                    raise ValueError('Incorrectly formatted infinstor_time_spec '
                            + str(time_spec))
                defaultClient = orig_func(*args, **kwargs)
                return InfinBotoClient(defaultClient, timespec_info)
            elif builtins.mlflowserver and mlflow.active_run() != None:
                if ('INFINSTOR_SNAPSHOT_TIME' in os.environ):
                    epoch_time = get_epoch_time_from_env(os.environ['INFINSTOR_SNAPSHOT_TIME'])
                else:
                    epoch_time = mlflow.active_run().info.start_time
                time_spec = infinstor.infinsnap(datetime.fromtimestamp(epoch_time/1000))
                mlflow.log_param('infinstor_snapshot_time', epoch_time)
                bucket_infos, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow = get_customerinfo()
                timespec_info = {
                        'type': 'infinsnap',
                        'epoch_time': epoch_time,
                        'time_spec': time_spec,
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                               is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                            }
                print('infinstor: Activating implicit infinsnap/slice. Snapshot time='
                    + datetime.fromtimestamp(epoch_time/1000).strftime("%m/%d/%Y %H:%M:%S"))
                defaultClient = orig_func(*args, **kwargs)
                return InfinBotoClient(defaultClient, timespec_info)
            else:
                bucket_infos, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow = get_customerinfo()
                timespec_info = {
                    'type': 'infinsnap',
                    'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                    'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                          is_infinsnap_bucket(onebucket)],
                    'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              not is_infinsnap_bucket(onebucket)],
                    'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                }
                defaultClient = orig_func(*args, **kwargs)
                return InfinBotoClient(defaultClient, timespec_info)
        defaultClient = orig_func(*args, **kwargs)
        return defaultClient
    return wrapper

def get_epoch_time_from_env(envvar):
    if envvar.startswith('run:/'):
        client = MlflowClient()
        run = client.get_run(envvar[5:])
        for key, value in run.data.params.items():
            if key == 'infinstor_snapshot_time':
                return int(value)
        # No infinstor_snapshot_time param. use run start time
        return run.info.start_time
    else:
        return int(envvar)

##Decorator for boto3.Session.resource
def decorate_boto3_resource(resource_func):
    orig_func = resource_func
    @functools.wraps(resource_func)
    def wrapper(*args, **kwargs):
        if 'infinstor_time_spec' in kwargs:
            time_spec = kwargs['infinstor_time_spec']
            del kwargs['infinstor_time_spec']
            print('infinstor: Activating time_spec=' + time_spec)
            bucket_infos, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow = get_customerinfo()
            if bucket_infos:
                if (len(time_spec) == 33):
                    timespec_info = {
                        'type': 'infinslice',
                        'time_spec': time_spec,
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                        }
                elif (len(time_spec) == 16):
                    timespec_info = {
                        'type': 'infinsnap',
                        'time_spec': time_spec,
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                        }
                else:
                    raise ValueError('Incorrectly formatted infinstor_time_spec '
                        + str(time_spec))
                defaultResource = orig_func(*args, **kwargs)
                return InfinBotoResource(defaultResource, timespec_info)
            elif builtins.mlflowserver and mlflow.active_run() != None:
                if ('INFINSTOR_SNAPSHOT_TIME' in os.environ):
                    epoch_time = get_epoch_time_from_env(os.environ['INFINSTOR_SNAPSHOT_TIME'])
                else:
                    epoch_time = mlflow.active_run().info.start_time
                time_spec = infinstor.infinsnap(epoch_time)
                mlflow.log_param('infinstor_snapshot_time', epoch_time)
                bucket_infos, use_presigned_url_for_infinsnap, use_presigned_url_for_mlflow = get_customerinfo()
                timespec_info = {
                        'type':'infinsnap',
                        'epoch_time': epoch_time,
                        'time_spec': time_spec,
                        'use_presigned_url_for_infinsnap': use_presigned_url_for_infinsnap,
                        'infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                              is_infinsnap_bucket(onebucket)],
                        'non_infinsnap_buckets': [onebucket['bucketname'] for onebucket in bucket_infos if
                                                  not is_infinsnap_bucket(onebucket)],
                        'use_presigned_url_for_mlflow': use_presigned_url_for_mlflow
                    }
                print('infinstor: Activating implicit infinsnap/slice. Snapshot time='
                    + datetime.fromtimestamp(epoch_time/1000).strftime("%m/%d/%Y %H:%M:%S"))
                defaultResource = orig_func(*args, **kwargs)
                return InfinBotoResource(defaultResource, timespec_info)
        defaultResource = orig_func(*args, **kwargs)
        return defaultResource
    return wrapper

def get_infin_output_location(run_id=None, default_bucket=None, default_prefix="/"):
    if not run_id:
        active_run = mlflow.active_run()
        if active_run:
            run_id = mlflow.active_run().info.run_id
    if run_id:
        client = mlflow.tracking.MlflowClient()
        run = client.get_run(run_id)
        artifact_uri = run.info.artifact_uri
        parse_result = urlparse(artifact_uri)
        if (parse_result.scheme != 's3'):
            raise ValueError('Error. Do not know how to deal with artifacts in scheme ' \
                             + parse_result.scheme)
        bucketname = parse_result.netloc
        prefix = parse_result.path.lstrip('/')
        return bucketname, prefix
    else:
        return default_bucket, default_prefix

bootstrap.bootstrap_config_values_from_mlflow_rest_if_needed()
boto3.Session.client = decorate_boto3_client(boto3.Session.client)
boto3.Session.resource = decorate_boto3_resource(boto3.Session.resource)

###Intercepting Logic####
"""
1. User declares an input bucket
2. If input spec is infinsnap or infinslice
    If bucket in inputspec is same as declared input bucket
        change the endpoint url
        don't intercept any other calls --> THIS WILL CHANGE FOR PARTITIONING
    else
        don't change anything
3. If the input spec is mlflow artifact
    Don't change the endpoint url, but intercept the read/list
    if bucket in the call is same as declared input bucket
        change the bucket to the mlflow artifact uri bucket
    else
        don't do anything
"""
