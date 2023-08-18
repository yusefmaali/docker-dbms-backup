import os


class Configuration:
    backup_folder: str = "/tmp"

    def __init__(self):
        self.filename_prefix = None
        self.file_rotation_count = 0

        self.compress = None

        self.mysql_host = None
        self.mysql_user = None
        self.mysql_password = None
        self.mysql_db_name = None
        self.mysql_extra_params = None

        self.postgres_host = None
        self.postgres_user = None
        self.postgres_password = None
        self.postgres_db_name = None
        self.postgres_extra_params = None

        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.aws_s3_bucket_name = None

    @property
    def is_mysql_enabled(self) -> bool:
        return (self.mysql_host is not None and
                self.mysql_user is not None and
                self.mysql_password is not None and
                self.mysql_db_name is not None)

    @property
    def is_postgres_enabled(self) -> bool:
        return (self.postgres_host is not None and
                self.postgres_user is not None and
                self.postgres_password is not None and
                self.postgres_db_name is not None)

    @property
    def is_compress_enabled(self):
        return self.compress in ["gzip", "bzip2"]

    @property
    def is_file_rotation_enabled(self):
        return (self.file_rotation_count is not None and
                self.file_rotation_count > 0)

    @property
    def is_aws_enabled(self):
        return (self.aws_access_key_id is not None and
                self.aws_secret_access_key is not None and
                self.aws_s3_bucket_name is not None)

    def load_from_environment(self):
        self.filename_prefix = os.environ.get('BACKUP_FILENAME_PREFIX') or ""
        self.file_rotation_count = int(os.environ.get('BACKUP_FILE_ROTATION_COUNT')) or 0

        self.compress = os.environ.get('COMPRESS')

        self.mysql_host = os.environ.get('MYSQL_HOST')
        self.mysql_user = os.environ.get('MYSQL_USER')
        self.mysql_password = os.environ.get('MYSQL_PASSWORD')
        self.mysql_db_name = os.environ.get('MYSQL_DATABASE_NAME')
        self.mysql_extra_params = os.environ.get('MYSQL_EXTRA_DUMP_PARAMS') or ""

        self.postgres_host = os.environ.get('POSTGRES_HOST')
        self.postgres_user = os.environ.get('POSTGRES_USER')
        self.postgres_password = os.environ.get('POSTGRES_PASSWORD')
        self.postgres_db_name = os.environ.get('POSTGRES_DATABASE_NAME')
        self.postgres_extra_params = os.environ.get('POSTGRES_EXTRA_DUMP_PARAMS') or ""

        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_s3_bucket_name = os.environ.get('AWS_S3_BUCKET_NAME')
