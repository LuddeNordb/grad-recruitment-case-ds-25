# Nordic Expansion Strategy - Data Analysis

For detailed case instructions and submission requirements, follow the [instructions](INSTRUCTIONS.md).

## Project Overview

This project provides quantitative forecasts of Swedish demographic changes in the near future to guide market entry and potential decisions. My work involved three steps:\ \
**Data Preparation:** I combined nine years (2015–2024) of $1\text{km}^2$ population data into a single dataset and aggregated the population into three strategic groups: Kids, Adults, and Seniors.\ \
**Forecasting:** I used an XGBoost machine learning model to predict the population change for each of the three groups in every $1\text{km}^2$ square for the years $\mathbf{2024}$ to $\mathbf{2026}$. I used four years of historical data for each square as well as the mean aggregated regional and communal population size as predictors for future growth. The predicted results were then aggregated per commune, and a percentage change in the three groups was calculated based on the 2024 actual population and the predicted 2026 population.\ \
**Strategic Visualization:** I created two key tools for decision-makers:\ 
Quadrant Matrices: These charts plot Communes based on their Current Market Size (X-axis) and Predicted Growth (Y-axis). This clearly separates markets into four categories: Golden Markets, Future Hubs, Mature, and Shrinking, informing location and timing.\
Overlap Analysis: This analysis identifies the regions where High Growth is predicted to occur simultaneously across multiple demographic groups (e.g., "All Three Hotspots"), guiding the optimal resource allocation strategy for diversified investments.

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
pip install pandas numpy scikit-learn matplotlib seaborn xgboost matplotlib-venn geopandas pyarrow
```

## Usage

```bash
# TODO: Add command(s) to run all of the code to generate the assets used in your analysis and presentation.
# Ensure your environment is active: source venv/bin/activate

# 1. Execute the script to generate the combined Parquet file which contains data for all years as well as region names
python create_dataset.py

# 2. Execute the script to train the regression models and update the tabular data with the predictions for percent change to 2026
python train_models.py

# 3. Execute the script to create the matrix plots which saves the images as outputs in the current direcctory
python create_matrixplot.py

# 4. Execute the script to create the venn diagram plots which saves the images
python create_venn.py
```
