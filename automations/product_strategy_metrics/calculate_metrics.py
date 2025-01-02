import re
import json
import argparse
from dataclasses import dataclass


@dataclass
class SectionAnalysis:
    percent_filled: float
    filled: list
    missing: list


def parse_sections(body: str) -> dict[str, str]:
    """Parse issue body into a dictionary that maps headings to sub-content."""

    # Regex to split the body into sections based on H3 headers
    # Example body: `Ignored\n### Greeting\nHello world ### Goodbye\n\n Goodbye world`
    # Example sections: ["Ignored", "Greeting", "Hello world", "Goodbye", "Goodbye world"]
    sections = re.split(r"###\s*(.+)\n", body)

    # Create a dictionary of sections
    parsed_sections = {}

    # Iterate through each title, content pair
    # the interval 2 to keep the title and content together
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        content = sections[i + 1].strip()
        parsed_sections[title] = content

    return parsed_sections


def analyze_sections(
    sections: dict[str, str],
    required_sections: list[str],
) -> SectionAnalysis:
    """Calculate the percentage of required sections that are filled out."""
    filled = []
    missing = []
    for section in required_sections:
        # Only consider a section complete if it has more than 20 characters
        # or if it explicitly uses "N/A"
        if section in sections and (
            len(sections[section]) > 20 or sections[section] == "N/A"
        ):
            filled.append(section)
        else:
            missing.append(section)
    percent_filled = (len(filled) / len(required_sections)) * 100
    return SectionAnalysis(percent_filled, filled, missing)


# Main script
def main():
    parser = argparse.ArgumentParser(description="Analyze sections in JSON data.")
    parser.add_argument("input_file", help="Path to the input JSON file")
    parser.add_argument(
        "--required-sections",
        nargs="+",
        required=True,
        help="List of required sections",
    )
    args = parser.parse_args()

    # Load data from JSON file
    with open(args.input_file, "r") as file:
        data = json.load(file)

    # Process each record
    for record in data:
        title = record.get("title", "Untitled")
        participant_count = record.get("participant_count", 0)
        body = record.get("body", "")
        url = record.get("url", "")

        sections = parse_sections(body)
        analysis = analyze_sections(sections, args.required_sections)

        # Output results
        print(f"### {title}")
        print(f"- URL: {url}")
        print(f"- Participant count: {participant_count}")
        print(f"- Percent of template complete: {round(analysis.percent_filled)}%")
        print(f"- Filled sections: {analysis.filled}")
        print(f"- Incomplete sections: {analysis.missing}\n")


if __name__ == "__main__":
    main()
