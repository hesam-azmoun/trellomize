from loguru import logger as log1

log1.add('data/file.log', rotation="500 MB", level="INFO")
