#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File to run the web app for DiagISM.
Run as python -m streamlit run main.py
@author: Andres Felipe Ramos Padilla
"""
import streamlit as st

from pages import reg_model2, reg_model8, csv_information

st.write("""
# DiagISM web app
This web app can help you to predict the ISM physical information of galaxies using 
FIR luminosities.
""")


def main():
    """
    Main is responsible for the visualisation of everything connected with streamlit.
    It is the web application itself.
    """

    # Sets sidebar's header and logo
#     st.sidebar_head()
#     st.image()

    analysis_type = st.sidebar.selectbox("Analysis models and information",
                                         ['Home', 'Model with selected FIR lines',
                                          'Model with 8 FIR Lines', 'CSV files information'])

    if analysis_type == 'Home':
        #         main_page.main_page()
        st.sidebar.write("""
        Select one of the models you want to execute
        """)
        st.markdown("""
        The information presented in this web app has been created with the research results
        presented in the
        **"Diagnosing the interstellar medium of galaxies with far-infrared emission lines"** 
        series of papers:
        
        * [I. The [C II] 158 microns line at z~0](https://ui.adsabs.harvard.edu/abs/2021A%26A...645A.133R)
        * [II. [C II], [O I], [O III], [N II] and [N III] up to z=6](https://ui.adsabs.harvard.edu/abs/2022arXiv220511955R)
        * [III. Physical parameters of observed galaxies (This web app, in prep.)]()
        
        Please acknowledge these papers if you have used this web app.""")

    if analysis_type == 'Model with selected FIR lines':
        reg_model2.page()
    elif analysis_type == 'Model with 8 FIR Lines':
        reg_model8.page()
    elif analysis_type == 'CSV files information':
        csv_information.page()
    st.warning(
        "This web app is still under construction. Predictions need some more testing.")
    st.write("""
        Andrés Felipe Ramos Padilla - May 2022.
        """)


if __name__ == '__main__':
    main()
    print("Streamlit finished it's work")
