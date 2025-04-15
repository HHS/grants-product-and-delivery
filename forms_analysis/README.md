# Grants.gov Forms Analysis

This directory contains a script to analyze the forms listed in the [Grants.gov forms repository](https://www.grants.gov/forms/forms-repository/).

## Usage

### Pre-requisites

- The repo is cloned locally
- Python 3.11 or greater is installed: `python3 --version`
- [Poetry](https://python-poetry.org/docs/#installation) is installed: `poetry --version`

### Running the script

Run the following commands from the root of the `forms_analysis` directory.

1. Install dependencies: `poetry install`
2. Fetch the XML schemas from Grants.gov: `poetry run python forms_analysis/fetch.py`
3. Parse the XML schemas into a CSV file: `poetry run python forms_analysis/parse.py`

### Output

The script will output a CSV file with the following columns.

| Column            | Description                               | Example                                                                |
| ----------------- | ----------------------------------------- | ---------------------------------------------------------------------- |
| name              | The name of the element                   | `"AgencyName"`                                                         |
| path              | The path to the element                   | `"SF3881_2_0.AgencyName"`                                              |
| type_source       | Namespace prefix of the type              | `"globLib"`                                                            |
| type              | The type of the element                   | `"AgencyNameDataType"`                                                 |
| required          | Whether the element is required           | `"True"`                                                               |
| min_occurrences   | Minimum number of occurrences             | `"1"`                                                                  |
| max_occurrences   | Maximum number of occurrences             | `"1"`                                                                  |
| description       | Description of the element                | `""`                                                                   |
| order             | The order in which the element appears    | `"1"`                                                                  |
| depth             | How many levels deep the element is       | `"1"`                                                                  |
| source_file       | The XML file it came from                 | `"SF3881_2_0-V2.0.xsd.xml"`                                            |
| form_name_xml     | The form name extracted from the filename | `"SF3881_2_0"`                                                         |
| form_link         | The URL to the schema on grants.gov       | `"https://apply07.grants.gov/apply/forms/schemas/SF3881_2_0-V2.0.xsd"` |
| form_family       | The form family                           | `"SF-424 Family"`                                                      |
| form_name         | The full form name                        | `"ACH Vendor/Miscellaneous Payment Enrollment Form"`                   |
| form_omb_number   | The OMB number for the form               | `"1530-0069"`                                                          |
| form_agency_owner | The agency that owns the form             | `"TREAS"`                                                              |
