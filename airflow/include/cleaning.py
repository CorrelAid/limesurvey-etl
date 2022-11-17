import sys
import logging
import pandas as pd

from airflow.models import Variable
from airflow.operators.python import PythonOperator


def concate_df() -> pd.DataFrame:
    """
    get the relevant tables and merge them into one pandas
    dataframe
    """
    pass

def create_cleaning_task():
    """
    use this function to dynamically create a cleaning task.
    """
    pass


def filter_out_int(df: pd.DataFrame, condition: str, value: int):
    """
    filter for integers bigger/smaller than specified in config
    """

    def smaller_than():
        pass

    def bigger_than():
        pass
    pass

def filter_str(df: pd.DataFrame, condition: str, value: str):
    """
    filter for strings specified in config
    """
    def keep():
        pass
    
    def exclude():
        pass

    pass


"""
1. read all the config from utils/config.py
2. loop over the config:
    - create tasks with arguments corresponding to the config
    - call the right functions
"""
