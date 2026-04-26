# Tableau Dashboard Guide

## Recommended Dashboard Title

**Nationwide U.S. Air Quality Intelligence Dashboard**

## Tableau Files to Import

Use these outputs from the project workflow:

- `dashboard/tableau/tableau_state_summary.csv`
- `dashboard/tableau/tableau_monthly_summary.csv`
- `dashboard/tableau/dashboard_kpis.json`
- charts from `visuals/` for reference

## Suggested Tableau Sheets

### 1. U.S. AQI Map

Fields:

- `State`
- `State_Code`
- `Average_AQI`
- `AQI_Category`

Purpose:

- color each state by average AQI
- show map tooltip with AQI, rank, and region

### 2. Top 10 Polluted States

Fields:

- `State`
- `Average_AQI`
- `Rank`

Purpose:

- show the highest average AQI states
- use descending bar chart

### 3. Cleanest States

Fields:

- `State`
- `Average_AQI`
- `Rank`

Purpose:

- compare lower-pollution states
- use separate bar chart or parameter toggle

### 4. Monthly AQI Trend

Fields:

- `Month`
- `Average_AQI`
- `Observation_Count`

Purpose:

- track change in AQI over time

### 5. KPI Summary Cards

Use:

- national average AQI
- total records
- states covered
- most polluted state
- cleanest state

## Recommended Filters

- `Region`
- `State`
- `AQI_Category`
- `Month` if you connect the monthly sheet separately

## Dashboard Layout

Top row:

- title
- KPI cards

Middle row:

- U.S. map
- top polluted states chart

Bottom row:

- monthly trend
- cleanest states chart

## Storytelling Tips

- highlight the most polluted state in a callout
- add a short note about the dataset source and date range
- keep colors consistent between AQI severity and chart elements
