import gzip
import pickle
import boto3
from pandas import DataFrame, read_csv, read_pickle
from io import StringIO,BytesIO
import os
import logging


class ConnectS3:

    @staticmethod
    def create_connection(
            aws_access_key_id="AKIA2YVKI2GF5O6VSN7S",
            aws_secret_access_key="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",
            region_name="ap-southeast-1"
    ):
        """
        Create boto connection object

        :return: Connection object
        """

        return boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def read_csv_from_s3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None
    ) -> DataFrame:
        """
        This function returns dataframe object of csv file stored in S3

        :param bucket_name: Name of the bucket where csv is stored
        :param object_name: Path of the object in S3
        :param resource: Connection object
        :return: dataframe object pandas
        """
        content_object = resource.Object(bucket_name, object_name)
        csv_string = content_object.get()['Body'].read().decode('utf - 8')
        df = read_csv(StringIO(csv_string))

        return df

    def write_csv_to_s3(
            self,
            bucket_name=None,
            object_name=None,
            df_to_upload=None,
            resource=None
    ) -> None:
        """
        Function to write csv in S3

        :param bucket_name: Name of the bucket where csv shall be stored
        :param object_name: Path of the object in S3
        :param df_to_upload: dataframe to be stored as csv
        :param resource: Connection object
        :return:
        """
        csv_buffer = StringIO()
        df_to_upload.to_csv(csv_buffer, index=False)
        content_object = resource.Object(bucket_name, object_name)
        content_object.put(Body=csv_buffer.getvalue())
        print('Successfully dumped data into s3')

    def read_compress_csv_from_s3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None
    ) -> DataFrame:
        """
        This function returns dataframe object of csv file stored in S3

        :param bucket_name: Name of the bucket where csv is stored
        :param object_name: Path of the object in S3
        :param resource: Connection object
        :return: dataframe object pandas
        """
        content_object = resource.Object(
            bucket_name,
            object_name
        )
        csv_string = content_object.get()['Body'].read()
        df = read_csv(BytesIO(csv_string), compression='gzip', header=0, sep=',', quotechar='"')

        return df


    def read_pkl_from_s3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None
    ):
        """
        Function to write pkl in S3
        :param bucket_name: Name of the bucket where pkl shall be stored
        :param object_name: Path of the object in S3
        :param resource: Connection object
        :return: pkl object
        """
        try:
            response = resource.Bucket(bucket_name).Object(object_name).get()
            body_string = response['Body'].read()
            loaded_pickle = pickle.loads(body_string)
            return loaded_pickle
        except:
            logging.error("Unable to find file {}. No such file exists".format(object_name))

    def write_pkl_to_s3(
            self,
            bucket_name=None,
            object_name=None,
            data=None,
            resource=None
    ) -> None:
        """
        Function to write pkl in S3

        :param bucket_name: Name of the bucket where pkl shall be stored
        :param object_name: Path of the object in S3
        :param data: file to be stored as pkl, like dataframe, dict, list
        :param resource: Connection object
        :return: None
        """
        try:
            pkl_obj = pickle.dumps(data)
            resource.Object(bucket_name, object_name).put(Body=pkl_obj)
            pkl_name = os.path.split(object_name)[1]
            logging.info("Successfully dumped " + pkl_name + " data into s3")
        except Exception as e:
            logging.error(f"Error while dumping {object_name} to S3, Exception: {e}")

    def upload_to_s3(
            self,
            bucket_name=None,
            file_with_path=None,
            key=None,
            resource=None
    ) -> None:
        """

        :param bucket_name: Name of the bucket where csv shall be stored
        :param key: the key name of file on s3
        :param file_name: filename with local path
        :param resource: Connection object
        :return: response
        """
        res = resource.Bucket(bucket_name).upload_file(Filename=file_with_path, Key=key, )
        logging.info(f'Successfully upload file {key} on s3')
        return res

    def download_from_s3(
            self,
            bucket_name=None,
            filename_with_path=None,
            key=None,
            resource=None
    ) -> None:
        """
        :param bucket_name: Name of the bucket where csv shall be stored
        :param key: the key name of file on s3
        :param filename_with_path: filename with local path
        :param resource: Connection object
        :return: response
        """
        try:
            res = resource.Bucket(bucket_name).download_file(
                Key=key,
                Filename=filename_with_path,
            )
            logging.info(f'Successfully download file {key} from s3 to {filename_with_path}')
            return res
        except Exception as e:
            logging.error(f"Error while downloading file , Error : {e}")

    def get_s3_keys(
            self,
            s3_client,
            bucket
    ) -> list:
        """Get a list of keys in an S3 bucket.
        :param s3_client: S3 client
        :param bucket: bucket name
        :return: list of all keys exist in s3
        """
        try:
            keys = []
            resp = s3_client.list_objects_v2(Bucket=bucket)
            for obj in resp['Contents']:
                keys.append(obj['Key'])
            return keys
        except Exception as e:
            logging.error(f"Error while listing keys , Error : {e}")

    def write_compress_pickles_to_S3(
            self,
            bucket_name=None,
            object_name=None,
            data=None,
            resource=None
    ) -> None:
        """Upload pickle as compressed file
           :param bucket_name: bucket name
           :param object_name:Where to upload
           :param data : local path of pickle file
           :param resource: Connection object
           :return:None
           """

        try:
            pkl_name = os.path.split(object_name)[1]
            logging.info("Start dumping " + pkl_name + " data into s3")
            d = read_pickle(data)

            with gzip.open(data, "wb") as f:
                pickle.dump(d, f)
            resource.meta.client.upload_file(data, bucket_name, object_name, )
            logging.info("Successfully dumped " + pkl_name + " data into s3")
        except Exception as e:
            logging.error(f"Error while dumping {object_name} to S3, Exception: {e}")

    def read_compress_pickles_from_S3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None,
    ) -> DataFrame:
        """Read pickle as compressed file
           :param bucket_name: bucket name
           :param object_name: S3 Path of Pickle file
           :param resource: Connection object
           :return:dataframe
           """
        try:
            content_object = resource.Object(bucket_name, object_name)
            read_file = content_object.get()['Body'].read()
            zipfile = BytesIO(read_file)
            with gzip.GzipFile(fileobj=zipfile) as gzipfile:
                content = gzipfile.read()

            loaded_pickle = pickle.loads(content)
            print("File {} has been read successfully".format(object_name))
            return loaded_pickle
        except Exception as e:
            logging.error(f"Error while dumping {object_name} to S3, Exception: {e}")

    def write_df_to_pkl_S3(
            self,
            bucket_name=None,
            object_name=None,
            data=None,
            resource=None
    ) -> None:
        """Upload csv  as compressed  pickle file
           :param bucket_name: bucket name
           :param object_name:Where to upload
           :param data : dataframe
           :param resource: Connection object
           :return:None
           """
        try:
            file_name = os.path.split(object_name)[1]
            logging.info("Start dumping " + file_name + " data into s3")
            pickle_buffer = BytesIO()
            data.to_pickle(pickle_buffer, compression='gzip')
            resource.Object(bucket_name, object_name).put(Body=pickle_buffer.getvalue())
            logging.info("Successfully dumped " + file_name + " data into s3")
        except Exception as e:
            logging.error(f"Error while dumping {object_name} to S3, Exception: {e}")
