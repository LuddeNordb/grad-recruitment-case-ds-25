# Nordic Expansion Strategy - Data Analysis

For detailed case instructions and submission requirements, follow the [instructions](INSTRUCTIONS.md).

## Project Overview

This project delivers a forward-looking, quantitative view of demographic shifts across Sweden to support informed market entry and investment decisions. The analysis was structured into three core workstreams:

**1. Data Preparation**  
I consolidated nine years of high-resolution (1 km²) population data (2015–2024) into a unified dataset and aggregated individuals into three strategic segments: **Kids**, **Adults**, and **Seniors**. This created a consistent historical foundation for analysing trends at both local and national scales.

**2. Forecasting**  
Using an XGBoost model, I forecasted population change for each demographic segment in every 1 km² grid cell for **2024–2026**. The model incorporated four years of historical data per grid, together with aggregated regional and municipal population indicators, to predict short-term growth trajectories. Forecasts were then aggregated to commune level, enabling calculation of expected percentage change from 2024 to 2026 for each segment.

**3. Strategic Visualisation**  
To translate results into actionable insights, I developed two complementary decision tools:  
- **Quadrant Matrices:** Plotting communes by *current market size* (X-axis) and *predicted growth* (Y-axis), segmenting them into **Golden Markets**, **Future Hubs**, **Mature**, and **Shrinking** areas, therefore clarifying both timing and investment potential.  
- **Overlap Analysis:** Identifying communes expected to experience concurrent growth across multiple demographic groups (“**All Three Hotspots**”), supporting prioritisation where diversified demand is most likely.

**Note on Further Verification**  
While the forecasting framework provides a strong directional signal, the underlying data and model outputs should be further validated to ensure no anomalies, artifacts, or data quality issues influence strategic decisions.

## Environment Setup

### 1. Download the Data

The dataset required for this assessment is hosted as a GitHub Release. Download it using one of the following methods:

```bash
# Using curl (Mac/Linux)
curl -L -o data.zip https://github.com/pds-eidra/grad-recruitment-case-ds-25/releases/download/v1.0-data/data.zip
unzip data.zip -d .
rm data.zip

# Using PowerShell (Windows)
Invoke-WebRequest -Uri "https://github.com/pds-eidra/grad-recruitment-case-ds-25/releases/download/v1.0-data/data.zip" -OutFile data.zip
Expand-Archive data.zip -DestinationPath .
Remove-Item data.zip
```

### 2. Environment & Dependencies

```bash
# 1. Setup the virtual environment, here we name it 'venv'
python -m venv venv

# 2. Activate the environment

# On Mac/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate

# 3. Install dependencies
pip install jupyter pandas numpy scikit-learn matplotlib seaborn xgboost matplotlib-venn geopandas pyarrow tabulate
```

## Usage

```bash
# Ensure your environment is active: source venv/bin/activate

jupyter nbconvert --to notebook --execute case.ipynb --output executed_analysis.ipynb 
```

Alterntivly everything can be run directly from the provided case.ipynb jupiter notebook. Outputs will be saved directly in the main directory
