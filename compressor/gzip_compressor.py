import logging

from compressor.compressor import Compressor


class GzipCompressor(Compressor):
    """Gzip compressor instance"""

    CHECK_COMMAND: str = "gzip --help"
    COMPRESS_COMMAND: str = "gzip {{source_filepath}}"

    def __init__(self):
        super().__init__(logging.getLogger("gzip_compressor"))

    def get_check_command(self) -> str:
        return self.CHECK_COMMAND

    def get_compress_command(self) -> str:
        return self.COMPRESS_COMMAND

    @property
    def filepath(self):
        return f"{self._filepath}.gz"
