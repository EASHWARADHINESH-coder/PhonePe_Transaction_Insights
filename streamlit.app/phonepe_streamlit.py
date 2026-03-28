# IMPORT LIBRARIES

import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text

# PAGE CONFIG

st.set_page_config(page_title="PhonePe Insights", layout="wide")
st.title("📊 PhonePe Transaction Insights Dashboard")

# DATABASE CONNECTION

@st.cache_resource
def get_engine():
    username = "root"
    password = "your_password"
    host = "localhost"
    database = "phonepe_db"

    engine = create_engine(
        f"mysql+pymysql://{username}:{password}@{host}/{database}"
    )
    return engine

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

    st.markdown("""
    # 📊 PhonePe Insights Dashboard
    ### 🚀 Understanding Digital Payment Growth Across India
    """)

    st.info("""
    🔍 Key Insights Covered:
    
    • Transaction Distribution Across India  
    • User Adoption Across States  
    • Insurance Penetration Analysis  
    • Top Performing States Snapshot
    """)

    # ----------------------------
    # LOAD FILTER DATA
    # ----------------------------
    try:
        year_query = text("""
        SELECT DISTINCT year
        FROM aggregated_transactions
        ORDER BY year
        """)
        year_df = pd.read_sql(year_query, engine)
        available_years = sorted(year_df["year"].dropna().tolist())

        quarter_query = text("""
        SELECT DISTINCT quarter
        FROM aggregated_transactions
        ORDER BY quarter
        """)
        quarter_df = pd.read_sql(quarter_query, engine)
        available_quarters = sorted(quarter_df["quarter"].dropna().tolist())

    except Exception as e:
        st.error(f"Error loading filter values: {e}")
        available_years = []
        available_quarters = []

    # ----------------------------
    # FILTERS
    # ----------------------------
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        selected_year = st.selectbox(
            "Select Year",
            available_years if available_years else ["No Data"]
        )

    with col_filter2:
        selected_quarter = st.selectbox(
            "Select Quarter",
            available_quarters if available_quarters else ["No Data"]
        )

    # ----------------------------
    # KPI SECTION
    # ----------------------------
    try:
        kpi_transaction_query = text("""
        SELECT SUM(transaction_count) AS total_transactions
        FROM aggregated_transactions
        WHERE year = :year AND quarter = :quarter
        """)

        kpi_user_query = text("""
        SELECT SUM(registeredUsers) AS total_users
        FROM aggregated_users
        WHERE year = :year AND quarter = :quarter
        """)

        kpi_insurance_query = text("""
        SELECT SUM(insurance_count) AS total_insurance
        FROM aggregated_insurance
        WHERE year = :year AND quarter = :quarter
        """)

        total_transactions = pd.read_sql(
            kpi_transaction_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )["total_transactions"].iloc[0]

        total_users = pd.read_sql(
            kpi_user_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )["total_users"].iloc[0]

        total_insurance = pd.read_sql(
            kpi_insurance_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )["total_insurance"].iloc[0]

        total_transactions = 0 if pd.isna(total_transactions) else total_transactions
        total_users = 0 if pd.isna(total_users) else total_users
        total_insurance = 0 if pd.isna(total_insurance) else total_insurance

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Transactions",
            f"{total_transactions/1_000_000:.2f} M"
        )

        col2.metric(
            "Registered Users",
            f"{total_users/1_000_000:.2f} M"
        )

        col3.metric(
            "Insurance Transactions",
            f"{total_insurance/1_000_000:.2f} M"
        )

    except Exception as e:
        st.error(f"Error loading KPI metrics: {e}")

    st.markdown("---")

    # ----------------------------
    # MAP DATA QUERIES
    # ----------------------------
    try:
        # Transaction map data
        query_transactions = text("""
        SELECT 
            state,
            SUM(transaction_count) AS total_transactions
        FROM aggregated_transactions
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        """)

        df_transactions = pd.read_sql(
            query_transactions, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        # User map data
        query_users = text("""
        SELECT 
            state,
            SUM(registeredUsers) AS total_users
        FROM aggregated_users
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        """)

        df_users = pd.read_sql(
            query_users, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        # Insurance map data
        query_insurance = text("""
        SELECT 
            state,
            SUM(insurance_count) AS total_insurance
        FROM aggregated_insurance
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        """)

        df_insurance = pd.read_sql(
            query_insurance, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        # State formatting
        if not df_transactions.empty:
            df_transactions["state"] = df_transactions["state"].str.replace("-", " ").str.title()

        if not df_users.empty:
            df_users["state"] = df_users["state"].str.replace("-", " ").str.title()

        if not df_insurance.empty:
            df_insurance["state"] = df_insurance["state"].str.replace("-", " ").str.title()

        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

        # ----------------------------
        # MAP CHARTS
        # ----------------------------
        col_map1, col_map2, col_map3 = st.columns(3)

        with col_map1:
            st.subheader("💳 Transactions")
            st.caption("State-wise transaction distribution")

            fig1 = px.choropleth(
                df_transactions,
                geojson=geojson_url,
                featureidkey="properties.ST_NM",
                locations="state",
                color="total_transactions",
                color_continuous_scale="Reds",
                title=f"Transactions Map ({selected_year} Q{selected_quarter})"
            )

            fig1.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
            fig1.update_geos(fitbounds="locations", visible=False)

            st.plotly_chart(fig1, use_container_width=True)

        with col_map2:
            st.subheader("👥 Users")
            st.caption("State-wise registered users distribution")

            fig2 = px.choropleth(
                df_users,
                geojson=geojson_url,
                featureidkey="properties.ST_NM",
                locations="state",
                color="total_users",
                color_continuous_scale="Blues",
                title=f"Users Map ({selected_year} Q{selected_quarter})"
            )

            fig2.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
            fig2.update_geos(fitbounds="locations", visible=False)

            st.plotly_chart(fig2, use_container_width=True)

        with col_map3:
            st.subheader("🛡 Insurance")
            st.caption("State-wise insurance transaction distribution")

            fig3 = px.choropleth(
                df_insurance,
                geojson=geojson_url,
                featureidkey="properties.ST_NM",
                locations="state",
                color="total_insurance",
                color_continuous_scale="Greens",
                title=f"Insurance Map ({selected_year} Q{selected_quarter})"
            )

            fig3.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
            fig3.update_geos(fitbounds="locations", visible=False)

            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading map charts: {e}")

    st.markdown("---")

    # ----------------------------
    # TOP STATES SNAPSHOT
    # ----------------------------
    try:
        st.subheader("🔥 Top Performing States Snapshot")

        top_txn_query = text("""
        SELECT 
            state,
            SUM(transaction_count) AS total_transactions
        FROM aggregated_transactions
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        ORDER BY total_transactions DESC
        LIMIT 5
        """)

        top_user_query = text("""
        SELECT 
            state,
            SUM(registeredUsers) AS total_users
        FROM aggregated_users
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        ORDER BY total_users DESC
        LIMIT 5
        """)

        top_ins_query = text("""
        SELECT 
            state,
            SUM(insurance_count) AS total_insurance
        FROM aggregated_insurance
        WHERE year = :year AND quarter = :quarter
        GROUP BY state
        ORDER BY total_insurance DESC
        LIMIT 5
        """)

        top_txn = pd.read_sql(
            top_txn_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        top_users = pd.read_sql(
            top_user_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        top_ins = pd.read_sql(
            top_ins_query, engine,
            params={"year": selected_year, "quarter": selected_quarter}
        )

        for df_ in [top_txn, top_users, top_ins]:
            if not df_.empty:
                df_["state"] = df_["state"].str.replace("-", " ").str.title()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### 💳 Top Transaction States")
            st.dataframe(top_txn, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("### 👥 Top User States")
            st.dataframe(top_users, use_container_width=True, hide_index=True)

        with c3:
            st.markdown("### 🛡 Top Insurance States")
            st.dataframe(top_ins, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading top states summary: {e}")

    st.markdown("---")

    # ----------------------------
    # HOME PAGE INSIGHTS
    # ----------------------------
    st.subheader("📌 Key Growth Insight")
    st.success(
"The home page shows that PhonePe growth should be tracked through transactions, users, and insurance together, because strong adoption in one area may not always mean balanced platform growth."
    )

    st.caption("Built with Streamlit | PhonePe Transaction Insights Dashboard")

# AGGREGATED TRANSACTIONS

elif page == "Decoding Transaction Dynamics on PhonePe":

    st.header("Decoding Transaction Dynamics on PhonePe")
    st.subheader("1.Comparison between Transaction Count and Transaction Amount by Transaction Type")

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

        st.write("""
Issue: Transaction usage and transaction value do not always grow together across states and categories, so high-frequency services may not be the highest-value drivers. This makes it important to track both count and amount together to understand real category growth.

Analysis & Growth Insight: Growth is strongest in categories that show a rise in both transaction volume and total value, indicating wider adoption as well as higher monetary contribution. This helps identify scalable services, state-wise demand patterns, and the transaction types driving PhonePe’s overall expansion.
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
Issue: Transaction share by count and amount often differs across categories, creating imbalance where frequently used services may not generate proportional revenue.

Analysis & Growth Insight: Focusing on categories with high value share and scaling high-frequency services can drive balanced growth by improving both user engagement and revenue contribution.
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
Issue: Growth in transaction count and transaction amount may not increase at the same rate over years, indicating gaps between user adoption and value generation.

Analysis & Growth Insight: Consistent upward trends signal strong digital adoption, and identifying transaction types driving both volume and value helps scale high-performing services for sustained growth.
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
Issue: Quarterly fluctuations in transaction count and amount indicate inconsistent growth, often influenced by seasonal demand and external factors like festivals or campaigns.

Analysis & Growth Insight: Identifying peak-performing quarters and transaction types helps leverage seasonal trends, optimize campaigns, and drive steady, year-round growth.
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
Issue: Top states by transaction volume and value may differ, indicating uneven regional contribution where high engagement does not always translate to high revenue.

Analysis & Growth Insight: Focusing on high-value states and improving monetization in high-volume regions can drive balanced geographic growth and maximize overall platform performance.
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
Issue: User distribution is concentrated in a few mobile brands, limiting reach if optimization is not aligned with dominant devices.

Analysis & Growth Insight: Focusing app performance and campaigns on top-used devices while expanding compatibility to emerging brands can increase user acquisition and drive broader growth.
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
Issue: User concentration in a few dominant mobile brands creates dependency, limiting reach across diverse device ecosystems.

Analysis & Growth Insight: Optimizing for leading brands while improving support for underrepresented devices can expand user base, enhance accessibility, and drive inclusive growth across India.
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
Issue: Engagement levels vary significantly across mobile brands, indicating inconsistent user activity despite similar user distribution.

Analysis & Growth Insight: Enhancing performance and experience on high-engagement devices while improving retention strategies for low-engagement brands can boost overall app usage and drive sustained growth.
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
Issue: Strong regional dominance of certain mobile brands creates uneven device distribution, limiting uniform user reach and experience across states.

Analysis & Growth Insight: Tailoring optimization and marketing strategies to region-specific device preferences can enhance adoption, improve accessibility, and drive targeted growth across diverse markets.
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
Issue: Changing device brand trends indicate shifting user preferences, risking decline in engagement if adaptation to new dominant devices is delayed.

Analysis & Growth Insight: Tracking rising brands and optimizing early for emerging devices enables better user acquisition, sustained engagement, and long-term growth.
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
Issue: Insurance transaction adoption is uneven across states, with a few regions dominating while others show low penetration.

Analysis & Growth Insight: Expanding awareness and targeted offerings in low-performing states while scaling success strategies from high-performing regions can drive nationwide insurance growth.
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
Issue: Insurance transaction value is concentrated in a few states, indicating uneven revenue distribution and limited high-value adoption across regions.

Analysis & Growth Insight: Expanding high-value insurance products and awareness in low-performing states while strengthening top markets can drive balanced revenue growth and deeper market penetration.
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
Issue: Year-wise growth in insurance transactions may be inconsistent, indicating fluctuating adoption and awareness across different periods.

Analysis & Growth Insight: Sustained upward trends reflect increasing trust and accessibility, and strengthening awareness campaigns with consistent engagement can drive steady long-term growth in digital insurance adoption.
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
Issue: High user base but low insurance transactions in certain states indicates underutilization and a gap between platform adoption and service usage.

Analysis & Growth Insight: Targeted awareness, localized products, and incentives in these regions can convert existing users into active insurance customers, unlocking significant growth potential.
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
Issue: Rapid growth is concentrated in a few states, indicating uneven expansion and untapped potential in slower-growing regions.

Analysis & Growth Insight: Focusing on high-growth states to scale quickly while replicating successful strategies in low-growth regions can drive balanced and accelerated nationwide insurance adoption.
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
Issue: Transaction volume is heavily concentrated in a few states, indicating uneven adoption and reliance on limited high-performing regions.

Analysis & Growth Insight: Expanding digital payment adoption in low-performing states while strengthening engagement in top states can drive balanced growth and broader market penetration.
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
Issue: Transaction value is concentrated in a few states, indicating uneven economic contribution and dependency on key regions.

Analysis & Growth Insight: Expanding high-value transactions in emerging states while strengthening core markets can drive balanced revenue growth and improve overall financial distribution.
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
Issue: Growth across years and quarters may be uneven, showing seasonal spikes and inconsistent transaction trends.

Analysis & Growth Insight: Sustained upward trends indicate strong adoption, and leveraging peak periods while stabilizing low phases can drive consistent long-term growth.
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
Issue: Transaction type distribution varies across states, leading to uneven service adoption and reliance on specific payment categories.

Analysis & Growth Insight: Identifying dominant transaction types per region enables targeted feature optimization and promotions, driving diversified usage and balanced growth across states.
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
Issue: Low transaction volumes in certain states indicate limited adoption despite gradual growth trends.

Analysis & Growth Insight: Strengthening digital infrastructure, awareness, and merchant onboarding in these emerging markets can accelerate adoption and unlock significant future growth.
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
Issue: User base is concentrated in a few states, indicating uneven adoption and limited reach in less penetrated regions.

Analysis & Growth Insight: Expanding awareness, infrastructure, and localized strategies in low-user states while strengthening engagement in top regions can drive balanced nationwide growth.
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
Issue: Some states show high user base but low app opens, indicating weak engagement despite strong adoption.

Analysis & Growth Insight: Improving user retention through targeted campaigns, feature awareness, and personalized experiences can convert passive users into active users and drive sustained growth.
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
Issue: User growth may be uneven across years, indicating fluctuating adoption and potential saturation in certain periods.

Analysis & Growth Insight: Sustained upward trends reflect strong adoption, and expanding into untapped markets with targeted strategies can maintain consistent user growth.
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
Issue: High user registration in some states does not translate into proportional app usage, indicating low engagement levels.

Analysis & Growth Insight: Enhancing user experience, targeted campaigns, and feature awareness in low-engagement states can increase app activity and drive deeper platform growth.
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
Issue: High user base but low app opens in certain states indicates a gap between adoption and active engagement.

Analysis & Growth Insight: Targeted engagement strategies, feature awareness, and incentives in these regions can convert passive users into active users, driving deeper usage and growth.
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