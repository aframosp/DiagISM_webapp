#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the definitions for the web app for DiagISM.
@author: Andres Felipe Ramos Padilla
"""
import streamlit as st
import numpy as np
import pandas as pd

def user_input_features():
    """Obtaining user defined values"""
    reds = st.sidebar.slider('Redshift', 0, 6, 2)
    col1, col2 = st.sidebar.columns(2)
    lum_oiii52 = col1.number_input('Lum_OIII_52', 3.0, 11.0, 6.0, 0.1)
    lum_niii57 = col1.number_input('Lum_NIII_57', 3.0, 11.0, 6.0, 0.1)
    lum_oi63 = col1.number_input('Lum_OI_63', 3.0, 11.0, 6.0, 0.1)
    lum_oiii88 = col1.number_input('Lum_OIII_88', 3.0, 11.0, 6.0, 0.1)
    lum_nii122 = col2.number_input('Lum_NII_122', 3.0, 11.0, 6.0, 0.1)
    lum_oi145 = col2.number_input('Lum_OI_145', 3.0, 11.0, 6.0, 0.1)
    lum_cii = col2.number_input('Lum_CII_158', 3.0, 11.0, 6.0, 0.1)
    lum_nii205 = col2.number_input('Lum_NII_205', 3.0, 11.0, 6.0, 0.1)
    data = {'z': np.log10(1+reds),
            'Lum_OIII_52': lum_oiii52,
            'Lum_NIII_57': lum_niii57,
            'Lum_OI_63': lum_oi63,
            'Lum_OIII_88': lum_oiii88,
            'Lum_NII_122': lum_nii122,
            'Lum_OI_145': lum_oi145,
            'Lum_CII_158': lum_cii,
            'Lum_NII_205': lum_nii205
            }
    options = st.sidebar.multiselect(
        'Parameters to train the model',
        ['z', 'Lum_OIII_52', 'Lum_NIII_57', 'Lum_OI_63', 'Lum_OIII_88',
         'Lum_NII_122', 'Lum_OI_145', 'Lum_CII_158', 'Lum_NII_205'],
        ['z', 'Lum_OIII_88', 'Lum_CII_158'])
    return pd.DataFrame(data, index=['User values'])[options]


def user_parameter():
    """Obtaining user defined parameters"""
    options = st.sidebar.multiselect(
        'Parameter to predict',
        ['SFR', 'ISRF', 'Metallicity', 'Pressure', 'Density',
         'Neutral cloud size', 'Gas Mass', 'Stellar Mass'],
        ['SFR'])
    if len(options) > 1:
        st.error('(Currently) Only one parameter can be predicted at a time.')
        st.stop()
    if len(options) < 1:
        st.sidebar.error('Choose at least one parameter')
        st.stop()
    return options


def create_mocks(values, features, sys_error=False):
    """Create mock values to estimate the error on the prediction"""
    if sys_error:
        sigma = 0.5
    else:
        sigma = st.sidebar.slider('Assumed error [dex]', 0.05, 1.0, 0.5, 0.05)
    nlines = values.shape[1]
    np.random.seed(42)
    nrows = 2000
    rows = np.zeros((values.shape[0], nrows, nlines))
    for igal in range(values.shape[0]):
        loc_cols = np.unique(np.where(~np.isnan(values[igal]))[0])[:-1]
        cond1 = (features[features.columns[loc_cols]] <= values[igal][loc_cols]+sigma).all(axis=1)
        cond2 = (features[features.columns[loc_cols]] >= values[igal][loc_cols]-sigma).all(axis=1)
        info = features[cond1 & cond2].describe()
        if info.isnull().values.any():
            st.write("""No luminosity values in the simulation similar to the input,
                     increase the sigma if prefered. Other way we use the average of the input.""")
            bad_sol = pd.DataFrame([values[igal]]).describe()
            bad_sol.loc['mean'] = np.nanmean(values[igal][:-1])
            info = bad_sol
            st.write(info)
        for col in range(nlines):
            rand_lum = np.random.normal(info.loc['mean'][col], sigma, nrows)
            if ~np.isnan(values[igal][col]):
                if col == nlines-1:
                    # Redshift does not change
                    rows[igal, :, col] = values[igal][col]
                else:
                    if sys_error:
                        rows[igal, :, col] = np.random.normal(
                            values[igal][col], 0.2, nrows)
                    else:
                        rows[igal, :, col] = np.random.normal(
                            values[igal][col], 0.01, nrows)
            else:
                rows[igal, :, col] = rand_lum
    return rows


@st.cache
def convert_df(dataframe):
    """Convert dataframe to csv file"""
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    head_inf = "The data was generated in DiagSIM with ..."
    return dataframe.to_csv(header=head_inf, index_label='id').encode('utf-8')
