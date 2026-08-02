#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns

def plot_HR_by_stage(data, stage_col='Stage', time_col='Time (s)', hr_col='HR'):
    """
    Plots the HR by stage.
    
    INPUTS:
        data: pandas DataFrame containing the data to plot
        stage_col: str, name of the column containing the stage information
        time_col: str, name of the column containing the time information
        hr_col: str, name of the column containing the HR information
    
    OUTPUT:
        None
    
    """
    plt.figure(figsize=(10, 6))

    colors = {'B': 'blue', '1': 'green', '2': 'purple'}
    for stage in data[stage_col].unique():
        stage_data = data[data[stage_col] == stage]
        plt.scatter(stage_data[time_col], stage_data[hr_col], color=colors[stage], label=f'Stage {stage}')
     
    sns.despine()    
    plt.xlabel('Time (s)')
    plt.ylabel('Observed Heart Rate (HR)')
    plt.title('HR by Stage')
    plt.legend() 