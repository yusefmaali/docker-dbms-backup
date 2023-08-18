import logging

from dbms.dbms import Dbms


class PostgresDbms(Dbms):
    """Postgres Dbms instance"""

    CHECK_COMMAND: str = "pg_dump --version"
    BACKUP_COMMAND: str = ("PGPASSWORD='{{password}}' pg_dump "
                           "--host={{host}} --username={{user}} "
                           "--dbname='{{db_name}}' --file={{backup_filepath}} "
                           "{{extra_params}}")

    def __init__(self, backup_path: str, filename_prefix: str):
        super().__init__(backup_path, filename_prefix, logging.getLogger("postgres_dbms"))

    def get_check_command(self) -> str:
        return self.CHECK_COMMAND

    def get_backup_command(self) -> str:
        return self.BACKUP_COMMAND
