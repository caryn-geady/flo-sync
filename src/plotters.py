#!/usr/bin/env python3

import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

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
        None (displays the plot)
    
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
    

def plot_co_vti_overlay(analysis_df, stage_order=['B', '1', '2']):
    """Dual-axis time-series overlay with stage shading
    
    INPUT:
        analysis_df: pd.DataFrame, containing the aligned and cleaned data for analysis.
        stage_order: list, order of stages for shading and labeling.
        
    OUTPUT:
        None (displays the plot)
    """
    fig, ax1 = plt.subplots(figsize=(12, 4.8))
    ax2 = ax1.twinx()

    ax1.plot(analysis_df['TimeSec'], analysis_df['CO'], color='tab:blue', lw=1.8, label='CO')
    ax2.plot(analysis_df['TimeSec'], analysis_df['VTI'], color='tab:orange', lw=1.8, alpha=0.9, label='VTI')

    palette = ['blue','green','purple']
    for i, stage in enumerate(stage_order):
        stage_mask = analysis_df['Stage'] == stage
        if stage_mask.sum() == 0:
            continue
        start_t = analysis_df.loc[stage_mask, 'TimeSec'].min()
        end_t = analysis_df.loc[stage_mask, 'TimeSec'].max()
        ax1.axvspan(start_t, end_t, color=palette[i], alpha=0.14, zorder=0)
        ax1.text(
            (start_t + end_t) / 2,
            0.98,
            str(stage),
            transform=ax1.get_xaxis_transform(),
            ha='center',
            va='top',
            fontsize=9,
            color='0.25'
        )

    ax1.set_title('Aligned Time-Series Overlay: CO and VTI by Stage')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('CO', color='tab:blue')
    ax2.set_ylabel('VTI', color='tab:orange')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    custom_lines = [
        Line2D([0], [0], color='tab:blue', lw=2, label='CO'),
        Line2D([0], [0], color='tab:orange', lw=2, label='VTI'),
    ]
    ax1.legend(handles=custom_lines, loc='upper left')
    sns.despine(right=False)
    plt.tight_layout()
    plt.show()
    
def _safe_zscore(series):
    """
    Calculate z-score for CO and VTI.

    INPUT:
        series: pd.Series, the data for which to calculate the z-score.
    OUTPUT:
        pd.Series, containing the z-scores of the input series.
    """
    std = series.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - series.mean()) / std

def bland_altman_plot(analysis_df):
    """
    Create a Bland-Altman plot for the given analysis DataFrame.

    INPUT:
        analysis_df: pd.DataFrame, containing the aligned and cleaned data for analysis.
    OUTPUT:
        None (displays the plot)
    """
    
    # normalized Bland-Altman analysis (z-scored due to differing units)
    analysis_df['CO_z'] = _safe_zscore(analysis_df['CO'])
    analysis_df['VTI_z'] = _safe_zscore(analysis_df['VTI'])
    ba_mean = (analysis_df['CO_z'] + analysis_df['VTI_z']) / 2
    ba_diff = analysis_df['VTI_z'] - analysis_df['CO_z']

    bias = ba_diff.mean()
    sd_diff = ba_diff.std(ddof=1)
    loa_upper = bias + 1.96 * sd_diff
    loa_lower = bias - 1.96 * sd_diff

    palette = ['blue', 'green', 'purple']

    plt.figure(figsize=(7.5, 5.2))
    sns.scatterplot(
        x=ba_mean,
        y=ba_diff,
        hue=analysis_df['Stage'],
        palette=palette,
        alpha=0.7,
        s=36,
        edgecolor='none'
    )
    plt.axhline(bias, color='black', linestyle='-', lw=1.8, label=f'Bias = {bias:.3f}')
    plt.axhline(loa_upper, color='firebrick', linestyle='--', lw=1.6, label=f'+1.96 SD = {loa_upper:.3f}')
    plt.axhline(loa_lower, color='firebrick', linestyle='--', lw=1.6, label=f'-1.96 SD = {loa_lower:.3f}')
    plt.title('Normalized Bland-Altman Plot (VTI_z - CO_z)')
    plt.xlabel('Mean of z-scored CO and VTI')
    plt.ylabel('Difference (VTI_z - CO_z)')
    plt.legend(loc='best')
    sns.despine()
    plt.tight_layout()
    plt.show()
    
def regression_plot(analysis_df):
    """
    Create a regression plot for the given analysis DataFrame.

    INPUT:
        analysis_df: pd.DataFrame, containing the aligned and cleaned data for analysis.
    OUTPUT:
        None (displays the plot)
    """
    # scatter + regression with 95% confidence bands
    sns.set_theme(style='whitegrid', context='notebook')
    palette = ['blue', 'green', 'purple']

    g = sns.lmplot(
        data=analysis_df,
        x='CO',
        y='VTI',
        col='Stage',
        col_wrap=3,
        hue='Stage',
        palette=palette,
        height=4,
        scatter_kws={'alpha': 0.6, 's': 22},
        line_kws={'color': 'black', 'lw': 2},
        ci=95,
    )
    g.fig.subplots_adjust(top=0.88)
    g.fig.suptitle('Stage-wise Regression: CO vs VTI (95% CI)', fontsize=14)
    plt.show()

    plt.figure(figsize=(6, 5))
    sns.regplot(
        data=analysis_df,
        x='CO',
        y='VTI',
        scatter_kws={'alpha': 0.45, 's': 20},
        line_kws={'color': 'black', 'lw': 2},
        ci=95,
        color='tab:blue'
    )
    plt.title('Overall Regression: CO vs VTI (95% CI)')
    plt.xlabel('CO')
    plt.ylabel('VTI')
    sns.despine()
    plt.tight_layout()
    plt.show()