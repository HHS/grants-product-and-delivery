import logging
import os
from pathlib import Path
import pandas as pd


def standardize_col_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Casts column names to PascalCase and strips whitespace.
    """
    df.columns = df.columns.str.lower().str.strip()
    df.columns = df.columns.str.replace(r"\s+", "_", regex=True)
    return df


def process_dat_file(file_path: str) -> pd.DataFrame:
    """
    Process a single DAT file (Excel) and return a standardized DataFrame.

    Args:
        file_path (str): Path to the DAT file

    Returns:
        pd.DataFrame: Processed DataFrame with standardized columns
    """
    try:
        # Read the Excel file, skipping the first two rows (header and separator)
        df = pd.read_excel(file_path, sheet_name=1, skiprows=2)

        # Add source file information
        df["source_file"] = os.path.basename(file_path)

        # Standardize column names
        df = standardize_col_names(df)

        # Add form link
        base_url = "https://apply07.grants.gov/apply/forms/sample/"
        df["form_link"] = base_url + df["source_file"]

        return df

    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return pd.DataFrame()


def process_all_dat_files(dat_dir: str) -> pd.DataFrame:
    """
    Process all DAT files in the specified directory and combine them into a single DataFrame.

    Args:
        dat_dir (str): Directory containing DAT files

    Returns:
        pd.DataFrame: Combined DataFrame with all processed data
    """
    # Get all Excel files in the directory
    dat_files = list(Path(dat_dir).glob("*.xls"))

    if not dat_files:
        logging.warning(f"No DAT files found in {dat_dir}")
        return pd.DataFrame()

    # Process each file
    dfs = []
    for file_path in dat_files:
        logging.info(f"Processing {file_path}")
        df = process_dat_file(str(file_path))
        if not df.empty:
            dfs.append(df)

    # Combine all DataFrames
    if not dfs:
        logging.warning("No DAT files were successfully processed")
        return pd.DataFrame()

    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def add_form_metadata(df: pd.DataFrame, metadata_path: str) -> pd.DataFrame:
    """
    Add form metadata to the parsed schema DataFrame.

    Args:
        df (pd.DataFrame): Parsed schema DataFrame
        metadata_path (str): Path to the metadata CSV file

    Returns:
        pd.DataFrame: DataFrame with form metadata added
    """
    # Read the metadata CSV file
    metadata_cols = {
        "Form DAT": "form_link",
        "Form Family": "form_family",
        "Form Name": "form_name",
        "OMB Number": "form_omb_number",
        "Agency Owner": "form_agency_owner",
    }
    metadata_df = pd.read_csv(metadata_path)
    metadata_df = metadata_df[metadata_cols.keys()]
    metadata_df.rename(columns=metadata_cols, inplace=True)
    metadata_df.drop_duplicates(subset=["form_link"], inplace=True)
    merged_df = pd.merge(df, metadata_df, on="form_link", how="left")

    return merged_df


def process_and_save_dat_files(
    dat_dir: str, metadata_path: str, output_path: str
) -> None:
    """
    Process all DAT files, enrich with metadata, and save the result.

    Args:
        dat_dir (str): Directory containing DAT files
        metadata_path (str): Path to FormMetadata.csv
        output_path (str): Path to save the output CSV
    """
    # Process all DAT files
    df = process_all_dat_files(dat_dir)

    if df.empty:
        logging.error("No data was processed")
        return

    # Enrich with metadata
    df = add_form_metadata(df, metadata_path)

    # Save to CSV
    df.to_csv(output_path, index=False)
    logging.info(f"Saved processed data to {output_path}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Process and save DAT files
    process_and_save_dat_files(
        dat_dir="./tmp/dat",
        metadata_path="./FormMetadata.csv",
        output_path="./tmp/processed_dat_files.csv",
    )
