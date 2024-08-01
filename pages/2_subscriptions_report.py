import streamlit as st
import plost
import pandas as pd
import numpy as np
from datetime import datetime
from functions.setup_page import page_creation
import plotly.express as px

## Apply standard page settings.
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('Subscriptions Report')

## Define data and filters. The resulting data variable includes the data with all filters applied.
data = page_creation()

# Find the min and max of the created_at column
min_date = pd.to_datetime(data['created_at']).dt.to_period('M').min()
max_date = pd.to_datetime(data['created_at']).dt.to_period('M').max()

# Everything below this point will be generated by the assigned analyst. 
# The framework has been set, but no visualization or data processing has been applied.
# Please perform any data processing in this file and not within the filter files. We can discuss upon completion if it makes sense to add any code to the filters file.

# Convert payment_at to datetime if not already

data.loc[:, 'payment_at'] = pd.to_datetime(data['payment_at'])
data['payment_month'] = data['payment_at'].dt.to_period('M')
data['payment_quarter'] = data['payment_at'].dt.to_period('Q')
data['subscription_started_month'] = data['subscription_period_started_at'].dt.to_period('M')
data['subscription_started_quarter'] = data['subscription_period_started_at'].dt.to_period('Q')

# Filter the Dataframe to include only 'subscription' and 'recurring' billing types
subscription_data = data[
    (data['billing_type'].isin(['subscription', 'recurring'])) & 
    (data['transaction_type'] == 'sale')
]

# Filter the Dataframe to include only 'one-time' and 'invoiceitem' billing types
onetime_data = data[
    (data['billing_type'].isin(['one-time', 'invoiceitem'])) & 
    (data['transaction_type'] == 'sale')
]

# Active subscriptions data
active_subscriptions_data = subscription_data[subscription_data['subscription_status'] == 'active']

# Filter subscription_started_month to be within the min and max dates
new_subscriptions_data = active_subscriptions_data[
    (active_subscriptions_data['subscription_started_month'] >= min_date) &
    (active_subscriptions_data['subscription_started_month'] <= max_date)
]

# Group by 'payment_month' to calculate MRR and single order
mrr_data = subscription_data.groupby(subscription_data['payment_month'])['total_amount'].sum().sort_index()
single_order_data = onetime_data.groupby(onetime_data['payment_month'])['total_amount'].sum().sort_index()

## KPI Metrics which need to be updated.
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)

    # Total Revenue From Subscriptions
    with col1:
        current_total_revenue = subscription_data['total_amount'].sum()
        last_quarter_total_revenue = subscription_data[subscription_data['payment_month'].dt.quarter == (subscription_data['payment_month'].dt.quarter.max() - 1)]['total_amount'].sum()
        current_total_revenue_str = f'${current_total_revenue:,.2f}' if not pd.isna(current_total_revenue) else "no data"
        qoq_total_revenue = current_total_revenue - last_quarter_total_revenue
        qoq_total_revenue_str = f'{qoq_total_revenue:,.2f} QoQ' if not pd.isna(qoq_total_revenue) else "no data"
        st.metric(
            label="**Total Revenue From Subscriptions**", 
            value=current_total_revenue_str,
            delta=qoq_total_revenue_str  # Use conditional string
        )

    # Active Subscriptions
    with col2:
        current_active_subscriptions = active_subscriptions_data['subscription_status'].count()
        current_active_subscriptions_str = f'{current_active_subscriptions}' if not pd.isna(current_active_subscriptions) else "no data"
        last_quarter_active_subscriptions = active_subscriptions_data[
            (active_subscriptions_data['payment_month'].dt.quarter == (active_subscriptions_data['payment_month'].dt.quarter.max() - 1))
        ]['subscription_status'].count()
        qoq_active_subscriptions = current_active_subscriptions - last_quarter_active_subscriptions
        qoq_active_subscriptions_str = f'{qoq_active_subscriptions:,.0f} QoQ' if not pd.isna(qoq_active_subscriptions) else "no data"
        st.metric(
            label="**Active Subscriptions**", 
            value=current_active_subscriptions_str,
            delta=qoq_active_subscriptions_str  # Use conditional string
        )

    # New Subscriptions
    with col3:
        current_new_subscriptions = new_subscriptions_data['subscription_status'].count()
        current_new_subscriptions_str =  f'{current_new_subscriptions}' if not pd.isna(current_new_subscriptions) else "no data"
        last_quarter_new_subscriptions = new_subscriptions_data[
            new_subscriptions_data['payment_month'].dt.quarter == (new_subscriptions_data['payment_month'].dt.quarter.max() - 1)
        ]['subscription_status'].count()
        qoq_new_subscriptions = current_new_subscriptions - last_quarter_new_subscriptions
        qoq_new_subscriptions_str = f'{qoq_new_subscriptions:,.0f} QoQ' if not pd.isna(qoq_new_subscriptions) else "no data"
        st.metric(
            label="**New Subscriptions**", 
            value=current_new_subscriptions_str,
            delta=qoq_new_subscriptions_str  # Use conditional string
        )

    # Average Subscription Length (weeks)
    with col4:
        subscription_data['subscription_length_weeks'] = (subscription_data['subscription_period_ended_at'] - subscription_data['subscription_period_started_at']).dt.days / 7
        current_avg_subscription_length_weeks = subscription_data['subscription_length_weeks'].mean()
        current_avg_subscription_length_weeks_str = f"{current_avg_subscription_length_weeks:.1f}" if not pd.isna(current_avg_subscription_length_weeks) else "no data"
        last_quarter_avg_subscription_length_weeks = subscription_data[
            subscription_data['payment_month'].dt.quarter == (subscription_data['payment_month'].dt.quarter.max() - 1)
        ]
        if not last_quarter_avg_subscription_length_weeks.empty:
            last_quarter_avg_subscription_length_weeks = (last_quarter_avg_subscription_length_weeks['subscription_period_ended_at'] - last_quarter_avg_subscription_length_weeks['subscription_period_started_at']).dt.days / 7
            last_quarter_avg_subscription_length_weeks = last_quarter_avg_subscription_length_weeks.mean()
        else:
            last_quarter_avg_subscription_length_weeks = np.nan
        qoq_avg_subscription_length_weeks = current_avg_subscription_length_weeks - last_quarter_avg_subscription_length_weeks
        qoq_avg_subscription_length_weeks_str = f"{qoq_avg_subscription_length_weeks:.1f} QoQ" if not pd.isna(qoq_avg_subscription_length_weeks) else "no data"
        st.metric(
            label="**Average Subscription Length (weeks)**", 
            value=current_avg_subscription_length_weeks_str,
            delta=qoq_avg_subscription_length_weeks_str  # Use conditional string
        )

    # Most Recent Month MRR
    with col5:
        most_recent_mrr = mrr_data.iloc[-1] if not mrr_data.empty else 0
        most_recent_mrr_str = f"${most_recent_mrr:,.2f}" if not pd.isna(most_recent_mrr) else "no data"
        last_quarter_mrr = mrr_data.shift(3).iloc[-1] if not mrr_data.shift(3).empty else np.nan
        qoq_mrr = most_recent_mrr - last_quarter_mrr
        qoq_mrr_str = f"{qoq_mrr:,.2f} QoQ" if not pd.isna(qoq_mrr) else "no data"
        st.metric(
            label="**Most Recent Month MRR**", 
            value=most_recent_mrr_str,
            delta=qoq_mrr_str  # Use conditional string
        )

# Time series charts need to be built out
with st.container():
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        st.markdown("**Number of New Subscriptions**")

        # Filter subscription_started_month to be within the min and max dates
        new_subscriptions_data = active_subscriptions_data[
            (active_subscriptions_data['subscription_started_month'] >= min_date) &
            (active_subscriptions_data['subscription_started_month'] <= max_date)
        ]

        new_subscriptions_by_month = new_subscriptions_data.groupby('subscription_started_month').size()

        # Convert PeriodIndex to timestamp for better x-axis formatting
        new_subscriptions_by_month.index = new_subscriptions_by_month.index.to_timestamp()

        # Convert Series to DataFrame
        new_subscriptions_by_month = new_subscriptions_by_month.reset_index(name='count')
        new_subscriptions_by_month.rename(columns={'index': 'subscription_started_month'}, inplace=True)

        # Create a Plotly line chart
        fig1 = px.bar(new_subscriptions_by_month, x='subscription_started_month', y='count')

        # Set bar color
        fig1.update_traces(marker_color='#306BEA')

        # Update x and y labels
        fig1.update_layout(
            xaxis_title='',
            yaxis_title=''
        )

        # Streamlit plot chart
        st.plotly_chart(fig1)

    with row1_col2:
        st.markdown("**Number of New Subscriptions by Plan**")
        
        # Group by 'subscription_month' and 'subscription_plan'
        subscription_by_plan = new_subscriptions_data.groupby(['subscription_started_month', 'subscription_plan']).size().unstack(fill_value=0)
        
        # Convert PeriodIndex to datetime for better x-axis formatting
        subscription_by_plan.index = subscription_by_plan.index.to_timestamp()

        # Convert DataFrame for plotting
        subscription_by_plan_df = subscription_by_plan.reset_index()
        subscription_by_plan_df = pd.melt(subscription_by_plan_df, id_vars=['subscription_started_month'], var_name='subscription_plan', value_name='count')

        # Define custom colors
        color_sequence = ['#306BEA', '#9EA91F', '#DB6645', '#85B4FF', '#1E0C09']

        # Create a Plotly line chart
        fig2 = px.line(subscription_by_plan_df, x='subscription_started_month', y='count', color='subscription_plan', color_discrete_sequence=color_sequence)

        # Update x and y labels
        fig2.update_layout(
            xaxis_title='',
            yaxis_title='',
            legend_title_text='Subscription Plan'
        )

        # Streamlit plot chart
        st.plotly_chart(fig2)

    with row2_col1:
        st.markdown("**Subscription Revenue by Product Type**")
        
        # Group by 'subscription_month' and 'product_type', then sum total_amount
        revenue_by_product_type = new_subscriptions_data.groupby(['payment_month', 'product_type'])['total_amount'].sum().unstack(fill_value=0)
        
        # Convert PeriodIndex to datetime for better x-axis formatting
        revenue_by_product_type.index = revenue_by_product_type.index.to_timestamp()

        # Convert DataFrame for plotting
        revenue_by_product_type_df = revenue_by_product_type.reset_index()
        revenue_by_product_type_df = pd.melt(revenue_by_product_type_df, id_vars=['payment_month'], var_name='product_type', value_name='total_amount')

        # Create a Plotly line chart
        fig3 = px.line(revenue_by_product_type_df, x='payment_month', y='total_amount', color='product_type', color_discrete_sequence=color_sequence)

        # Suppress x and y labels
        fig3.update_layout(
            xaxis_title='',
            yaxis_title='',
            legend_title_text='Product Type'
        )

        # Streamlit plot chart
        st.plotly_chart(fig3)

    with row2_col2:
        st.markdown("**Subscription Revenue vs. Single Order Revenue**")

        # Convert PeriodIndex to datetime for better x-axis formatting
        mrr_data.index = mrr_data.index.to_timestamp()
        single_order_data.index = single_order_data.index.to_timestamp()

        # Align the data by reindexing both Series to have the same index
        combined_index = mrr_data.index.union(single_order_data.index)
        mrr_data = mrr_data.reindex(combined_index, fill_value=0)
        single_order_data = single_order_data.reindex(combined_index, fill_value=0)

        # Create DataFrame for plotting
        revenue_data = pd.DataFrame({
            'Date': combined_index,
            'Subscription Revenue': mrr_data.values,
            'Single Order Revenue': single_order_data.values
        })

        # Convert DataFrame for plotting
        revenue_data_melted = pd.melt(revenue_data, id_vars=['Date'], var_name='Revenue Type', value_name='Amount')

        # Create a Plotly line chart
        fig4 = px.line(revenue_data_melted, x='Date', y='Amount', color='Revenue Type', color_discrete_sequence=color_sequence)

        # Suppress x and y labels and change legend title
        fig4.update_layout(
            xaxis_title='',
            yaxis_title='',
            legend_title_text='Revenue Type'
        )

        # Streamlit plot chart
        st.plotly_chart(fig4)

st.divider()

st.markdown("**Raw Data**")
st.dataframe(data) ## This is here just as an example. This can be deleted during development and before release.

st.divider()