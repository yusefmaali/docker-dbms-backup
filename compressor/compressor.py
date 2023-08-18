import subprocess
import timeit
from logging import Logger


class Compressor:
    """Base class for all Compressor instances"""

    def __init__(self, logger: Logger):
        self._logger = logger

        self._command_checked = False
        self._filepath = None

    def get_check_command(self) -> str:
        raise NotImplementedError

    def get_compress_command(self) -> str:
        raise NotImplementedError

    @property
    def filepath(self):
        raise NotImplementedError

    def check_environment(self) -> bool:
        """Check if the environment is correctly configured and is able to compress the file"""

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

    def compress_file(self, source_filepath: str, destination_filepath: str = "", extra_params: str = "") -> bool:
        """Compress the file"""

        if not self._command_checked and not self.check_environment():
            return False

        self._filepath = source_filepath

        compress_command = (self.get_compress_command()
                            .replace("{{source_filepath}}", source_filepath)
                            .replace("{{dest_filepath}}", destination_filepath)
                            .replace("{{extra_params}}", extra_params))

        self._logger.info("start compressing the backup")
        self._logger.info("   executing command: %s", compress_command)

        timer_start = timeit.default_timer()

        rv = subprocess.run(compress_command,
                            text=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timer_stop = timeit.default_timer()
        elapsed_time = timer_stop - timer_start

        self._logger.info("completed the compression")
        self._logger.info("   executed in: %f secs", elapsed_time)
        self._logger.info("   status code: %d", rv.returncode)
        self._logger.info("   stdout: (see following lines)\n%s", rv.stdout)

        return rv.returncode == 0
