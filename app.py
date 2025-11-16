import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="US Import Trend Hunter", layout="wide")

# --- HS CHAPTERS ---
HS_CHAPTERS = {
    "All Chapters": "ALL",
    "01 - Live animals": "01",
    "02 - Meat and edible meat offal": "02",
    "03 - Fish and crustaceans, molluscs": "03",
    "04 - Dairy produce; birds' eggs; natural honey": "04",
    "05 - Products of animal origin, not elsewhere specified": "05",
    "06 - Live trees and other plants; bulbs, roots": "06",
    "07 - Edible vegetables and certain roots and tubers": "07",
    "08 - Edible fruit and nuts; peel of citrus fruit or melons": "08",
    "09 - Coffee, tea, maté and spices": "09",
    "10 - Cereals": "10",
    "11 - Products of the milling industry; malt; starches": "11",
    "12 - Oil seeds and oleaginous fruits; miscellaneous grains": "12",
    "13 - Lac; gums, resins and other vegetable saps": "13",
    "14 - Vegetable plaiting materials; vegetable products n.e.s.": "14",
    "15 - Animal or vegetable fats and oils": "15",
    "16 - Preparations of meat, of fish or of crustaceans": "16",
    "17 - Sugars and sugar confectionery": "17",
    "18 - Cocoa and cocoa preparations": "18",
    "19 - Preparations of cereals, flour, starch or milk": "19",
    "20 - Preparations of vegetables, fruit, nuts": "20",
    "21 - Miscellaneous edible preparations": "21",
    "22 - Beverages, spirits and vinegar": "22",
    "23 - Residues and waste from the food industries; animal fodder": "23",
    "24 - Tobacco and manufactured tobacco substitutes": "24",
    "25 - Salt; sulphur; earths and stone; plastering materials": "25",
    "26 - Ores, slag and ash": "26",
    "27 - Mineral fuels, mineral oils and products of their distillation": "27",
    "28 - Inorganic chemicals; organic or inorganic compounds": "28",
    "29 - Organic chemicals": "29",
    "30 - Pharmaceutical products": "30",
    "31 - Fertilizers": "31",
    "32 - Tanning or dyeing extracts; tannins and their derivatives": "32",
    "33 - Essential oils and resinoids; perfumery, cosmetic or toilet prep": "33",
    "34 - Soap, organic surface-active agents, washing prep": "34",
    "35 - Albuminoidal substances; modified starches; glues": "35",
    "36 - Explosives; pyrotechnic products; matches": "36",
    "37 - Photographic or cinematographic goods": "37",
    "38 - Miscellaneous chemical products": "38",
    "39 - Plastics and articles thereof": "39",
    "40 - Rubber and articles thereof": "40",
    "41 - Raw hides and skins (other than furskins) and leather": "41",
    "42 - Articles of leather; saddlery and harness": "42",
    "43 - Furskins and artificial fur; manufactures thereof": "43",
    "44 - Wood and articles of wood; wood charcoal": "44",
    "45 - Cork and articles of cork": "45",
    "46 - Manufactures of straw, of esparto or of other plaiting materials": "46",
    "47 - Pulp of wood or of other fibrous cellulosic material": "47",
    "48 - Paper and paperboard; articles of paper pulp": "48",
    "49 - Printed books, newspapers, pictures and other products": "49",
    "50 - Silk": "50",
    "51 - Wool, fine or coarse animal hair; horsehair yarn": "51",
    "52 - Cotton": "52",
    "53 - Other vegetable textile fibers; paper yarn": "53",
    "54 - Man-made filaments": "54",
    "55 - Man-made staple fibers": "55",
    "56 - Wadding, felt and nonwovens; special yarns": "56",
    "57 - Carpets and other textile floor coverings": "57",
    "58 - Special woven fabrics; tufted textile fabrics; lace": "58",
    "59 - Impregnated, coated, covered or laminated textile fabrics": "59",
    "60 - Knitted or crocheted fabrics": "60",
    "61 - Articles of apparel and clothing accessories, knitted": "61",
    "62 - Articles of apparel and clothing accessories, not knitted": "62",
    "63 - Other made up textile articles; sets; worn clothing": "63",
    "64 - Footwear, gaiters and the like; parts of such articles": "64",
    "65 - Headgear and parts thereof": "65",
    "66 - Umbrellas, sun umbrellas, walking-sticks, seat-sticks": "66",
    "67 - Prepared feathers and down and articles made of feathers": "67",
    "68 - Articles of stone, plaster, cement, asbestos, mica": "68",
    "69 - Ceramic products": "69",
    "70 - Glass and glassware": "70",
    "71 - Natural or cultured pearls, precious or semi-precious stones": "71",
    "72 - Iron and steel": "72",
    "73 - Articles of iron or steel": "73",
    "74 - Copper and articles thereof": "74",
    "75 - Nickel and articles thereof": "75",
    "76 - Aluminum and articles thereof": "76",
    "78 - Lead and articles thereof": "78",
    "79 - Zinc and articles thereof": "79",
    "80 - Tin and articles thereof": "80",
    "81 - Other base metals; cermets; articles thereof": "81",
    "82 - Tools, implements, cutlery, spoons and forks, of base metal": "82",
    "83 - Miscellaneous articles of base metal": "83",
    "84 - Nuclear reactors, boilers, machinery and mechanical appliances": "84",
    "85 - Electrical machinery and equipment and parts thereof": "85",
    "86 - Railway or tramway locomotives, rolling-stock and parts": "86",
    "87 - Vehicles other than railway or tramway rolling-stock": "87",
    "88 - Aircraft, spacecraft, and parts thereof": "88",
    "89 - Ships, boats and floating structures": "89",
    "90 - Optical, photographic, cinematographic, measuring, precision": "90",
    "91 - Clocks and watches and parts thereof": "91",
    "92 - Musical instruments; parts and accessories of such articles": "92",
    "93 - Arms and ammunition; parts and accessories thereof": "93",
    "94 - Furniture; bedding, mattresses, mattress supports, cushions": "94",
    "95 - Toys, games and sports requisites; parts and accessories": "95",
    "96 - Miscellaneous manufactured articles": "96",
    "97 - Works of art, collectors' pieces and antiques": "97",
}

# --- FETCH FUNCTION ---
@st.cache_data
def fetch_census_data(year, months):
    base_url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
    hs_level = "HS4" 
    
    all_data = []
    
    progress_text = f"Fetching data for {year}..."
    my_bar = st.progress(0, text=progress_text)
    
    for i, month in enumerate(months):
        time_str = f"{year}-{month}"
        
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
            df = df.loc[:, ~df.columns.duplicated()] # Fix Duplicate Columns
            all_data.append(df)
        except Exception as e:
            st.error(f"⚠️ Error on {time_str}: {str(e)}")
        
        my_bar.progress((i + 1) / len(months), text=progress_text)

    my_bar.empty() 

    if not all_data:
        return pd.DataFrame()

    full_df = pd.concat(all_data)
    full_df['GEN_VAL_MO'] = pd.to_numeric(full_df['GEN_VAL_MO'])
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

st.sidebar.header("2. Category Filter")
selected_chapter_name = st.sidebar.selectbox("Filter by HS Chapter", options=list(HS_CHAPTERS.keys()))
selected_chapter_code = HS_CHAPTERS[selected_chapter_name]

st.sidebar.header("3. Volume Filter")
vol_range = st.sidebar.slider("Volume Range ($M)", 0.0, 500.0, (1.0, 100.0), step=0.5)
min_vol_raw = vol_range[0] * 1_000_000
max_vol_raw = vol_range[1] * 1_000_000

st.sidebar.header("4. Niche Hunter")
show_gems = st.sidebar.checkbox("Include Low-Vol / High-Growth Gems?", value=True)
gem_growth_threshold = 0
if show_gems:
    gem_growth_threshold = st.sidebar.slider("Min Growth % for Gems", 50, 1000, 200)

# --- MAIN APP LOGIC ---
st.title(f"🇺🇸 Import Scout: {quarter} {current_year}")
st.markdown(f"**Category:** {selected_chapter_name}")

col1, col2 = st.columns(2)
with col1:
    st.info(f"Fetching {current_year}...")
    df_curr = fetch_census_data(current_year, target_months)
with col2:
    st.info(f"Fetching {prior_year}...")
    df_prev = fetch_census_data(prior_year, target_months)

if not df_curr.empty and not df_prev.empty:
    df_curr.rename(columns={'GEN_VAL_MO': 'Value_Current'}, inplace=True)
    df_prev.rename(columns={'GEN_VAL_MO': 'Value_Prior'}, inplace=True)
    
    merged = pd.merge(df_curr, df_prev[['I_COMMODITY', 'Value_Prior']], on='I_COMMODITY', how='inner')
    
    # --- CHAPTER FILTERING LOGIC ---
    merged['Chapter_Code'] = merged['I_COMMODITY'].str[:2]
    if selected_chapter_code != "ALL":
        merged = merged[merged['Chapter_Code'] == selected_chapter_code].copy()
    
    if not merged.empty:
        merged['Growth_%'] = ((merged['Value_Current'] - merged['Value_Prior']) / merged['Value_Prior']) * 100
        merged['Market_Size_($M)'] = merged['Value_Current'] / 1_000_000
        
        mask_standard = (merged['Value_Current'] >= min_vol_raw) & (merged['Value_Current'] <= max_vol_raw)
        mask_gems = (
            (merged['Value_Current'] < min_vol_raw) & 
            (merged['Value_Current'] > 5000) & 
            (merged['Growth_%'] >= gem_growth_threshold)
        )
        
        if show_gems:
            filtered = merged[mask_standard | mask_gems].copy()
            filtered['Type'] = filtered.apply(
                lambda x: 'Hidden Gem 💎' if (x['Value_Current'] < min_vol_raw) else 'Standard Deal 📦', axis=1
            )
        else:
            filtered = merged[mask_standard].copy()
            filtered['Type'] = 'Standard Deal 📦'

        top_growers = filtered.sort_values(by='Growth_%', ascending=False).head(20)
        
        if not top_growers.empty:
            st.subheader(f"Top Opportunities in Chapter {selected_chapter_code}")
            fig_bar = px.bar(
                top_growers, 
                x='Growth_%', 
                y='I_COMMODITY_SDESC', 
                orientation='h',
                color='Type',
                hover_data=['Market_Size_($M)', 'I_COMMODITY'],
                color_discrete_map={'Hidden Gem 💎': '#00CC96', 'Standard Deal 📦': '#636EFA'}
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # --- DATA TABLE & DOWNLOAD BUTTON ---
            st.write("### 📋 Detailed Data")
            st.dataframe(
                top_growers[['I_COMMODITY', 'I_COMMODITY_SDESC', 'Market_Size_($M)', 'Growth_%', 'Type']]
                .style.format({'Market_Size_($M)': "${:.2f}M", 'Growth_%': "{:.1f}%"})
            )
            
            # PREPARE CSV
            # We export 'filtered' (all matches) so the user gets more than just the top 20
            csv_data = filtered[['I_COMMODITY', 'I_COMMODITY_SDESC', 'Value_Current', 'Value_Prior', 'Growth_%', 'Type']].to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Full Report (CSV)",
                data=csv_data,
                file_name=f'import_opps_{selected_chapter_code}_{current_year}.csv',
                mime='text/csv',
            )
            
        else:
            st.warning(f"No items found in Chapter {selected_chapter_code} matching your filters.")
    else:
        st.warning(f"No data found for Chapter {selected_chapter_code}.")
else:
    st.error("Data not available.")
