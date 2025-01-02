# Product strategy metrics

CLI script to calculate the metrics for the product strategy deliverable:

- Number of participants per deliverable
- Percentage of required sections complete per deliverable

## Usage

### Pre-requisites

- The repo is cloned locally
- Python 3.10 or greater is installed `python3 --version`
- [GiHub CLI](https://cli.github.com/) is installed and authenticated `gh auth login`

### Basic usage

From the root of the `automations/` directory run the following:

```bash
./product_strategy_metrics/run.sh \
 --org "HHS" \
 --project 12 \
 --batch 100 \
 --quad "Quad 1.1" \
 --section "Metrics" \
 --section "Press release" \
 --section "Acceptance criteria"
```

It should output something like the following:

```
### Search *
- URL: https://github.com/HHS/simpler-grants-gov/issues/2200
- Status: Done
- Participant count: 5
- Percent of template complete: 100%
- Filled sections: ['Metrics', 'Press release', 'Acceptance criteria']
- Incomplete sections: []

### Opportunity Listing *
- URL: https://github.com/HHS/simpler-grants-gov/issues/2203
- Status: Done
- Participant count: 5
- Percent of template complete: 100%
- Filled sections: ['Metrics', 'Press release', 'Acceptance criteria']
- Incomplete sections: []

### Engagement Sessions *
- URL: https://github.com/HHS/simpler-grants-gov/issues/2204
- Status: Done
- Participant count: 7
- Percent of template complete: 100%
- Filled sections: ['Metrics', 'Press release', 'Acceptance criteria']
- Incomplete sections: []

### Quad 1 Big Demo
- URL: https://github.com/HHS/simpler-grants-gov/issues/2215
- Status: In Progress
- Participant count: 3
- Percent of template complete: 0%
- Filled sections: []
- Incomplete sections: ['Metrics', 'Press release', 'Acceptance criteria']

...
```

### Parameters

The script currently supports two main parameters for calculating % complete:

- **Quad:** The quad whose deliverables should be included in the output. A value can be passed using the `--quad` flag, e.g. `--quad "Quad 1.1"
- **Required sections** The sections that should be considered "required" within the issue body. Multiple sections can be required by using the `--section` flag multiple times, e.g. `--section "Metrics" --section "Press release"`
