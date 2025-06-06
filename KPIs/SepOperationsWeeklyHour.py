import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Function to compute hourly average separation per runway ===
def hourly_average_separation(folder_path):
    """
    Compute the average separation time per hour of the day across multiple days for each runway.
    
    Args:
        folder_path (str): Path to the folder with 'runway_usage_stats*.csv' files.
    
    Returns:
        dict: Dictionary where keys are runways and values are 24-element arrays with hourly averages.
    """
    file_list = glob.glob(os.path.join(folder_path, 'runway_usage_stats*.csv'))  # Get all files

    hourly_separations = {}  # Will store separation lists by hour for each runway

    for file_path in file_list:
        df = pd.read_csv(file_path)
        df['t_start'] = pd.to_datetime(df['t_start'])  # Ensure datetime format

        for runway in df['used_runway'].dropna().unique():  # Loop through each runway
            df_runway = df[df['used_runway'] == runway].sort_values('t_start')
            df_runway['separation'] = df_runway['t_start'].diff().dt.total_seconds()  # Compute time gaps
            df_runway = df_runway.dropna(subset=['separation'])  # Remove first NaN row

            df_runway['hour'] = df_runway['t_start'].dt.hour  # Extract hour from timestamp

            if runway not in hourly_separations:
                hourly_separations[runway] = [[] for _ in range(24)]  # Init list of lists for 24 hours

            # Append valid separations (≤550s) per hour
            for hour in range(23):  # Hour 0 to 22 (last is 22–23)
                separations_hour = df_runway[
                    (df_runway['hour'] == hour) & (df_runway['separation'] <= 550)
                ]['separation'].values
                hourly_separations[runway][hour].extend(separations_hour)

    # Calculate mean per hour per runway
    hourly_means = {
        runway: [np.mean(h) if len(h) > 0 else np.nan for h in hourly_separations[runway]]
        for runway in hourly_separations
    }

    return hourly_means


# === Function to save hourly means to CSV ===
def save_hourly_separation_to_csv(hourly_means, output_path):
    """
    Save hourly separation means to a CSV file.
    
    Args:
        hourly_means (dict): Output from `hourly_average_separation()`.
        output_path (str): Path to the CSV file to save.
    """
    df_out = pd.DataFrame(hourly_means)
    df_out.index.name = 'Hour'  # Name the index column
    df_out.to_csv(output_path)


# === Function to plot the grouped bar chart ===
def plot_hourly_separation_bars(csv_folder_path):
    """
    Plot a grouped bar chart of average hourly separation time (from 04h to 22h)
    using customized colors, transparency, and edge styling.
    
    Args:
        csv_folder_path (str): Path to the folder containing 'hourly_separation_by_runway.csv'
    """
    # === CONFIGURATION ===
    csv_path = os.path.join(csv_folder_path, 'hourly_separation_by_runway.csv')
    colors = {1: '#7fbfff', 2: '#1b2a38', 3: '#bdbdbd'}  # Custom colors for each runway
    runway_names = {1: 'Runway 1', 2: 'Runway 2', 3: 'Runway 3'}
    alpha = 0.8
    edge_color = 'gray'

    # === LOAD DATA ===
    df = pd.read_csv(csv_path, index_col='Hour')
    df = df.loc[4:22]  # Focus on operational hours: 04:00–22:59

    # Rename columns to ensure consistent keys
    if list(df.columns) != [1, 2, 3]:
        df.columns = [1, 2, 3]

    # === PLOT ===
    x = np.arange(len(df))  # X positions
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, runway in enumerate([1, 2, 3]):
        ax.bar(
            x + i * bar_width,
            df[runway],
            width=bar_width,
            label=runway_names[runway],
            color=colors[runway],
            alpha=alpha,
            edgecolor=edge_color,
            linewidth=1
        )

    # === STYLING ===
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_xticks(x + bar_width)
    ax.set_xticklabels([f'{h:02d}–{(h+1)%24:02d}' for h in df.index])
    ax.set_ylabel('Average Separation Time (s)')
    ax.legend()
    plt.tight_layout()
    plt.show()


# === MAIN EXECUTION ===

folder_path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\Usage"  # Adjust path as needed
output_csv = os.path.join(folder_path, 'hourly_separation_by_runway.csv')

# Compute averages
hourly_means = hourly_average_separation(folder_path)

# Save to CSV
save_hourly_separation_to_csv(hourly_means, output_csv)

# Plot grouped bar chart
plot_hourly_separation_bars(folder_path)
