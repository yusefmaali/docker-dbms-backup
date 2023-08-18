import logging

from dbms.dbms import Dbms


class MysqlDbms(Dbms):
    """Mysql Dbms instance"""

    CHECK_COMMAND: str = "mysqldump --version"
    BACKUP_COMMAND: str = ("mysqldump "
                           "--host={{host}} --user={{user}} --password={{password}} "
                           "--lock-tables --default-character-set=utf8 --skip-triggers "
                           "--databases '{{db_name}}' {{extra_params}} > {{backup_filepath}}")

    def __init__(self, backup_path: str, filename_prefix: str):
        super().__init__(backup_path, filename_prefix, logging.getLogger("mysql_dbms"))

    def get_check_command(self) -> str:
        return self.CHECK_COMMAND

    def get_backup_command(self) -> str:
        return self.BACKUP_COMMAND
