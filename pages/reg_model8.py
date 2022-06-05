#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File to run the web app for DiagISM with the eight FIR lines model.
Run from python -m streamlit run main.py
@author: Andres Felipe Ramos Padilla
"""
import time
import pickle
from datetime import datetime, timezone

import streamlit as st

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from astropy.table import Table
from astropy.visualization import hist

from sklearn import preprocessing

from pages.defs import user_input_features, user_parameter, create_mocks, convert_df


def page():
    """Page for the web app of the model with eight FIR lines"""
    
    st.markdown("""
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 25rem;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    width: 25rem;
    margin-left: -25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.write("""
    # Predictions from the DiagISM model with eight FIR lines
    In this analysis, we predict a given physical parameter of a galaxy with the information
    of the eight FIR line luminosities.
    Pay attention to the score (Coefficient of determination R$^2$) as it may indicate that for 
    a given parameter the predictions may not be ideal.
    """)

    dataset = Table.read('files/complete_dataset.fits', format='fits')
    dataset['log(1+z)'] = np.log10(dataset['z']+1)

    st.sidebar.header('User input parameters')
    st.sidebar.write("""Select the values for the parameters or upload a CSV file. Luminosities are in log(Lsun) units,
    described as Lum_LINE where the number is the wavelength of emission in microns.""")

    dict_conv = {'Lum_OIII_52': 'L$_{\\mathrm{OIII_{52}}}$',
                 'Lum_NIII_57': 'L$_{\\mathrm{NIII_{57}}}$',
                 'Lum_OI_63': 'L$_{\\mathrm{OI_{63}}}$',
                 'Lum_OIII_88': 'L$_{\\mathrm{OIII_{88}}}$',
                 'Lum_NII_122': 'L$_{\\mathrm{NII_{122}}}$',
                 'Lum_OI_145': 'L$_{\\mathrm{OI_{145}}}$',
                 'Lum_CII_158': 'L$_{\\mathrm{CII}}$',
                 'Lum_NII_205': 'L$_{\\mathrm{NII_{205}}}$',
                 'z': 'log(1+z)'}

    df_user = user_input_features()

    uploaded_file = st.sidebar.file_uploader("Upload a CSV file instead",
                                             accept_multiple_files=False,
                                             type='csv')
    if uploaded_file is not None:
        df_user = pd.read_csv(uploaded_file)

    col_analt = ['L$_{\\mathrm{OIII_{52}}}$',
                 'L$_{\\mathrm{NIII_{57}}}$',
                 'L$_{\\mathrm{OI_{63}}}$',
                 'L$_{\\mathrm{OIII_{88}}}$',
                 'L$_{\\mathrm{NII_{122}}}$',
                 'L$_{\\mathrm{OI_{145}}}$',
                 'L$_{\\mathrm{CII}}$',
                 'L$_{\\mathrm{NII_{205}}}$',
                 'log(1+z)']

    try:
        listc = [dict_conv[col] for col in df_user.columns]
    except KeyError:
        e = KeyError('Column names are not correct, check the CSV information')
        st.exception(e)

    for icol, col in enumerate(dict_conv):
        if col in df_user.columns:
#             print(df_user[col])
            content = df_user[[col]]
            df_user.drop([col], inplace=True, axis=1)
        else:
            content = np.nan
        df_user.insert(icol, col, content)
    df_user.rename(columns={"z": "log(1+z)"}, inplace=True)
    st.write('Current user input physical parameters', df_user)

    if 'log(1+z)' not in listc:
        st.warning('Note that you are not using the redshift dimension.')

    if len(listc) < 3:
        st.warning('We recommend the use of two emission lines and the redshift.')

    if len(listc) == 1:
        st.error('One input is not enough to give you reliable information.')
        st.stop()

    dict_par = {'SFR': 'SFR',
                'ISRF': 'ISRF',
                'Metallicity': 'ZGal',
                'Pressure': 'Pressure',
                'Density': r'n$(\mathrm{H})_{\mathrm{cloud}}$',
                'Stellar Mass': r'M$_{\mathrm{\ast}}$',
                'Gas Mass': r'M$_{\mathrm{gas}}$',
                'Neutral cloud size': r'R$_{\mathrm{cloud}}$'}
    test_param = user_parameter()
    param_unit = dataset[dict_par[test_param[0]]].unit
    x_df = dataset[col_analt].to_pandas()
    y_df = dataset.to_pandas()[dict_par[test_param[0]]].values.reshape(-1, 1)

    scalerx = preprocessing.RobustScaler()
    scalery = preprocessing.RobustScaler()
    x_scale = scalerx.fit_transform(x_df)
    y_scale = scalery.fit_transform(y_df)

    st.write('Physical parameter to be predicted: ', test_param[0])

    start_time = time.time()
    hyp_tab = Table.read('files/Hyperparameters_table.csv', format='ascii.csv')
    loc_hyp = np.where(hyp_tab['Parameter'] == dict_par[test_param[0]])[0][0]
    regr_mlp_list = pickle.load(open('files/AllLines_trained', 'rb'))
    regr_mlp = regr_mlp_list[loc_hyp]

    def user_score():
        """ Score of the predictions for the selected parameters"""
        score_mlp = regr_mlp.score(x_scale, y_scale)
        st.write('Score of the predictions: %1.3f' % score_mlp)
        if score_mlp <= 0.7:
            st.error(
                'The score is not good enough to make a prediction with this parameter')
            st.stop()
        if np.logical_and(score_mlp > 0.7, score_mlp < 0.9):
            st.warning(
                'Score for this parameter may not be the best for the prediction.')
        return score_mlp

    score = user_score()
    df_np = df_user.to_numpy()
    faked = create_mocks(df_np, x_df)
#     st.write("Create mocks took", time.time() - start_time, "to run")
#     st.write('Faked data', faked)
    param_data = []
    for gal in range(faked.shape[0]):
        faked_scale = scalerx.transform(faked[gal])
        individual = regr_mlp.predict(faked_scale)
        trans_indiv = scalery.inverse_transform(individual.reshape(-1, 1))
        fin_mean = np.mean(trans_indiv)
        fin_std = np.std(trans_indiv)
        fin_med = np.median(trans_indiv)
        fin_84 = np.quantile(trans_indiv, 0.84)
        fin_16 = np.quantile(trans_indiv, 0.16)
        if gal <10:
            fig = plt.figure()
            hist(trans_indiv,  density=True, bins='scott', histtype='step')
            plt.axvline(x=fin_med, c='C1', label='median')
            plt.axvline(x=fin_mean, c='C1', ls='--', label='mean')
            plt.axvline(x=fin_84, c='C2', label='16th and 84th percentiles')
            plt.axvline(x=fin_16, c='C2')
            plt.xlabel('Estimated parameter value [%s]' % param_unit)
            plt.ylabel('Density')
            plt.legend(fontsize=8)
            plt.title('Galaxy %i' % gal)
            st.pyplot(fig)
        if gal ==11:
            st.info('Plotting only the first ten galaxies')
        int_data = {"per_16th": fin_16, "median": fin_med, "per_84th": fin_84,
                    "mean": fin_mean, "std": fin_std}
        int_output = pd.DataFrame(int_data, index=[gal])
        param_data.append(int_output)
    final_output = pd.concat(param_data)
    st.write(final_output)
    st.success('Results obtained!')
    st.write("Results took", np.round(
        time.time() - start_time, 2), "[s] to run")
    csv = convert_df(final_output)
    h_row1 = b'# Predictions obtained from DiagISM \n'
    h_row2 = bytes('# Date execution time: %s UTC \n' %
                   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                   'utf-8')
    h_row3 = bytes('# Predicted physical parameter: %s [%s]\n' % (
        test_param[0], param_unit), 'utf-8')
    h_row4 = b'# The score of the predictions was: %.3f \n' % score
    h_row5 = b'# Model: Eight FIR lines \n'
    header = h_row1 + h_row2 + h_row3 + h_row4 + h_row5
    csv = header + csv
    _, col2, _ = st.columns(3)
    col2.download_button(
        label="Download results as CSV",
        data=csv,
        file_name='DiagISM_result.csv',
        mime='text/csv',
    )
