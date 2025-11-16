import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="US Import Trend Hunter", layout="wide")

# --- FETCH FUNCTION (With fixes applied) ---
@st.cache_data
def fetch_census_data(year, months):
    base_url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
    hs_level = "HS4" 
    
    all_data = []
    
    progress_text = f"Fetching data for {year}..."
    my_bar = st.progress(0, text=progress_text)
    
    for i, month in enumerate(months):
        time_str = f"{year}-{month}"
        
        # FIXED: Includes correct variable names and wildcard '*'
        params = {
            'get': 'I_COMMODITY,I_COMMODITY_SDESC,GEN_VAL_MO', 
            'time': time_str,
            'COMM_LVL': hs_level,
            'I_COMMODITY': '*' 
        }
        
        try:
            r = requests.get(base_url, params=params)
            
            if r.status_code != 200:
                if r.status_code != 204:
                    st.warning(f"⚠️ Month {time_str}: Status {r.status_code}")
                continue 
                
            data = r.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            all_data.append(df)
            
        except Exception as e:
            st.error(f"⚠️ Error on {time_str}: {str(e)}")
        
        my_bar.progress((i + 1) / len(months), text=progress_text)

    my_bar.empty() 

    if not all_data:
        return pd.DataFrame()

    full_df = pd.concat(all_data)
    
    full_df['GEN_VAL_MO'] = pd.to_numeric(full_df['GEN_VAL_MO'])
    
    # Group by Code and Description
    aggregated = full_df.groupby(['I_COMMODITY', 'I_COMMODITY_SDESC'])['GEN_VAL_MO'].sum().reset_index()
    return aggregated

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Timeframe")
current_year = st.sidebar.selectbox("Year", ["2025", "2024"], index=0)
prior_year = str(int(current_year) - 1)
quarter = st.sidebar.selectbox("Quarter", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)"])

if "Q1" in quarter:
    target_months = ["01", "02", "03"]
elif "Q2" in quarter:
    target_months = ["04", "05", "06"]
else:
    target_months = ["07", "08", "09"]

st.sidebar.header("2. Standard Volume Filter")
# Dual Slider for Min and Max Range
vol_range = st.sidebar.slider(
    "Import Volume Range ($ Millions)",
    min_value=0.0, max_value=500.0, value=(1.0, 100.0), step=0.5
)
min_vol_raw = vol_range[0] * 1_000_000
max_vol_raw = vol_range[1] * 1_000_000

st.sidebar.header("3. Niche Hunter")
# Checkbox to enable "Hidden Gems" logic
show_gems = st.sidebar.checkbox("Include Low-Vol / High-Growth Gems?", value=True)

gem_growth_threshold = 0
if show_gems:
    st.sidebar.caption("Find items smaller than your min volume, but growing fast.")
    gem_growth_threshold = st.sidebar.slider("Min Growth % for Gems", 50, 1000, 200)

# --- MAIN APP LOGIC ---
st.title(f"🇺🇸 US Import Opportunity Scout ({quarter} {current_year})")
st.markdown(f"**Strategy:** Showing items between **\${vol_range[0]}M - \${vol_range[1]}M**.")
if show_gems:
    st.markdown(f"*Plus: Micro-trends (<\${vol_range[0]}M) growing faster than **{gem_growth_threshold}%**.*")

col1, col2 = st.columns(2)
with col1:
    st.info(f"Fetching {current_year} Data...")
    df_curr = fetch_census_data(current_year, target_months)
with col2:
    st.info(f"Fetching {prior_year} Data...")
    df_prev = fetch_census_data(prior_year, target_months)

if not df_curr.empty and not df_prev.empty:
    # Rename and Merge
    df_curr.rename(columns={'GEN_VAL_MO': 'Value_Current'}, inplace=True)
    df_prev.rename(columns={'GEN_VAL_MO': 'Value_Prior'}, inplace=True)
    
    merged = pd.merge(df_curr, df_prev[['I_COMMODITY', 'Value_Prior']], on='I_COMMODITY', how='inner')
    
    # Calculate Metrics
    merged['Growth_%'] = ((merged['Value_Current'] - merged['Value_Prior']) / merged['Value_Prior']) * 100
    merged['Market_Size_($M)'] = merged['Value_Current'] / 1_000_000
    
    # --- COMPLEX FILTERING LOGIC ---
    
    # Mask 1: The Standard Range (Between Min and Max)
    mask_standard = (merged['Value_Current'] >= min_vol_raw) & (merged['Value_Current'] <= max_vol_raw)
    
    # Mask 2: The "Hidden Gems" (Below Min Volume, but High Growth)
    # We add > 5000 to filter out absolute noise (like $10 shipments)
    mask_gems = (
        (merged['Value_Current'] < min_vol_raw) & 
        (merged['Value_Current'] > 5000) & 
        (merged['Growth_%'] >= gem_growth_threshold)
    )
    
    if show_gems:
        filtered = merged[mask_standard | mask_gems].copy()
        # Tag them so we can color them differently in the chart
        filtered['Type'] = filtered.apply(
            lambda x: 'Hidden Gem 💎' if (x['Value_Current'] < min_vol_raw) else 'Standard Deal 📦', axis=1
        )
    else:
        filtered = merged[mask_standard].copy()
        filtered['Type'] = 'Standard Deal 📦'

    # Sort by Growth to see winners first
    top_growers = filtered.sort_values(by='Growth_%', ascending=False).head(20)
    
    # --- VISUALIZATION ---
    
    if not top_growers.empty:
        st.subheader(f"🚀 Top Opportunities (Mixed View)")
        
        # Bar Chart with Color coding for Gems vs Standard
        fig_bar = px.bar(
            top_growers, 
            x='Growth_%', 
            y='I_COMMODITY_SDESC', 
            orientation='h',
            color='Type', # Colors bars based on if they are Gems or Standard
            hover_data=['Market_Size_($M)', 'I_COMMODITY', 'Value_Current'],
            color_discrete_map={'Hidden Gem 💎': '#00CC96', 'Standard Deal 📦': '#636EFA'},
            title="Growth Percentage: Standard vs. Hidden Gems"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📊 Detailed Data")
        st.dataframe(
            top_growers[['I_COMMODITY', 'I_COMMODITY_SDESC', 'Market_Size_($M)', 'Growth_%', 'Type']]
            .style.format({'Market_Size_($M)': "${:.2f}M", 'Growth_%': "{:.1f}%"})
        )
    else:
        st.warning("No categories matched your filters. Try widening the range or lowering the growth threshold.")

else:
    st.error("Data not available. Check your internet connection or API status.")