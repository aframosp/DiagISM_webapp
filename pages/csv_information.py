#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File explaining the structure of the input csv file
Run from python -m streamlit run main.py
@author: Andres Felipe Ramos Padilla
"""
import streamlit as st
import pandas as pd


def page():
    """Page for the web app explaining the CSV file"""
    example = pd.read_csv('files/example_input1.csv')
    example2 = pd.read_csv('files/example_input2.csv')

    st.write("""
    # CSV input format
    If you want to use a CSV instead of modifying the input values of the web app, you need to
    use a given format. The first column will be the redshift (z), with the value passed as 
    log(1+z). Then, you will find the luminosity columns, which will have the following names 
    depending on the luminosities you want to use.
    
    Columns: 'Lum_OIII_52',
    'Lum_NIII_57',
    'Lum_OI_63',
    'Lum_OIII_88',
    'Lum_NII_122',
    'Lum_OI_145',
    'Lum_CII_158',
    'Lum_NII_205'
               
    The units for the luminosities are in log(Lsun).
    
    ## CSV examples
    Here we show two examples of what we described before. First, we show how the .csv file will look
    when we know the luminosities for two lines (Example 1). Second, we show how the .csv file will
    look when there are missing values in the luminosity (Example 2). 
    We present both examples in plain text and as a pandas dataframe. 
    """)

    st.write("### Example 1")
    st.markdown("""
                ```csv
                z,Lum_OIII_88,Lum_CII_158
                0.47,6.0,6.0
                0.3,8.0,8.0
                0.1,8.0,8.0
                0,4.0,4.0
                ```
                """)
    st.write('As a pandas dataframe', example)

    st.write("### Example 2")
    st.markdown("""
                ```csv
                z,Lum_OIII_88,Lum_CII_158,Lum_OI_145
                0.47,,6.0,5.0
                0.3,8.0,8.0,7.0
                0.1,8.0,8.0,
                0,4.0,,5.0
                ```
                """)
    st.write('As a pandas dataframe', example2)
    
    st.markdown("""
    # CSV output format
    After obtaining the results of a given model, it is possible to save them in a CSV file. The CSV file contains information about the time, model used and score of the training. This information is present in the header of the file, which is easily readable in a text editor. In case you want to read the information systematically, we recommend the following codes: 
    ## [astropy (Python)](https://www.astropy.org/)
    ```python
    from astropy.table import Table
    Table.read('DiagISM_result.csv', format='ascii.csv', header_start=5)
    ```
    ## [pandas (Python)](https://pandas.pydata.org/)
    ```python
    import pandas as pd
    pd.read_csv('DiagISM_result.csv', header=5)
    ```
    ## [R](https://www.r-project.org/)
    ```R
    read.csv(file = 'DiagISM_result.csv', comment.char = '#')
    ```
    """)
