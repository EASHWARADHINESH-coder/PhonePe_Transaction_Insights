# IMPORT LIBRARIES

import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# PAGE CONFIG

st.set_page_config(page_title="PhonePe Insights", layout="wide")
st.title("📊 PhonePe Transaction Insights Dashboard")

# DATABASE CONNECTION

@st.cache_resource
def get_engine():
    try:
        engine = create_engine(
            f"mysql+pymysql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@{st.secrets['DB_HOST']}/{st.secrets['DB_NAME']}",
            pool_pre_ping=True
        )

        # Force a real connection test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return engine

    except Exception as e:
        st.error("Database connection failed. Check DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, and whether the MySQL server allows external connections.")
        st.exception(e)
        st.stop()

engine = get_engine()

# SIDEBAR NAVIGATION

st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Page",
    ["Home", "Decoding Transaction Dynamics on PhonePe", 
     "Device Dominance and User Engagement Analysis", 
     "Insurance Penetration and Growth Potential Analysis", 
     "Transaction Analysis for Market Expansion", 
     "User Engagement and Growth Strategy", 
     #"Insurance Engagement Analysis", 
     #"Transaction Analysis Across States and Districts", 
     #"User Registration Analysis", 
     #"Insurance Transactions Analysis"
    ]
)

# FUNCTION TO FORMAT STATE NAME

def format_state_name(state):
    return state.replace("-", " ").replace("&", " & ").title()

# HOME PAGE

if page == "Home":

    st.subheader("PhonePe Data Analysis")
    st.write("""
This dashboard analyzes PhonePe digital payment data across India.

Features:
- State wise transaction analysis
- Transaction type comparison
- Transaction amount insights
- Interactive charts
""")

    st.markdown("---")
    st.subheader("PhonePe Transaction Heatmap Across India")
    st.write("""
This visualization shows the geographic distribution of PhonePe transactions across different states in India.

Features:
- Highlights states with the highest digital payment activity
- Identifies regions with growing transaction adoption
- Displays transaction concentration using a color intensity scale
- Helps detect potential markets for future expansion

Insight:
States with darker colors indicate higher transaction volumes, showing strong PhonePe adoption and active digital payment usage.
""")
    
    query = text("""
    SELECT 
    state,
    SUM(transaction_count) AS total_transactions
    FROM aggregated_transactions
    GROUP BY state
    """)

    df = pd.read_sql(query, engine)

    df["state"] = df["state"].str.replace("-", " ").str.title()

    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    
    fig = px.choropleth(
        df,
        geojson=geojson_url,
        featureidkey="properties.ST_NM",
        locations="state",
        color="total_transactions",
        color_continuous_scale="Reds",
        title="PhonePe Transaction Distribution Across India"
    )

    fig.update_layout(
        height=700
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("PhonePe User Distribution Across India")
    st.write("""
This visualization displays the distribution of registered PhonePe users across different states in India.

Features:
- Shows the number of registered PhonePe users in each state
- Highlights regions with strong user adoption
- Uses color intensity to represent user concentration across states
- Provides a quick overview of PhonePe’s user base distribution

Insight:
States with darker shades indicate a higher number of registered users, reflecting strong adoption of PhonePe services and greater digital payment penetration in those regions.
""")

    query_users = text("""
    SELECT 
    state,
    SUM(registeredUsers) AS total_users
    FROM aggregated_users
    GROUP BY state
    """)

    df_users = pd.read_sql(query_users, engine)

    df_users["state"] = df_users["state"].str.replace("-", " ").str.title()

    fig2 = px.choropleth(
        df_users,
        geojson=geojson_url,
        featureidkey="properties.ST_NM",
        locations="state",
        color="total_users",
        color_continuous_scale="Blues",
        title="PhonePe Registered Users Distribution"
    )

    fig2.update_layout(height=700)

    fig2.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("PhonePe Insurance Distribution Across India")
    st.write("""
This visualization shows the distribution of PhonePe insurance transactions across different states in India.

Features:
- Displays the number of insurance transactions performed through PhonePe
- Highlights states with higher insurance adoption
- Uses color intensity to represent the concentration of insurance transactions
- Helps identify regions where digital insurance services are widely used

Insight:
States with darker green shades indicate higher insurance transaction activity, showing stronger adoption of digital insurance services through PhonePe. Lighter regions highlight potential markets where insurance penetration can grow further.
""")

    query_ins = text("""
    SELECT 
    state,
    SUM(insurance_count) AS total_insurance
    FROM aggregated_insurance
    GROUP BY state
    """)

    df_ins = pd.read_sql(query_ins, engine)

    df_ins["state"] = df_ins["state"].str.replace("-", " ").str.title()

    fig3 = px.choropleth(
        df_ins,
        geojson=geojson_url,
        featureidkey="properties.ST_NM",
        locations="state",
        color="total_insurance",
        color_continuous_scale="Greens",
        title="PhonePe Insurance Transactions Distribution"
    )

    fig3.update_layout(height=700)

    fig3.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(fig3, use_container_width=True)

# AGGREGATED TRANSACTIONS

elif page == "Decoding Transaction Dynamics on PhonePe":

    st.header("Decoding Transaction Dynamics on PhonePe")

    query_states = """
    SELECT DISTINCT state 
    FROM aggregated_transactions 
    ORDER BY state
    """

    states_df = pd.read_sql(query_states, engine)
    states_df["display_state"] = states_df["state"].apply(format_state_name)
    state_dict = dict(zip(states_df["display_state"], states_df["state"]))

    selected_display_state = st.selectbox(
        "Select State",
        states_df["display_state"]
    )

    selected_state = state_dict[selected_display_state]
    st.write(f"Selected State: {selected_display_state}")

    # STATE DATA QUERY

    query = text("""
    SELECT transaction_type,
    SUM(transaction_count) AS total_transactions,
    SUM(transaction_amount) AS total_amount
    FROM aggregated_transactions
    WHERE state = :state_name
    GROUP BY transaction_type
    """)

    state_data = pd.read_sql(query, engine, params={"state_name": selected_state})
    
    if not state_data.empty:

        state_data["total_transactions"] = pd.to_numeric(state_data["total_transactions"])
        state_data["total_amount"] = pd.to_numeric(state_data["total_amount"])

        state_data["total_transactions"] = state_data["total_transactions"] / 1_000_000
        state_data["total_amount"] = state_data["total_amount"] / 1_000_000

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Transactions (Millions)",
            f"{state_data['total_transactions'].sum():.2f}"
        )

        col2.metric(
            "Total Amount (Millions)",
            f"₹ {state_data['total_amount'].sum():.2f}"
        )

        st.markdown("---")
        st.subheader("1.Comparison between Transaction Count and Transaction Amount by Transaction Type")
        st.write("""
This section analyzes how different types of transactions are performed on PhonePe across Indian states.

Features:
- Allows users to select a specific state for detailed analysis
- Compares transaction counts across different transaction categories
- Shows the total transaction amount for each transaction type
- Provides a side-by-side comparison of transaction volume and value

Insight:
By comparing transaction count and transaction amount, we can identify which services are used most frequently and which generate higher transaction value. This helps understand user payment behavior and highlights the most popular transaction categories on PhonePe.
""")

        # CHARTS
        col1, col2 = st.columns(2)

        # Transaction Count Chart
        with col1:

            fig1 = px.bar(
                state_data,
                x="transaction_type",
                y="total_transactions",
                color="transaction_type",
                text="total_transactions",
                title="Transaction Count Distribution"
            )

            fig1.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside'
            )

            fig1.update_layout(xaxis_tickangle=-30)

            st.plotly_chart(fig1, use_container_width=True)

        # Transaction Amount Chart
        with col2:

            fig2 = px.bar(
                state_data,
                x="transaction_type",
                y="total_amount",
                color="transaction_type",
                text="total_amount",
                title="Transaction Amount Distribution"
            )

            fig2.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside'
            )

            fig2.update_layout(xaxis_tickangle=-30)

            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("2.Transaction and Amount Share by Transaction Type")
        st.write("""
This section illustrates how different transaction categories contribute to the overall transaction activity on PhonePe.

Features:
- Displays the proportion of transaction counts across different transaction types
- Shows the share of total transaction amount generated by each category
- Helps compare transaction frequency versus transaction value
- Provides a clear view of dominant payment services used by PhonePe users

Insight:
The transaction share chart highlights which services are used most frequently, while the amount share chart reveals which transaction categories generate the highest monetary value. This helps identify key revenue-driving services and popular payment behaviors among users.
""")

        fig3 = px.pie(
            state_data,
            names="transaction_type",
            values="total_transactions",
            title="Transaction Share by Type"
        )

        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.pie(
            state_data,
            names="transaction_type",
            values="total_amount",
            title="Amount Share by Type"
        )

        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.subheader("3.Year-wise Growth Analysis")
        st.write("""
This section analyzes how PhonePe transactions have grown over the years in the selected state.

Features:
- Displays the yearly growth of total transaction counts
- Shows how the total transaction amount has increased over time
- Provides a breakdown of transaction volume by transaction type across years
- Uses line, bar, and area charts for better trend analysis

Insight:
The yearly growth charts help identify trends in digital payment adoption. Increasing transaction counts indicate rising user activity, while growth in transaction amount reflects higher financial value processed through PhonePe. The transaction type breakdown highlights which payment services are driving growth over time.
""")
        
        query = text("""
        SELECT year,
        transaction_type,
        SUM(transaction_count) AS total_transactions,
        SUM(transaction_amount) AS total_amount
        FROM aggregated_transactions
        WHERE state = :state_name
        GROUP BY year, transaction_type
        ORDER BY year
        """)
        
        state_data = pd.read_sql(query, engine, params={"state_name": selected_state})
        
        # DATATYPE CONVERSION
        
        state_data["year"] = pd.to_numeric(state_data["year"])
        state_data["total_transactions"] = pd.to_numeric(state_data["total_transactions"])
        state_data["total_amount"] = pd.to_numeric(state_data["total_amount"])
        
        # YEARLY AGGREGATION
        
        yearly_data = state_data.groupby("year").agg({
            "total_transactions": "sum",
            "total_amount": "sum"
        }).reset_index()
        
        yearly_data["total_transactions"] = yearly_data["total_transactions"] / 1_000_000
        yearly_data["total_amount"] = yearly_data["total_amount"] / 1_000_000
        
        col5, col6 = st.columns(2)
        
        # Line Chart – Transaction Growth
        
        with col5:
            
            fig5 = px.line(
                yearly_data,
                x="year",
                y="total_transactions",
                title="Yearly Transaction Growth",
                markers=True
            )
            
            st.plotly_chart(fig5, use_container_width=True)
            
        # Bar Chart – Amount Growth
            
        with col6:
            
            fig6 = px.bar(
                yearly_data,
                x="year",
                y="total_amount",
                title="Yearly Amount Growth"
            )
                
            st.plotly_chart(fig6, use_container_width=True)
            st.write("#### Yearly Breakdown by Transaction Type")
            
            state_data["total_transactions"] = state_data["total_transactions"] / 1_000_000

        fig7 = px.area(
            state_data,
            x="year",
            y="total_transactions",
            color="transaction_type",
            title="Transaction Type Volume Over Years",
            labels={"total_transactions": "Millions"}
        )
        
        st.plotly_chart(fig7, use_container_width=True)

        st.markdown("---")
        st.subheader("4.Quarter-wise Growth Analysis")
        st.write("""
This section examines the quarterly trends in PhonePe transactions for the selected state.

Features:
- Shows how transaction counts change across quarters
- Displays the growth of total transaction amount quarter by quarter
- Compares quarterly performance across different years
- Provides a breakdown of transaction types to identify seasonal usage patterns

Insight:
Quarter-wise analysis helps identify short-term fluctuations and seasonal patterns in digital payment activity. Rising transaction counts across quarters indicate increasing adoption, while variations between quarters may reflect festive seasons, promotional campaigns, or changes in consumer spending behavior.
""")

        query = text("""
        SELECT year,
        quarter,
        transaction_type,
        SUM(transaction_count) AS total_transactions,
        SUM(transaction_amount) AS total_amount
        FROM aggregated_transactions
        WHERE state = :state_name
        GROUP BY year, quarter, transaction_type
        ORDER BY year, quarter
        """)

        state_data = pd.read_sql(query, engine, params={"state_name": selected_state})

        # DATATYPE CONVERSION
        
        state_data["year"] = pd.to_numeric(state_data["year"])
        state_data["quarter"] = pd.to_numeric(state_data["quarter"])
        state_data["total_transactions"] = pd.to_numeric(state_data["total_transactions"])
        state_data["total_amount"] = pd.to_numeric(state_data["total_amount"])
        
        # QUARTERLY AGGREGATION
        
        quarterly_data = state_data.groupby(["year", "quarter"]).agg({
            "total_transactions": "sum",
            "total_amount": "sum"
        }).reset_index()
        
        quarterly_data["total_transactions"] = quarterly_data["total_transactions"] / 1_000_000
        quarterly_data["total_amount"] = quarterly_data["total_amount"] / 1_000_000
        
        col8, col9 = st.columns(2)

        # Line Chart – Transaction Growth
        
        with col8:
            
            fig8 = px.line(
                quarterly_data,
                x="quarter",
                y="total_transactions",
                color="year",
                markers=True,
                title="Quarterly Transaction Growth by Year"
            )
            
            st.plotly_chart(fig8, use_container_width=True)
            
        # Bar Chart – Amount Growth
            
        with col9:
            
            fig9 = px.bar(
                quarterly_data,
                x="quarter",
                y="total_amount",
                color="year",
                barmode="group",
                title="Quarterly Amount Growth by Year"
            )
                
            st.plotly_chart(fig9, use_container_width=True)
            st.write("#### Quarterly Breakdown by Transaction Type")

            state_data["total_transactions"] = state_data["total_transactions"] / 1_000_000
            
        fig10 = px.area(
            state_data,
            x="quarter",
            y="total_transactions",
            color="transaction_type",
            title="Transaction Type Volume by Quarter and Year",
            facet_col="year",
            labels={"total_transactions": "Transactions (Millions)", "period": "Time Period"}
        )
            
        st.plotly_chart(fig10, use_container_width=True)

        st.markdown("---")
        st.subheader("5.Top 10 Transactions and Amount across States and Years")
        st.write("""
This section highlights the top-performing states on PhonePe based on transaction volume and transaction value for the selected year.

Features:
- Allows users to select a specific year for analysis
- Displays the top 10 states with the highest number of transactions
- Shows the top 10 states generating the highest transaction amount
- Uses horizontal bar charts to easily compare state performance

Insight:
The charts reveal which states contribute the most to PhonePe's transaction activity and revenue generation. High transaction counts indicate strong user engagement, while high transaction amounts highlight regions with larger financial flows through the platform.
""")

        query = text("""
        SELECT state,
        year,
        SUM(transaction_count) AS total_transactions,
        SUM(transaction_amount) AS total_amount
        FROM aggregated_transactions
        GROUP BY state, year
        """)

        top_state_data = pd.read_sql(query, engine)
        
        top_state_data["total_transactions"] = pd.to_numeric(top_state_data["total_transactions"])
        top_state_data["total_amount"] = pd.to_numeric(top_state_data["total_amount"])

        selected_year = st.selectbox(
            "Select Year",
            sorted(top_state_data["year"].unique())
        )
        
        filtered_data = top_state_data[top_state_data["year"] == selected_year]

        top_transactions = filtered_data.nlargest(10, "total_transactions")
        top_amount = filtered_data.nlargest(10, "total_amount")
        
        # convert to millions
        top_transactions["total_transactions"] = top_transactions["total_transactions"] / 1_000_000
        top_amount["total_amount"] = top_amount["total_amount"] / 1_000_000

        col11, col12 = st.columns(2)
        
        # Top Transactions Chart
        with col11:
            fig11 = px.bar(
                top_transactions,
                x="total_transactions",
                y="state",
                orientation="h",
                color="state",
                title=f"Top 10 States by Transactions (Q{selected_year})"
            )
            
            fig11.update_layout(yaxis=dict(categoryorder="total ascending"))
            
            st.plotly_chart(fig11, use_container_width=True)
            
            # Top Amount Chart
            with col12:
                fig12 = px.bar(
                    top_amount,
                    x="total_amount",
                    y="state",
                    orientation="h",color="state",
                    title=f"Top 10 States by Amount (Q{selected_year})"
                )
                
                fig12.update_layout(yaxis=dict(categoryorder="total ascending"))
                
                st.plotly_chart(fig12, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# AGGREGATED USERS

# FUNCTION TO FORMAT STATE NAME
def format_state_name(state):
    return state.replace("-", " ").replace("&", " & ").title()


# HOME PAGE
if page == "Home":

    st.subheader("")


# DEVICE DOMINANCE PAGE
elif page == "Device Dominance and User Engagement Analysis":

    st.header("Device Dominance and User Engagement Analysis")

    # ----------------------------
    # SQL QUERY
    # ----------------------------
    query = text("""
    SELECT state,
           year,
           quarter,
           brand,
           brand_users
    FROM aggregated_users
    """)

    brand_data = pd.read_sql(query, engine)

    # ----------------------------
    # Fix Data Types
    # ----------------------------
    brand_data["brand_users"] = pd.to_numeric(brand_data["brand_users"], errors="coerce")
    brand_data["year"] = pd.to_numeric(brand_data["year"], errors="coerce")
    brand_data["quarter"] = pd.to_numeric(brand_data["quarter"], errors="coerce")

    # ----------------------------
    # Format State Names
    # ----------------------------
    brand_data["state_display"] = brand_data["state"].apply(format_state_name)

    # ----------------------------
    # FILTERS
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_state_display = st.selectbox(
            "Select State",
            sorted(brand_data["state_display"].unique())
        )

    selected_state = brand_data.loc[
        brand_data["state_display"] == selected_state_display, "state"
    ].iloc[0]

    with col2:
        selected_year = st.selectbox(
            "Select Year",
            sorted(brand_data["year"].unique())
        )

    with col3:
        selected_quarter = st.selectbox(
            "Select Quarter",
            sorted(brand_data["quarter"].unique())
        )

    # ----------------------------
    # FILTER DATA
    # ----------------------------
    filtered_data = brand_data[
        (brand_data["state"] == selected_state) &
        (brand_data["year"] == selected_year) &
        (brand_data["quarter"] == selected_quarter)
    ]

    # ----------------------------
    # AGGREGATE BRAND DATA
    # ----------------------------
    brand_summary = (
        filtered_data.groupby("brand", as_index=False)["brand_users"]
        .sum()
    )

    # ----------------------------
    # TOP 5 BRANDS
    # ----------------------------
    top_brands = brand_summary.nlargest(5, "brand_users").copy()

    # Convert to millions
    top_brands["brand_users"] = top_brands["brand_users"] / 1000

    labels={
    "brand_users": "Brand Users (Thousands)",
    "brand": "Mobile Brand"
    }

    # ----------------------------
    # CHART
    # ----------------------------
    st.markdown("---")
    st.subheader("1.Top 5 Mobile Brands by Brand Users")
    st.write("""
This chart highlights the most popular mobile device brands used by PhonePe users in the selected state and time period.

Features:
- Displays the top 5 mobile brands based on the number of PhonePe users
- Allows comparison of device popularity across users
- Uses a horizontal bar chart for easy ranking visualization
- Shows brand user counts for the selected year and quarter

Insight:
The chart reveals which mobile brands dominate the PhonePe user base in the selected region. Higher user counts indicate greater device penetration and compatibility with digital payment services, helping understand device preferences among PhonePe users.
""")

    fig1 = px.bar(
        top_brands,
        x="brand_users",
        y="brand",
        orientation="h",
        color="brand",
        text="brand_users",
        title=f"Top 5 Mobile Brands in {selected_state_display} ({selected_year} Q{selected_quarter})",
        labels={
            "brand_users": "Brand Users (Thousands)",
            "brand": "Mobile Brand"
        }
    )

    fig1.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )

    fig1.update_layout(
        showlegend=False,
        yaxis_title="Mobile Brand",
        xaxis_title="Brand Users (Millions)"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("2.Which Device Brands Dominate the PhonePe User Base Across India?")
    st.write("""
This visualization analyzes the distribution of PhonePe users based on the mobile device brands they use across India.

Features:
- Displays the total number of PhonePe users for each mobile device brand
- Highlights the most widely used smartphone brands among PhonePe users
- Uses a bar chart to easily compare device brand popularity
- Helps understand device ecosystem trends within the PhonePe user base

Insight:
Brands with higher user counts dominate the PhonePe ecosystem, indicating stronger smartphone market presence among digital payment users. Understanding device preferences helps identify which platforms contribute most to PhonePe adoption and user engagement.
""")

    query = text("""
    SELECT brand, SUM(brand_users) AS total_users
    FROM aggregated_users
    GROUP BY brand
    ORDER BY total_users DESC
    """)

    df = pd.read_sql(query, engine)

    fig2 = px.bar(
        df,
        x="brand",
        y="total_users",
        color="brand",
        title="Top Device Brands Used by PhonePe Users in India",
        text="total_users"
    )

    fig2.update_layout(
        xaxis_title="Device Brand",
        yaxis_title="Registered Users",
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("3.User Engagement Across Device Brands")
    st.write("""
This visualization analyzes how actively PhonePe users engage with the application across different mobile device brands.

Features:
- Displays the total number of app opens for each mobile device brand
- Highlights which devices generate the highest user engagement
- Allows comparison of app usage behavior across different smartphone brands
- Uses a bar chart to clearly rank device brands by engagement level

Insight:
Higher app open counts indicate stronger user engagement on specific device brands. Brands with greater engagement suggest a larger active user base and consistent usage of PhonePe services, helping understand which devices contribute most to platform activity.
""")
    
    query = text("""
    SELECT brand, SUM(appOpens) AS high_no_of_appopens
    FROM aggregated_users
    GROUP BY brand
    ORDER BY high_no_of_appopens DESC
    """)

    df = pd.read_sql(query, engine)

    fig3 = px.bar(
        df,
        x="brand",
        y="high_no_of_appopens",
        color="brand",
        title="User Engagement by Device Brand (App Opens)",
        text="high_no_of_appopens"
    )

    fig3.update_layout(
        xaxis_title="Device Brand",
        yaxis_title="Total App Opens",
        showlegend=False
    )

    fig3.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("4.Device Brand Usage Across Different States")
    st.write("""
This visualization explores how different mobile device brands are used by PhonePe users across various states in India.

Features:
- Displays the number of registered users for each device brand in every state
- Highlights regional preferences for different smartphone brands
- Uses a stacked bar chart to compare brand usage across states
- Helps identify states where specific device brands dominate the user base

Insight:
The chart reveals regional variations in smartphone usage among PhonePe users. States with larger segments for specific brands indicate stronger market presence of those devices, helping understand how device ecosystems influence digital payment adoption.
""")

    query = text("""
    SELECT state, brand, SUM(brand_users) AS total_brand_users
    FROM aggregated_users
    GROUP BY state, brand
    ORDER BY state
    """)

    df = pd.read_sql(query, engine)

    fig4 = px.bar(
        df,
        x="state",
        y="total_brand_users",
        color="brand",
        title="Device Brand Usage Across States",
        text="total_brand_users"
    )

    fig4.update_layout(
        xaxis_title="State",
        yaxis_title="Number of Registered Users",
        xaxis_tickangle=-45
    )

    fig4.update_traces(
        texttemplate='%{text:,}',
        textposition="inside"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("5.Device Brand Usage Changed Over Years")
    st.write("""
This visualization analyzes how the usage of different mobile device brands among PhonePe users has evolved over the years.

Features:
- Displays year-wise trends in the number of users for each mobile device brand
- Highlights how device preferences change over time
- Uses a line chart with markers to track growth patterns across brands
- Allows comparison of user adoption across different smartphone brands

Insight:
The trend lines show how the popularity of different device brands has shifted over time among PhonePe users. Brands with consistently rising user counts indicate growing market share, while stable or declining trends may reflect changing smartphone preferences or market competition.
""")

    query = text("""
    SELECT year, brand, SUM(brand_users) AS total_brand_users
    FROM aggregated_users
    GROUP BY year, brand
    ORDER BY year, brand
    """)

    df = pd.read_sql(query, engine)

    fig5 = px.line(
        df,
        x="year",
        y="total_brand_users",
        color="brand",
        markers=True,
        title="Device Brand Usage Trend Over Years"
    )

    fig5.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Registered Users",
        legend_title="Device Brand"
    )

    fig5.update_traces(
        hovertemplate="Brand: %{legendgroup}<br>Year: %{x}<br>Users: %{y:,}"
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# AGGREGATED INSURANCE

# FUNCTION TO FORMAT STATE NAME
def format_state_name(state):
    return state.replace("-", " ").replace("&", " & ").title()


# HOME PAGE
if page == "Home":

    st.subheader("")


# DEVICE DOMINANCE PAGE
elif page == "Insurance Penetration and Growth Potential Analysis":

    st.header("Insurance Penetration and Growth Potential Analysis")

    st.markdown("---")
    st.subheader("1.States with Highest Insurance Transaction Volume")
    st.write("""
This visualization highlights the states with the highest number of insurance transactions conducted through PhonePe.

Features:
- Displays state-wise insurance transaction counts
- Ranks states based on total insurance transactions
- Uses a bar chart to easily compare transaction activity across regions
- Helps identify states with strong adoption of digital insurance services

Insight:
States with higher insurance transaction volumes indicate stronger adoption of digital insurance services through PhonePe. These regions represent mature markets for insurance products, while states with lower volumes may offer opportunities for expanding digital insurance awareness and services.
""")

    query = text("""
    SELECT state, SUM(insurance_count) AS total_insurance_transactions
    FROM aggregated_insurance
    GROUP BY state
    ORDER BY total_insurance_transactions DESC
    """)

    df = pd.read_sql(query, engine)

    fig1 = px.bar(
        df,
        x="state",
        y="total_insurance_transactions",
        color="state",
        title="States with Highest Insurance Transactions on PhonePe",
        text="total_insurance_transactions"
    )

    fig1.update_layout(
        xaxis_title="State",
        yaxis_title="Total Insurance Transactions",
        showlegend=False,
        xaxis_tickangle=-45
    )

    fig1.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("2.States with Highest Insurance Transaction Amount")
    st.write("""
This visualization analyzes the states that generate the highest insurance transaction value through PhonePe.

Features:
- Displays the total insurance transaction amount for each state
- Highlights regions contributing the highest financial value in insurance services
- Uses a bar chart to compare transaction value across states
- Helps identify revenue-driving markets for digital insurance adoption

Insight:
States with higher insurance transaction amounts indicate stronger financial participation in digital insurance services. These regions may have higher-value policies or greater insurance awareness, making them important markets for expanding digital financial products.
""")

    query = text("""
    SELECT state, SUM(insurance_amount) AS total_insurance_amount
    FROM aggregated_insurance
    GROUP BY state
    ORDER BY total_insurance_amount DESC
    """)

    df = pd.read_sql(query, engine)

    fig2 = px.bar(
        df,
        x="state",
        y="total_insurance_amount",
        color="state",
        title="States with Highest Insurance Transaction Amount on PhonePe",
        text="total_insurance_amount"
    )

    fig2.update_layout(
        xaxis_title="State",
        yaxis_title="Total Insurance Amount",
        showlegend=False,
        xaxis_tickangle=-45
    )

    fig2.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("3.Insurance Adoption Growth Over Years")
    st.write("""
This visualization analyzes the year-wise growth of insurance transactions conducted through PhonePe.

Features:
- Displays the total number of insurance transactions for each year
- Tracks the growth trend of digital insurance adoption over time
- Uses a line chart with markers to clearly show yearly changes
- Helps identify periods of significant growth in insurance usage

Insight:
An increasing trend in insurance transactions indicates rising awareness and adoption of digital insurance services among PhonePe users. This growth reflects expanding trust in digital financial products and highlights the platform’s role in improving insurance accessibility across India.
""")

    query = text("""
    SELECT year, SUM(insurance_count) AS total_insurance_transactions
    FROM aggregated_insurance
    GROUP BY year
    ORDER BY year
    """)

    df = pd.read_sql(query, engine)

    fig3 = px.line(
        df,
        x="year",
        y="total_insurance_transactions",
        markers=True,
        title="Growth of Insurance Transactions on PhonePe Over Years"
    )

    fig3.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Insurance Transactions"
    )

    fig3.update_traces(
        hovertemplate="Year: %{x}<br>Total Transactions: %{y:,}"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("4.States with Many PhonePe Users but Low Insurance Transactions")
    st.write("""
This visualization identifies states where PhonePe has a large user base but relatively low insurance transaction activity.

Features:
- Compares total registered PhonePe users with insurance transaction counts
- Uses a scatter plot to highlight the relationship between platform adoption and insurance usage
- Displays each state as an individual data point for easy comparison
- Helps detect regions where insurance services are underutilized

Insight:
States with high registered users but lower insurance transaction counts represent untapped opportunities for digital insurance adoption. These regions could benefit from targeted awareness campaigns, promotional offers, or localized insurance products to improve adoption through the PhonePe platform.
""")

    query = text("""
    SELECT 
    u.state,
    SUM(u.registeredUsers) AS total_registered_users,
    SUM(i.insurance_count) AS insurance_transaction_count
    FROM aggregated_users u
    JOIN aggregated_insurance i
    ON u.state = i.state
    AND u.year = i.year
    AND u.quarter = i.quarter
    GROUP BY u.state
    """)

    df = pd.read_sql(query, engine)

    fig4 = px.scatter(
        df,
        x="total_registered_users",
        y="insurance_transaction_count",
        color="state",
        size="insurance_transaction_count",
        hover_name="state",
        title="States with High PhonePe Users but Low Insurance Transactions"
    )

    fig4.update_layout(
        xaxis_title="Total Registered PhonePe Users",
        yaxis_title="Insurance Transaction Count"
    )

    fig4.update_traces(
        marker=dict(opacity=0.7)
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("5.States Showing the Fastest Insurance Growth Rate")
    st.write("""
This visualization identifies the states where insurance transactions on PhonePe are growing at the fastest rate.

Features:
- Calculates year-over-year growth rate in insurance transactions for each state
- Highlights the top 10 states with the highest insurance growth percentage
- Uses a bar chart to clearly compare growth performance across states
- Helps identify emerging markets for digital insurance adoption

Insight:
States with the highest growth rates represent rapidly expanding markets for digital insurance services. These regions may have increasing awareness of financial protection products and strong potential for future insurance adoption through the PhonePe platform.
""")

    query = text("""
    SELECT 
    state,
    year,
    SUM(insurance_count) AS total_transactions
    FROM aggregated_insurance
    GROUP BY state, year
    ORDER BY state, year
    """)

    df = pd.read_sql(query, engine)

    df["growth_rate"] = df.groupby("state")["total_transactions"].pct_change() * 100

    growth_df = df.dropna()

    latest_growth = growth_df.sort_values("year").groupby("state").tail(1)

    top_growth = latest_growth.sort_values("growth_rate", ascending=False).head(10)

    fig5 = px.bar(
        top_growth,
        x="state",
        y="growth_rate",
        color="state",
        text="growth_rate",
        title="Top 10 States with Fastest Insurance Growth on PhonePe"
    )

    fig5.update_layout(
        xaxis_title="State",
        yaxis_title="Growth Rate (%)",
        showlegend=False
    )

    fig5.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside'
    )

    st.plotly_chart(fig5, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# MAP TRANSACTION

# FUNCTION TO FORMAT STATE NAME
def format_state_name(state):
    return state.replace("-", " ").replace("&", " & ").title()


# HOME PAGE
if page == "Home":

    st.subheader("")


# DEVICE DOMINANCE PAGE
elif page == "Transaction Analysis for Market Expansion":

    st.header("Transaction Analysis for Market Expansion")

    st.markdown("---")
    st.subheader("1.States with Highest PhonePe Transaction Volume")
    st.write("""
This visualization highlights the states with the highest number of PhonePe transactions.

Features:
- Displays the total transaction volume for each state
- Ranks the top 10 states based on transaction activity
- Uses a bar chart for clear comparison of transaction volumes
- Helps identify regions with strong digital payment adoption

Insight:
States with the highest transaction volumes indicate strong user engagement and frequent usage of PhonePe services. These regions represent mature digital payment markets where users actively rely on PhonePe for daily transactions.
""")

    query = text("""
    SELECT 
    state,
    SUM(count) AS total_transactions
    FROM map_transactions
    GROUP BY state
    ORDER BY total_transactions DESC
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    df_top = df.head(10)

    fig1 = px.bar(
        df_top,
        x="state",
        y="total_transactions",
        color="state",
        text="total_transactions",
        title="Top 10 States with Highest PhonePe Transaction Volume"
    )

    fig1.update_layout(
        xaxis_title="State",
        yaxis_title="Total Transactions",
        showlegend=False,
        xaxis_tickangle=-40
    )

    fig1.update_traces(
        texttemplate='%{text:,}',
        textposition="outside"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("2.States Generating the Highest PhonePe Transaction Value")
    st.write("""
This visualization highlights the states that generate the highest total transaction value on the PhonePe platform.

Features:
- Displays the total transaction value processed in each state
- Ranks the top 10 states based on overall transaction amount
- Uses a bar chart to easily compare transaction value across regions
- Helps identify states contributing the most to PhonePe's financial transaction flow

Insight:
States with the highest transaction values represent key economic hubs where users perform higher-value digital payments. These regions are important markets for PhonePe, as they contribute significantly to the platform’s total transaction revenue and financial activity.
""")

    query = text("""
    SELECT 
    state,
    SUM(amount) AS total_transaction_value
    FROM map_transactions
    GROUP BY state
    ORDER BY total_transaction_value DESC
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    df_top = df.head(10)

    fig2 = px.bar(
        df_top,
        x="state",
        y="total_transaction_value",
        color="state",
        text="total_transaction_value",
        title="Top 10 States by Total PhonePe Transaction Value"
    )

    fig2.update_layout(
        xaxis_title="State",
        yaxis_title="Total Transaction Value",
        showlegend=False,
        xaxis_tickangle=-40
    )

    fig2.update_traces(
        texttemplate='%{text:,.0f}',
        textposition="outside"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("3.Growth of PhonePe Transactions Over Time")
    st.write("""
This visualization tracks the growth of PhonePe transactions over different years and quarters.

Features:
- Displays the total number of transactions for each year and quarter
- Uses a line chart with markers to highlight transaction trends over time
- Helps observe seasonal patterns and growth phases in digital payments
- Provides a time-based view of how PhonePe usage has evolved

Insight:
An increasing trend in transaction counts indicates rising adoption of digital payments through PhonePe. Growth over quarters and years reflects expanding user trust, wider merchant acceptance, and increasing reliance on digital financial services across India.
""")

    query = text("""
    SELECT 
    year,
    quarter,
    SUM(count) AS total_transactions
    FROM map_transactions
    GROUP BY year, quarter
    ORDER BY year, quarter
    """)

    df = pd.read_sql(query, engine)

    df["year_quarter"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)

    fig3 = px.line(
        df,
        x="year_quarter",
        y="total_transactions",
        markers=True,
        title="Growth of PhonePe Transactions Over Time"
    )

    fig3.update_layout(
        xaxis_title="Year / Quarter",
        yaxis_title="Total Transaction Count"
    )

    fig3.update_traces(
        hovertemplate="Period: %{x}<br>Transactions: %{y:,}"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("4.Distribution of Transaction Types Across States")
    st.write("""
This visualization shows how different types of PhonePe transactions are distributed across the top performing states.

Features:
- Displays transaction counts categorized by transaction type for each state
- Focuses on the top 10 states with the highest overall transaction activity
- Uses a stacked bar chart to compare multiple transaction categories within each state
- Helps understand which transaction types dominate in different regions

Insight:
The distribution of transaction types reveals user payment behavior across states. Certain regions may rely more on specific services such as peer-to-peer transfers, merchant payments, or financial services. Understanding these patterns helps identify regional preferences and supports targeted service improvements.
""")

    query = text("""
    SELECT 
    state,
    type,
    SUM(count) AS total_transactions
    FROM map_transactions
    GROUP BY state, type
    ORDER BY state
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    top_states = (
        df.groupby("state")["total_transactions"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index
    )

    df_filtered = df[df["state"].isin(top_states)]

    fig4 = px.bar(
        df_filtered,
        x="state",
        y="total_transactions",
        color="type",
        title="Distribution of PhonePe Transaction Types Across States"
    )

    fig4.update_layout(
        xaxis_title="State",
        yaxis_title="Total Transactions",
        barmode="stack",
        xaxis_tickangle=-40,
        legend_title="Transaction Type"
    )
    
    fig4.update_traces(
        hovertemplate="State: %{x}<br>Transactions: %{y:,}<extra></extra>"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("5.States with High Growth Potential but Lower Transaction Activity")
    st.write("""
This visualization highlights states that currently have lower overall transaction activity but show potential for future growth in digital payments.

Features:
- Identifies states with comparatively lower total transaction volumes
- Tracks yearly transaction trends for these emerging markets
- Uses a line chart with markers to visualize growth patterns over time
- Allows comparison of transaction growth among multiple states

Insight:
States with lower transaction activity but steady growth trends represent emerging digital payment markets. These regions may benefit from improved digital infrastructure, awareness campaigns, and merchant adoption strategies, creating opportunities for PhonePe to expand its user engagement and transaction volume.
""")

    query = text("""
    SELECT 
    state,
    year,
    SUM(count) AS total_transactions
    FROM map_transactions
    GROUP BY state, year
    ORDER BY state, year
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    state_totals = df.groupby("state")["total_transactions"].sum().reset_index()

    low_activity_states = state_totals.sort_values(
        by="total_transactions"
    ).head(10)["state"]

    df_filtered = df[df["state"].isin(low_activity_states)]

    fig5 = px.line(
        df_filtered,
        x="year",
        y="total_transactions",
        color="state",
        markers=True,
        title="Transaction Growth Trends in Emerging PhonePe Markets"
    )

    fig5.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Transaction Count",
        legend_title="State"
    )

    fig5.update_traces(
        hovertemplate="State: %{legendgroup}<br>Year: %{x}<br>Transactions: %{y:,}"
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# MAP USERS

# FUNCTION TO FORMAT STATE NAME
def format_state_name(state):
    return state.replace("-", " ").replace("&", " & ").title()


# HOME PAGE
if page == "Home":

    st.subheader("")


# DEVICE DOMINANCE PAGE
elif page == "User Engagement and Growth Strategy":

    st.header("User Engagement and Growth Strategy")

    st.markdown("---")
    st.subheader("1.States with the Highest Number of Registered PhonePe Users")
    st.write("""
This visualization highlights the states with the highest number of registered PhonePe users across India.

Features:
- Displays the total number of registered PhonePe users for each state
- Identifies the top 10 states with the largest user base
- Uses a bar chart to clearly compare user distribution across states
- Helps understand where PhonePe adoption is strongest

Insight:
States with the highest number of registered users represent major digital payment hubs where PhonePe adoption is widespread. These regions often have stronger digital infrastructure, higher smartphone penetration, and greater awareness of digital financial services.
""")

    query = text("""
    SELECT 
    state,
    SUM(registeredUsers) AS total_registered_users
    FROM map_users
    GROUP BY state
    ORDER BY total_registered_users DESC
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    df_top = df.head(10)

    fig1 = px.bar(
        df_top,
        x="state",
        y="total_registered_users",
        color="state",
        text="total_registered_users",
        title="Top 10 States with Highest PhonePe Registered Users"
    )
    
    fig1.update_layout(
        xaxis_title="State",
        yaxis_title="Total Registered Users",
        showlegend=False,
        xaxis_tickangle=-40
    )

    fig1.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("2.User Engagement Across States (Registered Users vs App Opens)")
    st.write("""
This visualization analyzes user engagement across states by comparing the number of registered PhonePe users with the number of times the application is opened.

Features:
- Compares total registered users and total app opens for each state
- Uses a scatter plot to show the relationship between user base and app activity
- Bubble size represents the number of registered users in each state
- Helps identify states with strong or weak user engagement levels

Insight:
States with high registered users and high app opens indicate strong user engagement and frequent usage of PhonePe services. States with many users but relatively fewer app opens may represent areas where engagement strategies, promotions, or feature awareness can be improved.
""")

    query = text("""
    SELECT 
    state,
    SUM(registeredUsers) AS total_registered_users,
    SUM(appOpens) AS total_app_opens
    FROM map_users
    GROUP BY state
    ORDER BY total_registered_users DESC
    """)

    df = pd.read_sql(query, engine)

    def format_state_name(state):
        state = state.replace("-", " ").replace("&", "and")
        return state.title()

    df["state"] = df["state"].apply(format_state_name)

    fig2 = px.scatter(
        df,
        x="total_registered_users",
        y="total_app_opens",
        color="state",
        size="total_registered_users",
        hover_name="state",
        title="User Engagement Across States"
    )

    fig2.update_layout(
        xaxis_title="Total Registered Users",
        yaxis_title="Total App Opens"
    )

    fig2.update_traces(
        marker=dict(opacity=0.7)
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("3.User Growth Trend Over Time")
    st.write("""
This visualization shows how the number of registered PhonePe users has grown over the years across India.

Features:
- Aggregates total registered PhonePe users for each year
- Uses a line chart with markers to clearly visualize the growth trend
- Helps identify periods of rapid user adoption
- Provides a clear view of how PhonePe's user base has expanded over time

Insight:
A steady upward trend in registered users indicates increasing adoption of digital payment platforms like PhonePe. Rapid growth periods may reflect expansion into new markets, improved digital infrastructure, or increased trust in online financial services.
""")

    query = text("""
    SELECT 
    year,
    SUM(registeredUsers) AS total_registered_users
    FROM map_users
    GROUP BY year
    ORDER BY year
    """)

    df = pd.read_sql(query, engine)

    fig3 = px.line(
        df,
        x="year",
        y="total_registered_users",
        markers=True,
        title="Growth of Registered PhonePe Users Over the Years"
    )

    fig3.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Registered Users"
    )

    fig3.update_traces(
        hovertemplate="Year: %{x}<br>Registered Users: %{y:,}"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("4.District-wise User Engagement (Registered Users vs App Opens)")
    st.write("""
This visualization compares the number of registered PhonePe users with the total number of app opens across different states. It helps measure how actively users engage with the PhonePe application.

Features:
- Displays the relationship between registered users and app usage
- Uses a scatter plot to identify engagement patterns across states
- Bubble size represents the number of registered users
- Helps detect states with strong or weak user activity

Insight:
States that appear in the upper-right section of the chart have both a large user base and high app activity, indicating strong engagement. States with many registered users but relatively lower app opens may indicate untapped engagement potential, where awareness campaigns or improved services could increase usage.
""")

    query = text("""
    SELECT 
    state,
    SUM(registeredUsers) AS total_registered_users,
    SUM(appOpens) AS total_app_opens
    FROM map_users
    GROUP BY state
    """)

    df = pd.read_sql(query, engine)

    df["state"] = df["state"].str.replace("-", " ").str.title()

    fig4 = px.scatter(
        df,
        x="total_registered_users",
        y="total_app_opens",
        color="state",
        size="total_registered_users",
        hover_name="state",
        title="State-wise User Engagement on PhonePe"
    )

    fig4.update_layout(
        xaxis_title="Total Registered Users",
        yaxis_title="Total App Opens"
    )

    fig4.update_traces(
        marker=dict(opacity=0.7)
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("5.States with High Users but Lower Engagement")
    st.write("""
This visualization highlights states where PhonePe has a large number of registered users but comparatively lower engagement in terms of app opens. It helps identify regions where user adoption is strong but active usage may be limited.

Features:
- Compares total registered users with total app opens across states
- Uses a scatter plot to detect engagement gaps
- Bubble size represents the total number of registered users
- Helps identify potential markets for increasing user engagement

Insight:
States positioned far to the right but relatively lower on the vertical axis have many registered users but fewer app opens. This indicates lower user engagement. These states present an opportunity for PhonePe to improve user interaction through targeted campaigns, better features, or promotional incentives to increase app usage.
""")

    query = text("""
    SELECT 
    state,
    SUM(registeredUsers) AS total_registered_users,
    SUM(appOpens) AS total_app_opens
    FROM map_users
    GROUP BY state
    ORDER BY total_registered_users DESC
    """)

    df = pd.read_sql(query, engine)

    df["state"] = df["state"].str.replace("-", " ").str.title()

    fig5 = px.scatter(
        df,
        x="total_registered_users",
        y="total_app_opens",
        color="state",
        size="total_registered_users",
        hover_name="state",
        title="States with High Registered Users but Lower Engagement"
    )

    fig5.update_layout(
        xaxis_title="Total Registered Users",
        yaxis_title="Total App Opens"
    )

    fig5.update_traces(
        marker=dict(opacity=0.7)
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------