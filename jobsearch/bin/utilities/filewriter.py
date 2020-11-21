""" basic utility thing """

from datetime import datetime
import os
import sys

def write_file(filename: str, content: str):
    """ writes out content to ./testdata/%Y-%m-%d/filename """
    path = f"./testdata/{datetime.today().strftime('%Y-%m-%d')}"
    full_filename = f"{path}/{filename}"
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as error_message:
        print(f"Failed to create path {path}: {error_message}", file=sys.stderr)
        return False

    try:
        with open(full_filename, 'w') as file_handle:
            file_handle.write(content)
    except IOError as ioerror:
        print(f"Unable to write to {full_filename}: {ioerror}", file=sys.stderr)
        return False
    except Exception as error_message:
        print(f"Failed to write to {full_filename}: {error_message}", file=sys.stderr)
        return False
    return True