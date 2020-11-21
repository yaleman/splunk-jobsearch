""" basic utility thing """

from datetime import datetime
import os
import sys
from tempfile import NamedTemporaryFile

def write_file(content: str):
    """ writes out content to ./testdata/%Y-%m-%d/filename 
    
        this is ONLY ever used in testing during development 
        or if someone specifically modifies the input
    """
    
    file_handle = NamedTemporaryFile(prefix=f"splunk-jobsearch-urlcontent-", suffix='.txt', delete=False)
    try:
        file_handle.write(content.encode('utf-8'))
        print(f"Writing to {file_handle.name}")
    except IOError as ioerror:
        print(f"Unable to write to {file_handle.name}: {ioerror}", file=sys.stderr)
        return False
    except Exception as error_message:
        print(f"Failed to write to {file_handle.name}: {error_message}", file=sys.stderr)
        return False
    return True