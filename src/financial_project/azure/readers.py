# Treat text as a file-like object in memory.
from io import StringIO
import pandas as pd

def read_file_azure(
    filesystem,
    file_path,
    encoding="latin1",
    sep="\t",
    decimal=",",
):
    """
    Download a delimited text file from Azure and return a DataFrame.

    Parameters:
        filesystem: Azure filesystem client.
        file_path: Path of the file inside the filesystem.
        encoding: Text encoding used to decode the file.
        sep: Delimiter separating columns.
        decimal: Character used as the decimal separator.

    Returns:
        pandas.DataFrame: The contents of the file.
    """

    # Create a client for the requested file.
    file_client = filesystem.get_file_client(file_path)

    # Start downloading the file from Azure.
    download = file_client.download_file()

    # Read all bytes and decode them into text.
    content = download.readall().decode(encoding)

    # Wrap the text in an in-memory file-like object.
    text_file = StringIO(content)

    # Parse the delimited text and create a DataFrame.
    data = pd.read_csv(
        text_file,
        sep=sep,
        decimal=decimal,
        low_memory=False,
    )

    return data