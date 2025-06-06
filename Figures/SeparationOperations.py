import pandas as pd
import numpy as np
import os
import glob

def calculate_separation_times(folder_path):
    """
    Calculate separation times between consecutive operations for each runway.

    Args:
        df (pd.DataFrame): DataFrame with columns ['callsign', 'used_runway', 't_start', 't_end'].

    Returns:
        dict: Dictionary with runway as key and list of separation times (in seconds) as values.
    """
    
    all_separation_times = {}

    file_list = glob.glob(os.path.join(folder_path, 'runway_usage_stats*.csv'))
    
    for file_path in file_list:
        df = pd.read_csv(file_path)
    
        df['t_start'] = pd.to_datetime(df['t_start'])

        # Loop over each runway
        for runway in df['used_runway'].unique():
            df_runway = df[df['used_runway'] == runway].sort_values(['used_runway', 't_start'])
            separations = df_runway['t_start'].diff().dt.total_seconds().dropna().values      
            
            if runway not in all_separation_times:
                all_separation_times[runway] = separations
            else:
                all_separation_times[runway] = np.concatenate((all_separation_times[runway], separations))

    return all_separation_times


import matplotlib.pyplot as plt
import numpy as np

def plot_separation_times(separation_times_dict, bin_width=10):
    """
    Plot separation times for each runway in the same figure.

    Args:
        separation_times_dict (dict): Dictionary with runway as key and separation times array as value.
        bin_width (int): Width of each bin in seconds (default 10 seconds).
    """
    plt.figure(figsize=(14, 6))

    colors = {1: '#7fbfff', 2: '#1b2a38', 3: '#bdbdbd'}  
    max_time = 0

    for separations in separation_times_dict.values():
        if len(separations) > 0:
            max_time = max(max_time, np.max(separations))
    
    bins = np.arange(0, max_time + bin_width, bin_width)

    runway_order = [3, 1, 2] 
    for runway in runway_order:
        separations = separation_times_dict.get(runway, None)
        if separations is not None and len(separations) > 0:
            plt.hist(separations, bins=bins, alpha=0.7, label=f'Runway {runway}', color=colors.get(runway, None), edgecolor='black')

    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xlabel('Separation Time (s)', fontsize=12)
    plt.ylabel('Number of Operations', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.show()


