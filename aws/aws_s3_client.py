import logging
import os
import timeit

import boto3


class AwsS3Client:
    def __init__(self, access_key: str, secret_key: str, s3_bucket_name: str):
        self._aws_access_key_id = access_key
        self._aws_secret_access_key = secret_key
        self._aws_s3_bucket_name = s3_bucket_name

        self._aws_session = None
        self._aws_s3_resource = None
        self._aws_s3_bucket = None

        self._logger = logging.getLogger("aws_s3_client")

    def __aws_init(self) -> bool:
        if not self.__create_aws_session():
            return False
        if not self.__create_bucket_reference():
            return False
        return True

    def __create_aws_session(self) -> bool:
        if self._aws_session is not None:
            return True

        self._aws_session = boto3.Session(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key)

        return True

    def __create_bucket_reference(self) -> bool:
        if (self._aws_s3_resource is not None and
                self._aws_s3_bucket is not None):
            return True

        self._logger.info("start looking for '%s' bucket", self._aws_s3_bucket_name)

        self._aws_s3_resource = self._aws_session.resource('s3')
        buckets = self._aws_s3_resource.buckets.all()

        bucket_found = False
        for bucket in buckets:
            if bucket.name == self._aws_s3_bucket_name:
                bucket_found = True
                break

        if not bucket_found:
            self._logger.error("the bucket name '%s' is invalid or the bucket doesn't exists",
                               self._aws_s3_bucket_name)
            return False

        self._logger.info("the bucket is there")

        self._aws_s3_bucket = self._aws_s3_resource.Bucket(self._aws_s3_bucket_name)

        return True

    def rotate_files(self, max_file_count: int) -> bool:
        if not self.__aws_init():
            return False

        self._logger.info("start rotating files")

        timer_start = timeit.default_timer()

        bucket_files = self._aws_s3_bucket.objects.all()
        file_keys = [file.key for file in bucket_files]

        file_count = len(file_keys)
        if file_count < max_file_count:
            self._logger.info("no need to rotate files, not enough files in the storage")
            return True

        sorted_file_keys_by_date = [file.key for file in sorted(bucket_files, key=lambda x: x.last_modified)]

        deleted_keys = []
        for i in range(0, file_count-(max_file_count-1)):
            key_to_delete = sorted_file_keys_by_date[i]
            deleted_keys.append(key_to_delete)

            self._logger.info("   deleting file '%s'", key_to_delete)

            obj = self._aws_s3_resource.Object(self._aws_s3_bucket_name, key_to_delete)
            obj.delete()

        # fetch again the file list to check the deletion
        bucket_files = self._aws_s3_bucket.objects.all()

        files_deleted = True
        for file in bucket_files:
            if file.key in deleted_keys:
                files_deleted = False
                break

        timer_stop = timeit.default_timer()
        elapsed_time = timer_stop - timer_start

        self._logger.info("completed files rotation in %f secs", elapsed_time)

        return files_deleted

    def upload_file(self, filepath: str) -> bool:
        if not self.__aws_init():
            return False

        timer_start = timeit.default_timer()
        filename = os.path.basename(filepath)

        self._logger.info("start uploading file '%s'", filename)

        self._aws_s3_bucket.upload_file(filepath, filename)

        timer_stop = timeit.default_timer()
        elapsed_time = timer_stop - timer_start

        self._logger.info("completed file upload in %f secs", elapsed_time)

        return True
