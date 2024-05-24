from loguru import logger as log1


def log(message):
    with open('data/logs.txt', 'a') as f:
        f.write(f"{message}\n")


log1.add('data/file.log', rotation="500 MB", level="INFO")
