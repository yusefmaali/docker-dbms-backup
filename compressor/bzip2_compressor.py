import logging

from compressor.compressor import Compressor


class BZip2Compressor(Compressor):
    """Bzip2 compressor instance"""

    CHECK_COMMAND: str = "bzip2 --help"
    COMPRESS_COMMAND: str = "bzip2 {{source_filepath}}"

    def __init__(self):
        super().__init__(logging.getLogger("bzip2_compressor"))

    def get_check_command(self) -> str:
        return self.CHECK_COMMAND

    def get_compress_command(self) -> str:
        return self.COMPRESS_COMMAND

    @property
    def filepath(self):
        return f"{self._filepath}.bz2"
