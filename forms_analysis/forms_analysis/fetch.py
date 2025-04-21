import pandas as pd
import requests
import os
from urllib.parse import urlparse
from typing import List, Optional


def download_file(
    url: str,
    output_dir: str,
    file_extension: Optional[str] = None,
) -> Optional[str]:
    """
    Download a file from a URL and save it to the specified directory.

    Args:
        url (str): URL of the file to download
        output_dir (str): Directory to save the file
        file_extension (Optional[str]): Optional file extension to ensure the file has

    Returns:
        Optional[str]: Path to the downloaded file, or None if download failed
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Add file extension if specified and not already present
        if file_extension and not filename.endswith(file_extension):
            filename += file_extension

        # Full path to save file
        output_path = os.path.join(output_dir, filename)

        # Download the file
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the file
        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None


def download_files_from_metadata(
    metadata_path: str,
    column_name: str,
    output_dir: str,
    file_extension: Optional[str] = None,
) -> List[str]:
    """
    Download files from URLs specified in a column of the metadata CSV.

    Args:
        metadata_path (str): Path to the metadata CSV file
        column_name (str): Name of the column containing URLs
        output_dir (str): Directory to save downloaded files
        file_extension (Optional[str]): Optional file extension to ensure files have

    Returns:
        List[str]: List of paths to downloaded files
    """
    # Read the metadata file
    df = pd.read_csv(metadata_path)

    # Get unique URLs from the specified column
    urls = df[column_name].dropna().unique()

    # Download each file
    downloaded_files = []
    for url in urls:
        file_path = download_file(url, output_dir, file_extension)
        if file_path:
            downloaded_files.append(file_path)
            print(f"Downloaded {column_name}: {file_path}")

    return downloaded_files


if __name__ == "__main__":

    # Or download specific types of files:
    # download_files_from_metadata(
    #     metadata_path="./FormMetadata.csv",
    #     column_name="Form Schema",
    #     output_dir="./tmp/schemas",
    #     file_extension=".xml",
    # )
    download_files_from_metadata(
        metadata_path="./FormMetadata.csv",
        column_name="Form DAT",
        output_dir="./tmp/dat",
    )
