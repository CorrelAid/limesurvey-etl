import sys
import logging
import pandas as pd
from sqlalchemy import create_engine, exc


def clean(df: pd.DataFrame) -> bool:
    with open("include/cleaning.yaml"):
        pass

    # parse the yaml and call functions accordingly
    return True


def exclude_text(df: pd.DataFrame, column: pd.Series, value: str):
    return df[column] != "Nein"


def exclude_numbers(df: pd.DataFrame, column: pd.Series, value):
    pass
