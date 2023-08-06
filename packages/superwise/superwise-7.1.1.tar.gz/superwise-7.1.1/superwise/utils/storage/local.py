import os

from superwise.utils.storage import validate_file_size


def load_from_local_storage(file_path: str, validate_size: bool = False) -> tuple:
    if validate_size:
        file_size = os.path.getsize(file_path)

        validate_file_size(file_path=file_path, file_size=file_size)

    with open(file_path, "rb") as file:
        data = file.read()

    filename = file_path.split("/")[-1]

    return filename, data
