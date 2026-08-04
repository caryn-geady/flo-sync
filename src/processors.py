#!/usr/bin/env python3

import pandas as pd, numpy as np
from scipy.interpolate import interp1d
from scipy import signal

def get_running_time(fp_data):
    """
    Calculates the running time for each stage in the data.
    
    INPUT:
        fp_data: pandas DataFrame containing the data with 'Stage' and 'Time (s)' columns.
    
    """
    fp_data['Corrected Time (s)'] = fp_data['Time (s)']

    # offset each stage's time by the end of the previous one
    for i in range(1, len(fp_data['Stage'].unique())):
        stage = fp_data['Stage'].unique()[i]
        prev_stage = fp_data['Stage'].unique()[i-1]
        prev_stage_time = fp_data[fp_data['Stage'] == prev_stage]['Corrected Time (s)'].max()
        fp_data.loc[fp_data['Stage'] == stage, 'Corrected Time (s)'] += prev_stage_time
  
      
def resample_to_common_time_base(labchart_data, fp_data, time_col_labchart='TimeSec', time_col_fp='Corrected Time (s)', hr_col='HR', desired_freq=1000):
    """
    Creates a common time base given the two dataframes.

    INPUT:
        labchart_data: pandas DataFrame, containing the labchartdata.
        fp_data: pandas DataFrame, containing the fpdata.
        time_col_labchart: str (optional), the column name for the time values in the labchart data. Defaults to 'TimeSec'.
        time_col_fp: str (optional), the column name for the time values in the fp data. Defaults to 'Corrected Time (s)'.
        hr_col: str (optional), the column name for the heart rate values. Defaults to 'HR'.
        desired_freq: int (optional), the desired sampling frequency. Defaults to 1000.

    OUTPUT:
        labchart_resampled: pandas DataFrame, containing the resampled labchart data.
        fp_resampled: pandas DataFrame, containing the resampled fp data.
    """
    
    max_time = max(labchart_data[time_col_labchart].max(), fp_data[time_col_fp].max())
    desired_time_base = np.arange(0, max_time, 1/desired_freq)

    interp_func_labchart = interp1d(
        labchart_data[time_col_labchart], labchart_data[hr_col], kind='linear', fill_value="extrapolate"
    )
    labchart_resampled = pd.DataFrame({
        time_col_labchart: desired_time_base,
        hr_col: interp_func_labchart(desired_time_base)
    })

    interp_func_fp = interp1d(
        fp_data[time_col_fp], fp_data[hr_col], kind='linear', fill_value="extrapolate"
    )
    fp_resampled = pd.DataFrame({
        time_col_fp: desired_time_base,
        hr_col: interp_func_fp(desired_time_base)
    })

    return labchart_resampled, fp_resampled


def estimate_sampling_frequency(data, time_col):
    """
    Estimate the effective sampling frequency from a time column using the median positive time step.
    
    INPUT:
        data: pandas DataFrame containing the time column.
        time_col: str, the name of the time column in the DataFrame.
        
    OUTPUT:
        estimated_freq: float, the estimated sampling frequency in Hz.
    """
    time_values = data[time_col].dropna().sort_values().to_numpy(dtype=float)
    if len(time_values) < 2:
        return 1.0

    deltas = np.diff(time_values)
    deltas = deltas[deltas > 0]
    if len(deltas) == 0:
        return 1.0

    median_delta = np.median(deltas)
    if median_delta <= 0:
        return 1.0

    return 1.0 / median_delta


def resample_to_regular_time_base(data, time_col='TimeSec', hr_col='HR', desired_freq=None, max_freq=10.0):
    """
    Resample a single dataframe onto a regular time base starting at 0 seconds.

    This is useful before cross-correlation because it preserves each signal's own
    duration instead of stretching both signals onto a shared absolute timeline.
    
    INPUT:
        data: pandas DataFrame containing the time and HR columns.
        time_col: str, the name of the time column in the DataFrame (default: 'TimeSec').
        hr_col: str, the name of the HR column in the DataFrame (default: 'HR').
        desired_freq: float, the desired sampling frequency in Hz. If None, it will be estimated from the data but capped at max_freq.
        max_freq: float, the maximum allowed sampling frequency in Hz (default: 10.0).
        
    OUTPUT:
        resampled_data: pandas DataFrame containing the resampled time and HR columns.
    """
    if data.empty:
        return pd.DataFrame({time_col: [], hr_col: []})

    sorted_data = data[[time_col, hr_col]].dropna().sort_values(time_col).reset_index(drop=True)
    if sorted_data.empty:
        return pd.DataFrame({time_col: [], hr_col: []})

    if desired_freq is None:
        desired_freq = min(max_freq, estimate_sampling_frequency(sorted_data, time_col))

    desired_freq = max(float(desired_freq), 1e-6)
    sample_period = 1.0 / desired_freq

    relative_time = sorted_data[time_col] - sorted_data[time_col].iloc[0]
    duration = float(relative_time.iloc[-1])
    if duration <= 0:
        return pd.DataFrame({time_col: [0.0], hr_col: [float(sorted_data[hr_col].iloc[-1])]})

    time_base = np.arange(0.0, duration + sample_period / 2.0, sample_period)
    interpolator = interp1d(relative_time, sorted_data[hr_col], kind='linear', fill_value='extrapolate')

    return pd.DataFrame({
        time_col: time_base,
        hr_col: interpolator(time_base),
    })
    
def get_stage_offset(stage, fp_data, labchart_data, fp_time_col='Corrected Time (s)', labchart_time_col='TimeSec', hr_col='HR'):
    """
    Calculate the time offset between the FP and LabChart data for a given stage.
    
    INPUT:
        - stage: str, the stage to analyze (e.g., '1', '2', 'B')
        - fp_data: DataFrame, the FP data containing 'Stage', 'Corrected Time (s)', and 'HR' columns
        - labchart_data: DataFrame, the LabChart data containing 'TimeSec' and 'HR' columns
        - fp_time_col: str, the column name for time in the FP data (default: 'Corrected Time (s)')
        - labchart_time_col: str, the column name for time in the LabChart data (default: 'TimeSec')
        - hr_col: str, the column name for heart rate in both datasets (default: 'HR')
        
    OUTPUT:
        - calculated_time_delay: float, the estimated time delay (in seconds) between the two datasets for the specified stage.
    """
    stage_fp = fp_data[fp_data['Stage'] == stage].copy()
    stage_start = stage_fp[fp_time_col].min()
    stage_end = stage_fp[fp_time_col].max()
    lab_window = labchart_data[(labchart_data[labchart_time_col] >= stage_start) & (labchart_data[labchart_time_col] <= stage_end)].copy()

    # estimate the native sampling rates and resample both signals to a shared frequency
    labchart_freq = estimate_sampling_frequency(lab_window, labchart_time_col)
    fp_freq = estimate_sampling_frequency(stage_fp, fp_time_col)
    target_freq = max(1.0, min(10.0, labchart_freq, fp_freq))
    sample_period = 1.0 / target_freq

    labchart_resampled = resample_to_regular_time_base(
        lab_window, time_col=labchart_time_col, hr_col=hr_col, desired_freq=target_freq
    )
    fp_resampled = resample_to_regular_time_base(
        stage_fp, time_col=fp_time_col, hr_col=hr_col, desired_freq=target_freq
    )

    # standardize signals to focus purely on alignment and not amplitude differences
    sig1 = labchart_resampled[hr_col].astype(float)
    sig2 = fp_resampled[hr_col].astype(float)
    sig1 = (sig1 - sig1.mean()) / sig1.std(ddof=0)
    sig2 = (sig2 - sig2.mean()) / sig2.std(ddof=0)


    correlation = signal.correlate(sig1, sig2, mode='full')
    lags = signal.correlation_lags(len(sig1), len(sig2), mode='full')

    best_lag_index = np.argmax(correlation)
    best_lag = lags[best_lag_index]
    calculated_time_delay = best_lag * sample_period

    print(f"Stage: {stage}")
    print(f"Stage window: {stage_start:.3f} s to {stage_end:.3f} s")
    print(f"Estimated sampling frequencies -> labchart window: {labchart_freq:.3f} Hz, fp stage {stage}: {fp_freq:.3f} Hz")
    print(f"Using shared resample frequency: {target_freq:.3f} Hz")
    print(f"Calculated Time Delay: {calculated_time_delay:.3f} seconds")
    print("-" * 50)
    
    return calculated_time_delay