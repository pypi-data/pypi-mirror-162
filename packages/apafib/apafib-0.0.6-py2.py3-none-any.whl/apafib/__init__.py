"""
.. module:: __init__.py

__init__.py
*************

:Description: __init__.py


:Authors: bejar
    

:Version: 

:Created on: 06/05/2022 10:53 

"""

from apafib.datasets import fetch_apa_data, load_BCN_IBEX, load_BCN_UK, load_BCN_vuelos, \
     load_medical_costs, load_stroke, load_wind_prediction, load_titanic, load_crabs, \
          load_life_expectancy 

from apafib.classifiers import BlackBoxClassifier, BlackBoxRegressor

__version__ = '0.0.6'

__all__ = ['fetch_apa_data', 
           'BlackBoxClassifier', 
           'BlackBoxRegressor',
           'load_BCN_IBEX',
           'load_BCN_UK',
           'load_BCN_vuelos',
           'load_medical_costs',
           'load_wind_prediction',
           'load_stroke',
           'load_titanic',
           'load_crabs',
           'load_life_expectancy'

           ]