import datetime
import os
import subprocess
import timeit
from logging import Logger


class Dbms:
    """Base class for all Dbms instances"""

    def __init__(self, backup_path: str, filename_prefix: str, logger: Logger):
        self._backup_path = backup_path
        self._filename_prefix = filename_prefix
        self._logger = logger

        self._command_checked = False
        self._filepath = None

    def get_check_command(self) -> str:
        raise NotImplementedError

    def get_backup_command(self) -> str:
        raise NotImplementedError

    @property
    def filepath(self):
        return self._filepath

    def check_environment(self) -> bool:
        """Check if the environment is correctly configured and is able to generate a mysql backup"""

        check_command = self.get_check_command()

        self._logger.info("start checking the environment")
        self._logger.info("   executing command: %s", check_command)

        timer_start = timeit.default_timer()

        rv = subprocess.run(check_command,
                            text=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timer_stop = timeit.default_timer()
        elapsed_time = timer_stop - timer_start

        self._logger.info("completed the environment check")
        self._logger.info("   executed in: %f secs", elapsed_time)
        self._logger.info("   status code: %d", rv.returncode)
        self._logger.info("   stdout: (see following lines)\n%s", rv.stdout)

        self._command_checked = True

        return rv.returncode == 0

    def create_backup(self, host: str, user: str, password: str, db_name: str, extra_params: str = "") -> bool:
        """Create the backup"""

        if not self._command_checked and not self.check_environment():
            return False

        current_iso_datetime = (datetime.datetime.utcnow()
                                .replace(microsecond=0)
                                .isoformat()
                                .replace("-", "")
                                .replace(":", "")
                                .replace("T", ""))

        filename = f"{current_iso_datetime}Z.sql"
        if self._filename_prefix is not None and len(self._filename_prefix) > 0:
            filename = f"{self._filename_prefix}_{filename}"

        self._filepath = os.path.join(self._backup_path, filename)

        backup_command = (self.get_backup_command()
                          .replace("{{host}}", host)
                          .replace("{{db_name}}", db_name)
                          .replace("{{backup_filepath}}", self._filepath)
                          .replace("{{extra_params}}", extra_params))

        logged_command = (backup_command
                          .replace("{{user}}", "***")
                          .replace("{{password}}", "***"))
        backup_command = (backup_command
                          .replace("{{user}}", user)
                          .replace("{{password}}", password))

        self._logger.info("start creating the backup")
        self._logger.info("   executing command: %s", logged_command)

        timer_start = timeit.default_timer()

        rv = subprocess.run(backup_command,
                            text=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timer_stop = timeit.default_timer()
        elapsed_time = timer_stop - timer_start

        self._logger.info("completed the backup creation")
        self._logger.info("   executed in: %f secs", elapsed_time)
        self._logger.info("   status code: %d", rv.returncode)
        self._logger.info("   stdout: (see following lines)\n%s", rv.stdout)

        return rv.returncode == 0
