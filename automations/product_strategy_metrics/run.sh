#! /bin/bash
# Calculate product strategy metrics:
# - Number of participants per deliverable
# - Percentage of sections complete per deliverable
# 
# Usage (from root of automations sub-directory):
# ./product_strategy_metrics/run.sh \
#  --org "HHS" \
#  --project 12 \
#  --quad "Quad 1.1" \
#  --batch 100

# #######################################################
# Parse command line args with format `--option arg`
# #######################################################

# see this stack overflow for more details:
# https://stackoverflow.com/a/14203146/7338319
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      echo "Running in dry run mode"
      dry_run=YES
      shift # past argument
      ;;
    --org)
      org="$2"
      shift # past argument
      shift # past value
      ;;
    --project)
      project="$2"
      shift # past argument
      shift # past value
      ;;
    --batch)
      batch="$2"
      shift # past argument
      shift # past value
      ;;
    --quad)
      quad="$2"
      shift # past argument
      shift # past value
      ;;
    --section)
      required_sections+=("$2")
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

# #######################################################
# Set script-specific variables
# #######################################################

mkdir -p tmp # Create the tmp/ directory if it doesn't exist
script_dir="product_strategy_metrics"
raw_data_file="tmp/github-data-raw.json"
parsed_data_file="tmp/github-data-parsed.json"
github_query=$(cat "$script_dir/getDeliverableData.graphql")

# #######################################################
# Fetch GitHub data
# #######################################################

# # Call the GitHub GraphQL API using the GitHub CLI with pagination,
# # then use jq to combine the project items from the paginated response,
# # and write the resulting values to a JSON file

gh api graphql \
 --header 'GraphQL-Features:issue_types' \
 --field login="${org}" \
 --field project="${project}" \
 --field quadField="Quad" \
 --field batch="${batch}" \
 --paginate \
 -f query="${github_query}" \
 --jq ".data.organization.projectV2.items.nodes" | \
 jq --slurp 'add' > $raw_data_file

# #######################################################
# Extract the relevant data from each deliverable
# #######################################################

jq "[

  # Iterate through each deliverable
  .[] |

  # Filter deliverables based on quad
  select(.quad.title == \"$quad\") |

  # Extract and rename the relevant fields
  {
    title: .content.title,
    url: .content.url,
    participant_count: .content.participants.totalCount,
    body: .content.body,
    status: .status.name
  }

]" $raw_data_file > $parsed_data_file  # read from raw and write to parsed

# #######################################################
# Calculate and print metrics
# #######################################################

python3 "${script_dir}/calculate_metrics.py" "$parsed_data_file" --required-sections "${required_sections[@]}"
