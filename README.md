# USA Air Quality Analysis Dashboard

Analyze air quality across all 50 U.S. states using Python and Tableau, then present the results through state rankings, trend analysis, and GIS-based dashboard views.

## Project Objective

This project focuses on:

- collecting U.S. air quality data
- cleaning and standardizing pollutant records
- calculating average AQI by state
- ranking states by pollution level
- building visualizations and a final dashboard

## Recommended 4-Phase Plan

### Phase 1: Data Collection and Project Setup

Goal: gather a reliable dataset and organize the repository.

Tasks:

- download EPA or Kaggle air quality CSV data
- verify core fields like `State`, `Date`, and `AQI`
- store original files in `data/raw/`
- document source details and scope

Deliverables:

- raw dataset
- finalized repo structure
- dependency list

### Phase 2: Data Cleaning and Preparation

Goal: make the dataset analysis-ready.

Tasks:

- remove nulls and duplicates
- standardize state names
- convert date columns
- keep useful pollutant columns
- export cleaned data to `data/processed/`

Deliverables:

- cleaned dataset
- data quality notes
- reproducible cleaning steps

### Phase 3: AQI Analysis and Visualization

Goal: compute insights and produce charts.

Tasks:

- calculate average AQI per state
- create pollution rankings
- analyze monthly AQI trends
- build correlation heatmaps and comparison charts
- save charts in `visuals/`

Deliverables:

- state average AQI table
- ranked pollution summary
- exploratory visuals

### Phase 4: Dashboard, GIS Storytelling, and Portfolio Delivery

Goal: turn the analysis into a strong portfolio project.

Tasks:

- import processed data into Tableau
- build KPI cards, filters, rankings, and U.S. map
- prepare project report and presentation
- write resume-ready project summary

Deliverables:

- Tableau dashboard
- final report
- presentation PDF
- polished GitHub README

## Repository Structure

```text
USA_Air_Quality_Dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── notebooks/
├── src/
├── visuals/
├── dashboard/
│   ├── tableau/
│   └── streamlit/
├── report/
├── docs/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## Key Dataset Columns

Priority columns:

- `State`
- `City`
- `Date`
- `AQI`

Useful pollutant columns:

- `PM2.5`
- `PM10`
- `NO2`
- `SO2`
- `CO`
- `O3`

## Starter Workflow

1. Place the source CSV inside `data/raw/`.
2. Clean and standardize the dataset.
3. Save the cleaned version to `data/processed/`.
4. Run state-level AQI analysis.
5. Export visuals and connect the processed file to Tableau.

## Python Libraries

Install core packages:

```bash
pip install -r requirements.txt
```

Optional dashboard package:

```bash
pip install streamlit
```

## Phase 2 Run Command

After placing a raw CSV in `data/raw/`, run:

```bash
python -m src.data_cleaning --input data/raw/your_file.csv
```

This will:

- save a cleaned CSV into `data/processed/`
- save a JSON cleaning summary into `report/`
- standardize common column-name variations automatically

## Phase 3 Run Command

After Phase 2 creates a cleaned CSV, run:

```bash
python3 -m src.aqi_analysis --input data/processed/your_file_cleaned.csv
```

This will:

- create `state_average_aqi.csv` with rankings
- export monthly trend and AQI category tables
- generate chart images inside `visuals/`
- save a Phase 3 summary report into `report/`

## Phase 4 Run Command

After Phase 3 is complete, run:

```bash
python3 -m src.dashboard_prep --input data/processed/your_file_cleaned.csv
```

This will:

- create Tableau-ready state summary files in `dashboard/tableau/`
- prepare KPI JSON for dashboard cards
- add map-ready fields like state code and region
- save a Phase 4 manifest into `report/`

## Optional Demo Dataset

If you want to test the full project before downloading a real dataset, generate a synthetic cleaned file:

```bash
python3 -m src.generate_sample_data
```

This creates:

- `data/processed/sample_aqi_2024_cleaned.csv`

Important:

- this sample is synthetic for demo purposes
- replace it with a real EPA or Kaggle dataset before publishing final results

## Resume-Ready Project Title

**Nationwide U.S. Air Quality Intelligence Dashboard**

Suggested description:

- Analyzed air quality data across all 50 U.S. states using Python and Tableau
- Calculated state-wise average AQI and developed pollution ranking models
- Built interactive dashboards for environmental monitoring and decision support
