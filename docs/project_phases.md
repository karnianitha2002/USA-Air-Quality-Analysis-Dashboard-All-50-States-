# Project Phases

## Phase 1: Data Collection and Scope Definition

Purpose:
Build the foundation for the project by selecting a dataset and defining analysis coverage.

Checklist:

- choose EPA or Kaggle source
- confirm 50-state coverage if possible
- inspect available columns
- note date range and update frequency
- store raw files in `data/raw/`

Success criteria:

- dataset is downloaded
- source is documented
- file format is ready for Python analysis

## Phase 2: Data Cleaning and Preparation

Purpose:
Transform raw data into a consistent, analysis-ready dataset.

Checklist:

- remove missing `State` and `AQI` rows
- remove duplicates
- standardize state naming
- parse `Date`
- retain analysis columns
- save cleaned output to `data/processed/`

Success criteria:

- cleaned dataset is reproducible
- core columns are valid
- state names are consistent

## Phase 3: Analysis and Insight Generation

Purpose:
Compute the main metrics and answer the business question.

Checklist:

- calculate average AQI per state
- rank most and least polluted states
- create monthly trend summaries
- explore pollutant relationships
- export tables and charts

Success criteria:

- state averages are computed
- ranking table is ready
- charts support dashboard storytelling

## Phase 4: Dashboard and Portfolio Packaging

Purpose:
Convert the analysis into recruiter-friendly deliverables.

Checklist:

- build Tableau dashboard
- create U.S. state map
- add comparison filters and KPI cards
- prepare report and presentation
- finalize GitHub documentation

Success criteria:

- dashboard is interactive
- visuals are portfolio-ready
- repo is easy to review and present
