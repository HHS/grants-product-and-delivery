import pandas as pd
import requests
import os
from urllib.parse import urlparse
from typing import List


def download_xml_schema(url: str, output_dir: str) -> str:
    """
    Download an XML schema from a URL and save it to the specified directory.

    Args:
        url (str): URL of the XML schema
        output_dir (str): Directory to save the XML file

    Returns:
        str: Path to the downloaded file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Ensure filename ends with .xml
        if not filename.endswith(".xml"):
            filename += ".xml"

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


def download_all_schemas(metadata_path: str, output_dir: str) -> List[str]:
    """
    Download all XML schemas from the FormSchema column in FormMetadata.csv.

    Args:
        metadata_path (str): Path to FormMetadata.csv
        output_dir (str): Directory to save XML files

    Returns:
        List[str]: List of paths to downloaded files
    """
    # Read the metadata file
    df = pd.read_csv(metadata_path)

    # Get unique schema URLs
    schema_urls = df["Form Schema"].dropna().unique()

    # Download each schema
    downloaded_files = []
    for url in schema_urls:
        file_path = download_xml_schema(url, output_dir)
        if file_path:
            downloaded_files.append(file_path)
            print(f"Downloaded: {file_path}")

    return downloaded_files


if __name__ == "__main__":
    download_all_schemas("./FormMetadata.csv", "./tmp/schemas")
