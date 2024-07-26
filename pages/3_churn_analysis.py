import streamlit as st
import plost
import pandas as pd
import numpy as np
from datetime import datetime
from functions.setup_page import page_creation

## Apply standard page settings.
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('Churn Analysis')

## Define data and filters. The resulting data variable includes the data with all filters applied.
data = page_creation()

st.divider()

st.dataframe(data.head(10)) ## This is here just as an example. This can be deleted during development and before release.

st.divider()

# Everything below this point will be generated by the assigned analyst. 
# The framework has been set, but no visualization or data processing has been applied.
# Please perform any data processing in this file and not within the filter files. We can discuss upon completion if it makes sense to add any code to the filters file.

## KPI Metrics which need to be updated.
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="**New MRR**", value="TBD")

    with col2:
        st.metric(label="**Churned MRR**", value="TBD")

    with col3:
        st.metric(label="**30 Day Retention Rate**", value="TBD")

    with col4:
        st.metric(label="**90 Day Retention Rate**", value="TBD")

    with col5:
        st.metric(label="**1 Year Retention Rate**", value="TBD")

# Time series charts need to be built out
with st.container():
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown("**Churn Rate**")

    with row1_col2:
        st.markdown("**Churn Rate by Subscription by Plan**")

## Cohort Analysis Chart
st.markdown("**Cohort Analysis**")

## New MRR by Type
st.markdown("**New MRR by Type**")