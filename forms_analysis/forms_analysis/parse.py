import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path

# XML Schema namespace
XSD_NAMESPACE = "{http://www.w3.org/2001/XMLSchema}"


def process_element(
    element: ET.Element,
    columns: list,
    order_counter: int,
    current_path: str = "",
    depth: int = 0,
) -> int:
    """
    Recursively process XML elements and their children, collecting information about each element.

    Args:
        element (ET.Element): The XML element to process
        columns (list): List to store column information
        order_counter (int): Counter for element order
        current_path (str): Current path in dot notation
        depth (int): Current depth in the element hierarchy

    Returns:
        int: Updated order counter
    """
    # Skip elements without a name attribute
    if element.get("name") is None:
        return order_counter

    # Build the current path
    element_name = element.get("name")
    full_path = f"{current_path}.{element_name}" if current_path else element_name

    # Get element information
    column_info = {
        "name": element_name,
        "path": full_path,
        "type_source": "",
        "type": "",
        "required": element.get("minOccurs", "1") != "0",
        "min_occurrences": element.get("minOccurs", "1"),
        "max_occurrences": element.get("maxOccurs", "1"),
        "description": "",
        "order": order_counter,
        "depth": depth,
    }

    # Handle type information
    type_value = element.get("type", "")
    if type_value:
        # Split on colon to separate prefix and type name
        parts = type_value.split(":")
        if len(parts) == 2:
            column_info["type_source"] = parts[0]
            column_info["type"] = parts[1]
        else:
            column_info["type"] = type_value
    else:
        # Check for simpleType with restriction
        simple_type = element.find(f"./{XSD_NAMESPACE}simpleType")
        if simple_type is not None:
            restriction = simple_type.find(f"./{XSD_NAMESPACE}restriction")
            if restriction is not None:
                base_type = restriction.get("base", "")
                if base_type:
                    parts = base_type.split(":")
                    if len(parts) == 2:
                        column_info["type_source"] = parts[0]
                        column_info["type"] = "restriction"
                    else:
                        column_info["type"] = "restriction"

    # Increment order counter
    order_counter += 1

    # Get description from annotation if available
    annotation = element.find(f".//{XSD_NAMESPACE}annotation")
    if annotation is not None:
        documentation = annotation.find(f".//{XSD_NAMESPACE}documentation")
        if documentation is not None:
            column_info["description"] = documentation.text.strip()

    columns.append(column_info)

    # Find the complexType if it exists
    complex_type = element.find(f"./{XSD_NAMESPACE}complexType")
    if complex_type is not None:
        # Find direct child elements within the sequence
        sequence = complex_type.find(f"./{XSD_NAMESPACE}sequence")
        if sequence is not None:
            # If this element has a complexType with a sequence containing elements,
            # it's a section
            if sequence.findall(f"./{XSD_NAMESPACE}element"):
                column_info["type"] = "FieldSet"

            for child in sequence.findall(f"./{XSD_NAMESPACE}element"):
                order_counter = process_element(
                    child, columns, order_counter, full_path, depth + 1
                )

    return order_counter


def parse_schema(xml_path: str) -> pd.DataFrame:
    """
    Parse an XML schema and extract all elements under the root element.

    Args:
        xml_path (str): Path to the XML schema file

    Returns:
        pd.DataFrame: DataFrame containing column information with columns:
            - name: Element name
            - path: Full path to the element using dot notation
            - type: Data type (without namespace prefix)
            - type_source: Namespace prefix of the type (e.g., 'xs', 'globLib')
            - required: Whether the element is required
            - min_occurrences: Minimum number of occurrences
            - max_occurrences: Maximum number of occurrences
            - description: Description of the element
            - order: The order in which the element appears in the schema
            - depth: How many levels deep the element is in the hierarchy (0 for root)
    """
    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find the root element (first element with a name attribute)
    root_element = root.find(f".//{XSD_NAMESPACE}element[@name]")
    if root_element is None:
        raise ValueError("No root element found in schema")

    # Initialize list to store column information
    columns = []
    order_counter = 0

    # Start processing from the root element
    process_element(root_element, columns, order_counter)

    # Create DataFrame
    df = pd.DataFrame(columns)

    # Sort by order to preserve original sequence
    df = df.sort_values("order")

    return df


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
        "Form Schema": "form_link",
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


def parse_all_schemas(schemas_dir: str, metadata_path: str) -> pd.DataFrame:
    """
    Parse all XML schemas in a directory and combine them into a single DataFrame.

    Args:
        schemas_dir (str): Path to directory containing XML schema files

    Returns:
        pd.DataFrame: Combined DataFrame with all schema elements, including:
            - source_file: The XML file it came from
            - form_name: The form name extracted from the filename
            - form_link: The URL to the schema on grants.gov
    """
    # Get all XML files in the directory
    schema_files = list(Path(schemas_dir).glob("*.xml"))

    if not schema_files:
        raise ValueError(f"No XML files found in {schemas_dir}")

    # Initialize list to store all DataFrames
    all_dfs = []

    # Process each schema file
    for schema_file in schema_files:
        try:
            # Parse the schema
            df = parse_schema(str(schema_file))

            # Add source file information
            df["source_file"] = schema_file.name

            # Add form name (extracted from filename)
            form_name = schema_file.name.split("-")[0]
            df["form_name_xml"] = form_name

            # Add form link
            base_url = "https://apply07.grants.gov/apply/forms/schemas/"
            schema_name = schema_file.name.replace(".xml", "")
            df["form_link"] = base_url + schema_name

            all_dfs.append(df)

        except Exception as e:
            print(f"Error processing {schema_file.name}: {str(e)}")

    # Combine all DataFrames
    if not all_dfs:
        raise ValueError("No schemas were successfully parsed")

    # Combine all DataFrames, add form metadata, and sort by form name and order
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df = add_form_metadata(combined_df, metadata_path)
    combined_df = combined_df.sort_values(["form_name", "order"])

    return combined_df


if __name__ == "__main__":
    print("Parsing schemas and saving to ./tmp/parsed_form_schemas.csv")
    df = parse_all_schemas("./tmp/schemas", "./FormMetadata.csv")
    df.to_csv("./tmp/parsed_form_schemas.csv", index=False)
    print("Summary of parsed schemas:")
    print(df.info())
