#!/usr/bin/env python3


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