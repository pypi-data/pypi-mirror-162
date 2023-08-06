import boto3
import io
from io import StringIO, BytesIO
import pandas as pd
try:
    import exceptions
except ImportError:
    import builtins as exceptions
from botocore.exceptions import ClientError


class Boto:


    def __init__(self, region='us-east-1'):
        self.__region = region
        if region is None:
            region = boto3.session.Session().region_name
            if region is None:
                raise Exceptions.NoRegionFoundError("No default aws region configuration found. Must specify a region.")
        self.__s3 = boto3.client('s3', region_name=region)


    # ##########################################################################
    def put_df(self, bucket: str, key: str, dataframe, header: bool, index: bool, sep=','):
        buffer = StringIO()  # creating an empty buffer
        dataframe.to_csv(buffer, sep=sep, header=header, index=index)  # filling the buffer
        buffer.seek(0)  # set to the start of the stream
        buffer = BytesIO(buffer.getvalue().encode())

        try:
            s3_client = boto3.client('s3')
            result = s3_client.put_object(
                Body=buffer,
                Bucket=bucket,
                Key=key,
            )
            metadata = result['ResponseMetadata']
            key_check = self.get_keys(bucket, key)[0]
            response = {'HTTPStatusCode': str(metadata['HTTPStatusCode']),
                        'Key': key_check['Key'],
                        'LastModified': key_check['LastModified']
                        }
        except ClientError as e:
            raise e

        return response


    # ##########################################################################
    def put_file(self, bucket: str, key: str, file_or_buffer):
        buffer = StringIO()  # creating an empty buffer
        buffer.seek(0)  # set to the start of the stream
        buffer = BytesIO(file_or_buffer.encode())

        try:
            s3_client = boto3.client('s3')
            result = s3_client.put_object(
                Body=buffer,
                Bucket=bucket,
                Key=key,
            )
            metadata = result['ResponseMetadata']
            key_check = self.get_keys(bucket, key)[0]
            response = {'HTTPStatusCode': str(metadata['HTTPStatusCode']),
                        'Key': key_check['Key'],
                        'LastModified': key_check['LastModified']
                        }
        except ClientError as e:
            raise e

        return response


    # ##########################################################################
    def get_csv_as_df(self, bucket: str, key: str, sep=',', skiprows=None, encoding='utf-8', dict_dtypes=None, index=None):

        try:
            s3_client = boto3.client('s3')
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(BytesIO(obj['Body'].read()), names=None, skiprows=skiprows, header='infer', sep=sep, encoding=encoding, dtype=dict_dtypes, index_col=index)
        except ClientError as e:
            raise e

        return df


    # ##########################################################################
    def get_file(self, bucket: str, key: str):

        try:
            s3_client = boto3.client('s3')
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            bytes_obj = BytesIO(obj['Body'].read()).read()
            file_body = bytes_obj.decode('UTF-8')
        except ClientError as e:
            raise e

        return file_body


    # ##########################################################################
    def get_keys(self, bucket: str, prefix = ''):
        try:
            s3_client = boto3.client('s3')
            result = s3_client.list_objects(
                Bucket=bucket,
                Delimiter=',',
                MaxKeys=1000,
                Prefix=prefix
            )
            object_list = []
            for obj in result['Contents']:
                obj_dict = {'Key': obj['Key'], 'LastModified': str(obj['LastModified'])}
                object_list.append(obj_dict)
        except ClientError as e:
            raise e

        return object_list

    # ##########################################################################
    def get_excel(self, bucket: str, key: str, engine = None):
        try:
            s3_client = boto3.client('s3')
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            bytes_obj = BytesIO(obj['Body'].read())
            excelfile = pd.ExcelFile(bytes_obj, engine = engine)
        except ClientError as e:
            raise e

        return excelfile

    # ##########################################################################
    def put_excel(self, bucket: str, key: str, dataframe, header: bool,index: bool):
        with io.BytesIO() as output:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dataframe.to_excel(writer,sheet_name='Sheet1',header=header,index=index)
            data = output.getvalue()
        try:
            s3_client = boto3.client('s3')
            result = s3_client.put_object(
                Body=data,
                Bucket=bucket,
                Key=key,
            )
            metadata = result['ResponseMetadata']
            key_check = self.get_keys(bucket, key)[0]
            response = {'HTTPStatusCode': str(metadata['HTTPStatusCode']),
                        'Key': key_check['Key'],
                        'LastModified': key_check['LastModified']
                        }
        except ClientError as e:
            raise e

        return response