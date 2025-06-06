import pandas as pd
import numpy as np
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt

def separation_data(folder_path, output_csv_path, max_separation=500, bin_size=5):
    file_list = glob.glob(os.path.join(folder_path, 'groundtime_stats*.csv'))
    all_separation_records = []

    for file_path in file_list:
        df = pd.read_csv(file_path, parse_dates=['t_start'])
        df['date'] = df['t_start'].dt.date
        df['hour'] = df['t_start'].dt.hour

        for runway in df['used_runway'].unique():
            df_runway = df[df['used_runway'] == runway].sort_values('t_start').reset_index(drop=True)
            separations = df_runway['t_start'].diff().dt.total_seconds().dropna()
            clean_separations = separations[(separations > 0) & (separations < max_separation)]
            
            # Get hours aligned by position (not index)
            hour_values = df_runway['hour'].iloc[1:].values
            hour_filtered = hour_values[clean_separations.reset_index(drop=True).index.values]
            
            # Collect records
            tmp_df = pd.DataFrame({
                'used_runway': runway,
                'date': df_runway['date'].iloc[1:].values[clean_separations.reset_index(drop=True).index.values],
                'hour': hour_filtered,
                'separation': clean_separations.values
            })
            all_separation_records.append(tmp_df)

    combined_df = pd.concat(all_separation_records, ignore_index=True)

    # Step 1: Aggregate per runway, date, hour
    hourly_summary = combined_df.groupby(['used_runway', 'date', 'hour']).agg(
        mean_separation=('separation', 'mean'),
        count_ops=('separation', 'count')
    ).reset_index()

    # Step 2: Calculate total operations per hour across all runways (per date)
    hourly_ops = hourly_summary.groupby(['date', 'hour']).agg(
        total_ops=('count_ops', 'sum')
    ).reset_index()

    # Step 3: Merge total_ops back to hourly_summary
    merged = pd.merge(hourly_summary, hourly_ops, on=['date', 'hour'], how='left')

    # Step 4: Bin total_ops into ranges (e.g., 0–4, 5–9, ...)
    merged['ops_bin'] = (merged['total_ops'] // bin_size) * bin_size

    # Step 5: Calculate mean separation per runway per ops_bin
    final_summary = merged.groupby(['ops_bin', 'used_runway']).agg(
        avg_separation=('mean_separation', 'mean')
    ).reset_index()
    
    # Save to CSV
    final_summary.to_csv(output_csv_path, index=False)
    return final_summary


import pandas as pd
import matplotlib.pyplot as plt

def plot_separation_summary(csv_path, save_path=None, bin_size=5):
    # Load data
    df = pd.read_csv(csv_path)

    pivot_df = df.pivot(index='ops_bin', columns='used_runway', values='avg_separation')
    pivot_df.columns = [f"Runway {int(rw)}" for rw in pivot_df.columns]

    # Define your custom colors
    colors = {
    "Runway 1": '#7fbfff',
    "Runway 2": '#1b2a38',
    "Runway 3": '#bdbdbd'
    }

    # Prepare formatted bin labels
    bin_edges = pivot_df.index
    bin_labels = [f"{b + 1}-{b + bin_size}" for b in bin_edges]

    # Plot settings
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Apply color mapping
    color_list = [colors[runway] for runway in pivot_df.columns]

    ax = pivot_df.plot(kind='bar', figsize=(12, 8), width=0.8, edgecolor='black', color=color_list, ax=ax)

    # Custom X-tick labels
    ax.set_xticklabels(bin_labels)

    # Labels and title
    plt.xlabel('Operations/h (binned)', fontsize=12)
    plt.ylabel('Average Separation Time (s)', fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Tight layout
    plt.tight_layout()

    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


