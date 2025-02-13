# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 17:47:06 2024

@author: GONGR067
"""
import sys
import os
sys.path.append(r'./scripts')

import streamlit as st
print(sys.path)
print(os.getcwd())
def start():
    pages = {
        "Engines Excitation": [
            st.Page("scripts/Plot_engine_excitation.py", title="Plot excitation"),
            st.Page("scripts/Engine_RPM_analysis_V01.py", title="RPM analysis"),
        ],
        "Others": [
            st.Page("scripts/Thermal_shock_data_analysis.py", title="Thermal shock data analysis"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == '__main__':
    start()