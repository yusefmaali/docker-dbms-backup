import logging
import os
import sys
import timeit

from dotenv import load_dotenv

from aws.aws_s3_client import AwsS3Client
from compressor.bzip2_compressor import BZip2Compressor
from compressor.gzip_compressor import GzipCompressor
from configuration import Configuration
from dbms.dbms import Dbms
from dbms.mysql_dbms import MysqlDbms
from dbms.postgres_dbms import PostgresDbms

EXIT_DBMS_INSTANCE: int = 2
EXIT_CREATE_BACKUP: int = 3
EXIT_COMPRESS_BACKUP: int = 4
EXIT_UPLOAD_BACKUP: int = 5
EXIT_AWS_S3_CLIENT: int = 6

config = Configuration()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("docker_container_scheduler")


def create_dbms_instance() -> Dbms | None:
    if config.is_mysql_enabled:
        logger.info("Found a mysql configuration")
        return MysqlDbms(config.backup_folder, config.filename_prefix)
    elif config.is_postgres_enabled:
        logger.info("Found a postgres configuration")
        return PostgresDbms(config.backup_folder, config.filename_prefix)

    return None


def create_backup(dbms: Dbms) -> bool:
    if config.is_mysql_enabled:
        return dbms.create_backup(host=config.mysql_host,
                                  user=config.mysql_user, password=config.mysql_password,
                                  db_name=config.mysql_db_name, extra_params=config.mysql_extra_params)

    elif config.is_postgres_enabled:
        return dbms.create_backup(host=config.postgres_host,
                                  user=config.postgres_user, password=config.postgres_password,
                                  db_name=config.postgres_db_name, extra_params=config.postgres_extra_params)

    return False


def compress_backup(filepath: str) -> str | None:
    if not config.is_compress_enabled:
        return filepath

    if config.compress == "gzip":
        compressor = GzipCompressor()
        if not compressor.compress_file(filepath):
            return None
        return compressor.filepath

    elif config.compress == "bzip2":
        compressor = BZip2Compressor()
        if not compressor.compress_file(filepath):
            return None
        return compressor.filepath

    return None


def upload_file(filepath: str) -> bool:
    if config.is_aws_enabled:
        try:
            client = AwsS3Client(
                access_key=config.aws_access_key_id,
                secret_key=config.aws_secret_access_key,
                s3_bucket_name=config.aws_s3_bucket_name)

            if config.is_file_rotation_enabled:
                completed = client.rotate_files(max_file_count=config.file_rotation_count)
                if not completed:
                    return False

            return client.upload_file(filepath=filepath)
        except Exception as e:
            logger.error("AwsS3Client raised an exception. Exiting", exc_info=e)
            exit(EXIT_AWS_S3_CLIENT)

    # uploading may be not configured, leaving the backup file in the local storage
    return True


if __name__ == '__main__':
    timer_start = timeit.default_timer()

    load_dotenv()
    config.load_from_environment()

    dbms_instance = create_dbms_instance()
    if dbms_instance is None:
        logger.error("cannot create the dbms instance. Exiting")
        exit(EXIT_DBMS_INSTANCE)

    if not create_backup(dbms_instance):
        logger.error("cannot create the backup. Exiting")
        exit(EXIT_CREATE_BACKUP)

    backup_file = compress_backup(dbms_instance.filepath)
    if backup_file is None:
        logger.error("cannot compress the backup file. Exiting")
        exit(EXIT_COMPRESS_BACKUP)

    if not upload_file(backup_file):
        logger.error("cannot upload the backup file. Exiting")
        exit(EXIT_UPLOAD_BACKUP)

    timer_stop = timeit.default_timer()
    elapsed_time = timer_stop - timer_start

    try:
        os.remove(backup_file)
    except Exception as e:
        logger.error("cannot remove temporary backup file", exc_info=e)

    logger.info("operations completed in %f secs", elapsed_time)
