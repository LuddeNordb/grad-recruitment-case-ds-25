import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration (Based on your final DataFrame columns) ---
REGION_NAME_COL = 'kommunnamn'
FORECAST_YEAR = 2026

# The confirmed names for the predicted absolute increase (Y-axis)
INCREASE_COLS = {
    'Kids': 'kids_population_increase_p',
    'Adults (HPP)': 'adult_population_increase_p',
    'Seniors (Retired)': 'senior_population_increase_p'
}

# X-axis: Current Total Population (Market Size Proxy)
DENSITY_COL = 'beftotalt' 

def plot_quadrant_matrix_absolute(df, increase_col, title):
    """
    Generates the Strategic Quadrant Matrix Plot with:
    1. Absolute Predicted Increase on Y-axis (centered at 0).
    2. Population on the X-axis using a LOG SCALE, centered on the MEAN population.
    """
    df_plot = df.copy()
    
    # NOTE: Assuming df_plot is already aggregated to the commune level.
    REGION_NAME_COL = 'kommunnamn'
    DENSITY_COL = 'beftotalt'
    FORECAST_YEAR = 2026

    # --- Data Setup ---
    # Filter to the top 20 most populous communes for strategic focus
    top_n = 20
    df_plot = df_plot.nlargest(top_n, DENSITY_COL).copy()
    
    # --- Define Strategic Centers/Thresholds ---
    # Y-axis strategic center (Growth Threshold) is FIXED AT ZERO
    increase_threshold = 0 
    
    # X-axis strategic center (Density Threshold) is now the MEAN population
    density_mean = df_plot[DENSITY_COL].mean()
    
    # 1. Log-Center the X-axis on the MEAN (new logic)
    # Use log base 10 for standard visualization
    log_data = np.log10(df_plot[DENSITY_COL])
    log_mean = np.log10(density_mean)
    
    # Calculate the maximum distance (offset) from the log mean to the data extremes
    max_offset = np.max([log_mean - log_data.min(), log_data.max() - log_mean])
    
    # Add a small buffer for aesthetic padding
    buffer = 0.05 
    
    # Set the symmetric log limits
    log_xlim_min = log_mean - max_offset - buffer
    log_xlim_max = log_mean + max_offset + buffer
    
    # Convert back to natural scale for plotting limits (10^log_limit)
    data_xlim_min = 10**log_xlim_min
    data_xlim_max = 10**log_xlim_max
    
    # --- Quadrant Classification ---
    # The dividing line for the quadrants is now the MEAN
    high_density = df_plot[DENSITY_COL] >= density_mean
    low_density = df_plot[DENSITY_COL] < density_mean
    high_growth = df_plot[increase_col] >= increase_threshold
    low_growth = df_plot[increase_col] < increase_threshold
    
    # Classify regions
    df_plot.loc[high_density & high_growth, 'Quadrant'] = '1. Golden Markets (Above Average Pop, Growth)'
    df_plot.loc[low_density & high_growth, 'Quadrant'] = '2. Future Hubs (Below Average Pop, Growth)'
    df_plot.loc[high_density & low_growth, 'Quadrant'] = '3. Mature/Declining (Above Average Pop, Decline)'
    df_plot.loc[low_density & low_growth, 'Quadrant'] = '4. Non-Strategic/Shrinking (Below Average Pop, Decline)'

    # --- Visualization ---
    plt.figure(figsize=(10, 10))
    
    # Apply LOG SCALE and centered limits
    plt.xscale('log')
    plt.xlim(data_xlim_min, data_xlim_max)
    
    # Set Y-axis limits symmetrically around 0
    max_abs_y = df_plot[increase_col].abs().max()
    plt.ylim(-max_abs_y * 1.1, max_abs_y * 1.1)
    
    sns.scatterplot(
        x=DENSITY_COL, 
        y=increase_col, 
        hue='Quadrant', 
        data=df_plot, 
        palette='Spectral', 
        s=150
    )
    
    # Horizontal strategic line (Y=0)
    plt.axhline(increase_threshold, color='r', linestyle='-', linewidth=1.5, 
                label='Growth Center (Zero Change)')
    
    # Vertical strategic line (at the MEAN, which is now the visual center)
    plt.axvline(density_mean, color='b', linestyle='--', linewidth=1, 
                label=f'Density Center (Mean Pop: {int(density_mean/1000):,}K)')
    
    # Format X-axis ticks to display powers of 10 nicely
    plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(
        lambda x, p: format(int(x), ',')
    ))
    
    # Format Y-axis ticks for readability (in absolute numbers)
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(
        lambda y, p: format(int(y), ',')
    ))

    # Add labels for key communes
    if REGION_NAME_COL in df_plot.columns:
        for i in df_plot.index:
            plt.annotate(df_plot[REGION_NAME_COL][i], 
                         # Use log-transformed X position for annotation placement
                         (df_plot[DENSITY_COL][i] * 1.05, df_plot[increase_col][i]), 
                         fontsize=8)

    plt.title(f'Strategic Quadrant Analysis: {title} (Commune Level Forecast {FORECAST_YEAR})')
    plt.xlabel('2024 Total Commune Population (Market Size Proxy - LOG SCALE, Centered on MEAN)')
    plt.ylabel(f'{title} Predicted ABSOLUTE Increase (2024-{FORECAST_YEAR}, Number of People)')
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, title='Strategic Quadrant')
    plt.tight_layout()
    
    # Save the plot
    file_title = title.lower().replace(" ", "_").replace("(","_").replace(")","")
    plt.savefig(f'quadrant_matrix_log_centered_{file_title}.png')
    plt.close()
    
    print(f"Quadrant Matrix plot for {title} saved as 'quadrant_matrix_log_centered_{file_title}.png'.")

def main():
    # Load the comparison DataFrame Parquet file
    df_final_regional = pd.read_parquet('./data/geoparquet/population_predictions_2024_kommun.parquet')
    for title, col in INCREASE_COLS.items():
        plot_quadrant_matrix_absolute(df_final_regional.copy(), col, title)

    print("\n--- Centered Absolute Increase Quadrant Matrix Visualization Code Ready ---")

if __name__ == "__main__":
    main()