import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn3_unweighted

# --- Configuration ---
REGION_NAME_COL = 'kommunnamn'
FORECAST_YEAR = 2026
INCREASE_COLS = {
    'Kids': 'kids_population_increase_p',
    'Adults (HPP)': 'adult_population_increase_p',
    'Seniors (Retired)': 'senior_population_increase_p'
}

# 2. Filter: Only include regions predicted to grow (increase > 0) in AT LEAST ONE dimension.
growth_filter = (
    (df[INCREASE_COLS['Kids']] > 0) |
    (df[INCREASE_COLS['Adults (HPP)']] > 0) |
    (df[INCREASE_COLS['Seniors (Retired)']] > 0)
)
df_growing = df[growth_filter].copy()

# 3. Define Relative "High Growth" Thresholds (Median of the growing regions)
kids_growth_threshold = df_growing[INCREASE_COLS['Kids']].median()
adult_growth_threshold = df_growing[INCREASE_COLS['Adults (HPP)']].median()
senior_growth_threshold = df_growing[INCREASE_COLS['Seniors (Retired)']].median()

# --- 4. Set Creation for Overlap Calculation ---
# Use the DataFrame index as a unique ID for the set operations
set_kids_growth = set(df_growing[df_growing[INCREASE_COLS['Kids']] > kids_growth_threshold].index)
set_adult_growth = set(df_growing[df_growing[INCREASE_COLS['Adults (HPP)']] > adult_growth_threshold].index)
set_senior_growth = set(df_growing[df_growing[INCREASE_COLS['Seniors (Retired)']] > senior_growth_threshold].index)

# Define the sets for easier logic
A = set_kids_growth
B = set_adult_growth
C = set_senior_growth

# Calculate all 7 non-overlapping segments required by venn3_unweighted
# Order: (A\B\C, B\A\C, A^B\C, C\A\B, A^C\B, B^C\A, A^B^C)
subsets = (
    len(A - B - C),                  # Kids Only (a)
    len(B - A - C),                  # Adults Only (b)
    len(A.intersection(B) - C),      # Kids & Adults (ab)
    len(C - A - B),                  # Seniors Only (c)
    len(A.intersection(C) - B),      # Kids & Seniors (ac)
    len(B.intersection(C) - A),      # Adults & Seniors (bc)
    len(A.intersection(B).intersection(C)) # All Three (abc)
)
#pick names for each segment by randomly choosing a kommun in the subset
subsets = (
    "\n".join(df_growing.loc[list(A - B - C), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(B - A - C), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(A.intersection(B) - C), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(C - A - B), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(A.intersection(C) - B), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(B.intersection(C) - A), REGION_NAME_COL].sample(2).values),
    "\n".join(df_growing.loc[list(A.intersection(B).intersection(C)), REGION_NAME_COL].sample(3).values)
)

def main():
    # 1. Load Data from parquet
    df = pd.read_parquet('./data/geoparquet/population_predictions_2024_kommun.parquet')

    plt.figure(figsize=(10, 8))
    venn3_unweighted(
        subsets=subsets,
        set_labels=('Kids (Above Median Growth)', 'Adults (HPP, Above Median Growth)', 'Seniors (Above Median Growth)'),
        set_colors=('skyblue', 'lightcoral', 'lightgreen'),
        alpha=0.7
    )

    plt.title(f'Overlap of High-Growth Communes (2024-{FORECAST_YEAR})')
    plt.tight_layout()
    plt.savefig('market_overlap_venn_diagram.png')
    plt.close()
    print("Venn Diagram saved as 'market_overlap_venn_diagram.png'.")

if __name__ == "__main__":
    main()