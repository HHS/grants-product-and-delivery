import pandas as pd


def join_csvs(
    dat_path: str,
    xml_path: str,
    output_path: str = "tmp/joined_data.csv",
) -> pd.DataFrame:
    # Read the CSV files
    dat_df = pd.read_csv(dat_path)
    xml_df = pd.read_csv(xml_path)

    dat_df = dat_df.drop_duplicates(subset=["agency_field_name", "form_name"])

    # Select the columns we want from the DAT file
    dat_columns = [
        "field_#",
        "field_label",
        "field_id",
        "business_rules",
        "data_type",
        "list_of_values",
        "min_#_of_chars_or_min_value",
        "max_#_of_chars_or_max_value",
        "field_implementation",
        "help_tip",
        "mandatory_message",
        "validation_message",
        "short_field_label",
        "invalid_message",
        "agency_field_name",
        "form_name",
    ]

    # Filter the DAT dataframe to only include the columns we want
    dat_df = dat_df[dat_columns]

    # Merge the dataframes
    # First merge on agency_field_name == name and form_name == form_name
    merged_df = pd.merge(
        xml_df,
        dat_df,
        left_on=["name", "form_name"],
        right_on=["agency_field_name", "form_name"],
        how="left",
    )

    # Save the result to a new CSV file
    merged_df.to_csv(output_path, index=False)

    print(f"Merged data has been saved to '{output_path}'")
    print(f"Number of rows in merged data: {len(merged_df)}")

    return merged_df


if __name__ == "__main__":
    dat_path = "tmp/processed_dat_files.csv"
    xml_path = "tmp/parsed_form_schemas.csv"
    join_csvs(dat_path, xml_path, output_path="tmp/form_fields_joined.csv")
