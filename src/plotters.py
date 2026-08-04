#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns

def plot_HR_by_stage(data, ref_data=None, stage_col='Stage', time_col='Time (s)', ref_time_col='TimeSec', hr_col='HR', xlim=None):
    """
    Plots the HR by stage.
    
    INPUT:
        data: pandas DataFrame containing the data to plot
        ref_data: pandas DataFrame containing the reference data to plot
        stage_col: str, name of the column containing the stage information
        time_col: str, name of the column containing the time information
        ref_time_col: str, name of the column containing the reference time information
        hr_col: str, name of the column containing the HR information
        xlim: tuple, optional, limits for the x-axis (time). 
    
    OUTPUT:
        None
    
    """
    plt.figure(figsize=(10, 6))
    
    if ref_data is not None:
        plt.scatter(ref_data[ref_time_col], ref_data[hr_col], color='lightgray', alpha=0.1, label='labchart_data')

    colors = {'B': 'blue', '1': 'green', '2': 'purple'}
    for stage in data[stage_col].unique():
        stage_data = data[data[stage_col] == stage]
        plt.scatter(stage_data[time_col], stage_data[hr_col], color=colors[stage], alpha=0.3, label=f'Stage {stage}')
     
    sns.despine()    
    plt.xlabel('Time (s)')
    plt.ylabel('Observed Heart Rate (HR)')
    plt.title('HR by Stage')
    if xlim:
        plt.xlim(xlim)
    plt.legend(loc='upper left') 