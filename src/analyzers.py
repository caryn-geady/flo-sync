#!/usr/bin/env python3

import pandas as pd


def build_analysis_df(fp_data, labchart_data, remove_invalid=True):
    """
    Consolidate fp_data and labchart_data into a single DataFrame for analysis.

    INPUT:
        fp_data: pd.DataFrame, containing the processed flo data with corrected time and stage information.
        labchart_data: pd.DataFrame, containing the labchart data.
        remove_invalid: bool, whether to remove invalid rows from the final DataFrame.

    OUTPUT:
        analysis_df: pd.DataFrame, containing aligned and cleaned data for analysis.
        _type_: _description_
    """

    # resample the labchart_data to the same time base as the fp_data post-alignment
    desired_time_base = fp_data['Corrected Time (s)'].values

    labchart_sorted = labchart_data.sort_values('TimeSec').set_index('TimeSec')

    labchart_data_resampled = pd.DataFrame({'TimeSec': desired_time_base})

    for col in labchart_sorted.columns:
        if pd.api.types.is_numeric_dtype(labchart_sorted[col]):
            labchart_data_resampled[col] = np.interp(
                desired_time_base,
                labchart_sorted.index.to_numpy(),
                labchart_sorted[col].to_numpy()
            )
            
    # Build a unified analysis table from aligned fp_data and labchart_data_resampled
    analysis_df = fp_data[['Corrected Time (s)', 'Stage', 'Vmax VTI Total']].copy()
    analysis_df = analysis_df.rename(columns={
        'Corrected Time (s)': 'TimeSec',
        'Vmax VTI Total': 'VTI'
    })
    analysis_df['CO'] = labchart_data_resampled['CO'].to_numpy()
    
    analysis_df = analysis_df.replace([np.inf, -np.inf], np.nan).dropna(subset=['TimeSec', 'Stage', 'CO', 'VTI']).copy()
    analysis_df = analysis_df.sort_values('TimeSec').reset_index(drop=True)

    if remove_invalid:
        # Remove any rows where CO or VTI are zero or negative, as these are physiologically implausible
        analysis_df = analysis_df[(analysis_df['CO'] > 0) & (analysis_df['VTI'] > 0)].copy()
    
    return analysis_df