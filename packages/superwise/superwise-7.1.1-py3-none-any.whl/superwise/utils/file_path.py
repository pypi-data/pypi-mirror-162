import os


def extract_file_extension(path: str) -> str:
    file_name, file_extension = os.path.splitext(path)
    return file_extension
