import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="US Import Trend Hunter", layout="wide")

# --- CACHED DATA FUNCTION ---
# We use @st.cache_data so we don't hit the API every time you click a button
@st.cache_data
def fetch_census_data(year, months):
    base_url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
    hs_level = "HS4" # 4-Digit HS Codes
    
    all_data = []
    
    # Display a progress bar in the UI
    progress_text = f"Fetching data for {year}..."
    my_bar = st.progress(0, text=progress_text)
    
    for i, month in enumerate(months):
        time_str = f"{year}-{month}"
        params = {
            'get': 'I_GEN_VAL_MO,I_COMMODITY_SDESC',
            'time': time_str,
            'COMM_LVL': hs_level,
        }
        try:
            r = requests.get(base_url, params=params)
            if r.status_code == 200:
                data = r.json()
                df = pd.DataFrame(data[1:], columns=data[0])
                all_data.append(df)
        except:
            pass
        
        # Update progress bar
        my_bar.progress((i + 1) / len(months), text=progress_text)

    my_bar.empty() # Clear bar when done

    if not all_data:
        return pd.DataFrame()

    full_df = pd.concat(all_data)
    full_df['I_GEN_VAL_MO'] = pd.to_numeric(full_df['I_GEN_VAL_MO'])
    
    # Aggregate by Code and Description
    aggregated = full_df.groupby(['I_COMMODITY', 'I_COMMODITY_SDESC'])['I_GEN_VAL_MO'].sum().reset_index()
    return aggregated

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Filter Options")

# Dynamic Year Selection
current_year = st.sidebar.selectbox("Select Year to Analyze", ["2025", "2024"], index=0)
prior_year = str(int(current_year) - 1)

# Quarter Selection
quarter = st.sidebar.selectbox("Select Quarter", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)"])
if "Q1" in quarter:
    target_months = ["01", "02", "03"]
elif "Q2" in quarter:
    target_months = ["04", "05", "06"]
else:
    target_months = ["07", "08", "09"]

# Minimum Volume Filter (To hide small noise)
min_vol = st.sidebar.slider("Min. Import Volume ($ Millions)", 1, 500, 50)
min_vol_raw = min_vol * 1_000_000

# --- MAIN APP LOGIC ---
st.title(f"🇺🇸 US Import Opportunity Scout ({quarter} {current_year})")
st.markdown("Identify high-growth import categories using real-time US Census Data.")

# Fetch Data
col1, col2 = st.columns(2)
with col1:
    st.info(f"Fetching {current_year} Data...")
    df_curr = fetch_census_data(current_year, target_months)
with col2:
    st.info(f"Fetching {prior_year} Data (Comparison)...")
    df_prev = fetch_census_data(prior_year, target_months)

if not df_curr.empty and not df_prev.empty:
    # Rename and Merge
    df_curr.rename(columns={'I_GEN_VAL_MO': 'Value_Current'}, inplace=True)
    df_prev.rename(columns={'I_GEN_VAL_MO': 'Value_Prior'}, inplace=True)
    
    merged = pd.merge(df_curr, df_prev[['I_COMMODITY', 'Value_Prior']], on='I_COMMODITY', how='inner')
    
    # Calculate Metrics
    merged['Growth_%'] = ((merged['Value_Current'] - merged['Value_Prior']) / merged['Value_Prior']) * 100
    merged['Market_Size_($M)'] = merged['Value_Current'] / 1_000_000
    
    # Filter by User Selection
    filtered = merged[merged['Value_Current'] > min_vol_raw].copy()
    
    # Top 15 Winners
    top_growers = filtered.sort_values(by='Growth_%', ascending=False).head(15)
    
    # --- VISUALIZATION ---
    
    # 1. Interactive Bar Chart (Growth)
    st.subheader(f"🚀 Top 15 Fastest Growing Imports (YoY)")
    fig_bar = px.bar(
        top_growers, 
        x='Growth_%', 
        y='I_COMMODITY_SDESC', 
        orientation='h',
        hover_data=['Market_Size_($M)', 'I_COMMODITY'],
        color='Growth_%',
        color_continuous_scale='Viridis',
        title="Growth Percentage by Category"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

    # 2. Scatter Plot (Opportunity Matrix)
    st.subheader("💎 The 'Hidden Gems' Matrix")
    st.markdown("Look for bubbles in the **top-right**: High Volume AND High Growth.")
    
    # We take top 50 for the scatter plot to show more context
    scatter_data = filtered.sort_values(by='Growth_%', ascending=False).head(50)
    
    fig_scatter = px.scatter(
        scatter_data,
        x='Market_Size_($M)',
        y='Growth_%',
        size='Market_Size_($M)',
        color='Growth_%',
        hover_name='I_COMMODITY_SDESC',
        log_x=True, # Log scale helps visualize massive vs small markets
        title="Market Size vs. Growth Rate"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 3. Raw Data Table
    with st.expander("View Raw Data Source"):
        st.dataframe(top_growers)

else:
    st.error("Data not available. Note: Census data has a lag (~45 days). Q4 data might not be out yet.")
