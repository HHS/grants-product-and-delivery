"""Loads exported DAT and XML files fetched from Grants.gov."""

import logging
from pathlib import Path
from typing import Callable
import pandas as pd


def standardize_col_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Casts column names to snake_case and strips whitespace.
    """
    df.columns = df.columns.str.lower().str.strip()
    df.columns = df.columns.str.replace(r"\s+", "_", regex=True)
    return df


def add_form_metadata(
    df: pd.DataFrame,
    metadata_path: str,
    link_column: str,
) -> pd.DataFrame:
    """
    Add form metadata to the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to enrich
        metadata_path (str): Path to the metadata CSV file
        link_column (str): Column name to use for merging with metadata

    Returns:
        pd.DataFrame: DataFrame with form metadata added
    """
    # Read the metadata CSV file
    metadata_cols = {
        "Form Schema": "form_schema_url",
        "Form DAT": "form_dat_url",
        "Form Family": "form_family",
        "Form Name": "form_name",
        "OMB Number": "form_omb_number",
        "Agency Owner": "form_agency_owner",
    }

    # Format metadata
    metadata_df = pd.read_csv(metadata_path)
    metadata_df = metadata_df[metadata_cols.keys()]
    metadata_df.rename(columns=metadata_cols, inplace=True)

    # Drop duplicates based on the specific link column we're using
    metadata_df.drop_duplicates(subset=[link_column], inplace=True)

    # Merge metadata with data
    merged_df = pd.merge(
        df,
        metadata_df,
        left_on="form_link",
        right_on=link_column,
        how="left",
    )

    return merged_df


def process_all_files(
    file_dir: str,
    file_type: str,
    metadata_path: str,
    output_path: str,
    process_func: Callable,
) -> None:
    """
    Process all files in a directory, enrich with metadata, and save the result.

    Args:
        file_dir (str): Directory containing files
        file_type (str): Type of files to process ("dat" or "xml")
        metadata_path (str): Path to FormMetadata.csv
        output_path (str): Path to save the output CSV
        process_func (callable): Function to process individual files
    """
    # Get all files in the directory
    if file_type == "dat":
        files = list(Path(file_dir).glob("*.xls"))
    else:  # xml
        files = list(Path(file_dir).glob("*.xml"))

    if not files:
        logging.warning(f"No {file_type} files found in {file_dir}")
        return

    # Process each file
    dfs = []
    for file_path in files:
        logging.info(f"Processing {file_path}")
        df = process_func(str(file_path))
        if not df.empty:
            dfs.append(df)

    # Combine all DataFrames
    if not dfs:
        logging.warning(f"No {file_type} files were successfully processed")
        return

    combined_df = pd.concat(dfs, ignore_index=True)

    # Enrich with metadata
    combined_df = add_form_metadata(
        combined_df,
        metadata_path,
        link_column="form_schema_url",
    )

    # Save to CSV
    combined_df.to_csv(output_path, index=False)
    logging.info(f"Saved processed data to {output_path}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
