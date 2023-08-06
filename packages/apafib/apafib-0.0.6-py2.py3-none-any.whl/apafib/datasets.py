"""
.. module:: Datasets.py

setup.py
******

:Description: Datasets.py

    Datasets functions

:Authors:
    bejar

:Version: 

:Date:  06/05/2022
"""
from apafib.config import DATALINK, datasets
import pandas as pd
from sklearn.utils import Bunch

def fetch_apa_data(name, version, target_column, return_X_y=False, as_frame=True):
    """_dataset fetching function_

    Args:
        name (_type_): _description_
        version (_type_): _description_
        target_column (_type_): _description_
        return_X_y (bool, optional): _description_. Defaults to True.
        as_frame (bool, optional): _description_. Defaults to False.
    """
    if name not in datasets:
        raise NameError("Dataset is not valid")
    maxver, fname = datasets[name]
    if version > maxver:
        raise NameError("Invalid version")

    fname+=f"{version}"
    data = pd.read_csv(f"{DATALINK}/{fname}.csv", header=0, delimiter=',',decimal='.')

    # Check if target column/columns exist
    if type(target_column) is not list:
        target_column = [target_column]

    for t in target_column:
        if t not in data.columns:
            raise NameError(f'Target column {t} invalid')  

    data_X = data.loc[:,~data.columns.isin(target_column)].copy()
    data_y = data.loc[:, target_column].copy()

    if return_X_y:
        return (data_X.to_numpy(), data_y.to_numpy())

    b = Bunch()
    b['data'] = data_X if as_frame else data_X.to_numpy()
    b['target'] = data_y if as_frame else data_y.to_numpy()
    b['feature_names'] = data_X.columns 
    b['target_names'] = data_y.columns 
    if as_frame:
        b['frame'] = data.copy()

    return b


def fetch_dataset(fname):
    return pd.read_csv(f"{DATALINK}/{fname}.csv", na_values="", sep=",", header=0)


def load_medical_costs():
    return fetch_dataset('stroke-data')

def load_stroke():
    return fetch_dataset('insurance')

def load_wind_prediction():
    return fetch_dataset('wind-dataset')

def load_BCN_IBEX():
    return fetch_dataset('BCNDiari2021-IBEX')

def load_BCN_UK():
    return fetch_dataset('BCNDiari2021-UK')

def load_BCN_vuelos():
    return fetch_dataset('BCNDiari2021-vuelos')

def load_titanic():
    return fetch_dataset('titanic')

def load_crabs():
    return fetch_dataset('crabs').drop(columns='index')

def load_life_expextancy():
    return fetch_dataset('Life_Expectancy_Data')






    