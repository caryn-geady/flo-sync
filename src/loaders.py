#!/usr/bin/env python3

import os
import pandas as pd


def load_data(data_dir):
    """
    Load data from the specified directory. Expects two data files, 'FPdata' and 'labchartdata'. 
    
    INPUT:
        data_dir: str, path to the directory containing the data files.
    OUTPUT:
        fp_data: pandas DataFrame, containing the FPdata.
        labchart_data: pandas DataFrame, containing the labchartdata.
    
    """
    
    filenames = os.listdir(data_dir)
    
    fp_file = [f for f in filenames if 'FPdata' in f][0]
    labchart_file = [f for f in filenames if 'labchartdata' in f][0]
    fp_ext = os.path.splitext(fp_file)[1]
    labchart_ext = os.path.splitext(labchart_file)[1]
    
    supported_extensions = ['.csv', '.xls', '.xlsx', '.txt']
    if fp_ext not in supported_extensions:
        raise ValueError(f"Unsupported file extension for FPdata: {fp_ext}. Supported extensions are: {supported_extensions}")
    if labchart_ext not in supported_extensions:
        raise ValueError(f"Unsupported file extension for labchartdata: {labchart_ext}. Supported extensions are: {supported_extensions}")
    
    # load data according to extension
    if fp_ext in ['.xls', '.xlsx']:
        fp_data = pd.read_excel(os.path.join(data_dir, fp_file))
    elif fp_ext == '.csv':
        fp_data = pd.read_csv(os.path.join(data_dir, fp_file))
    elif fp_ext == '.txt':
        fp_data = pd.read_csv(os.path.join(data_dir, fp_file), delimiter='\t')
    
    if labchart_ext in ['.xls', '.xlsx']:
        labchart_data = pd.read_excel(os.path.join(data_dir, labchart_file))
    elif labchart_ext == '.csv':
        labchart_data = pd.read_csv(os.path.join(data_dir, labchart_file))
    elif labchart_ext == '.txt':
        labchart_data = pd.read_csv(os.path.join(data_dir, labchart_file), delimiter='\t')

    return fp_data, labchart_data