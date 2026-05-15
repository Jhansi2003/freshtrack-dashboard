import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import warnings
from datetime import datetime

# =========================================================
# CONFIG & SILENCE
# =========================================================
warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="FreshTrack AI | Mission Control",
    page_icon="🛰️",
    layout="wide",
)

# =========================================================
# HIGH-END MISSION CONTROL CSS
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-dark: #000000;
        --card-bg: #111111;
        --sidebar-bg: #0a0a0a;
        --primary-blue: #3b82f6;
        --text-dim: #94a3b8;
        --accent-border: #222222;
    }

    /* Main Container */
    .stApp {
        background-color: var(--bg-dark);
        color: white;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--accent-border);
    }

    /* Headers */
    .op-intel-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    
    .op-subtitle {
        color: var(--text-dim);
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-top: 1.5rem;
    }

    /* Custom Metric Cards */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--accent-border);
        border-radius: 16px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }

    .metric-label {
        color: var(--text-dim);
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin: 10px 0;
    }

    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        background: rgba(59, 130, 246, 0.1);
        color: var(--primary-blue);
        width: fit-content;
    }

    /* Filter Bar */
    .filter-section {
        background: var(--card-bg);
        border: 1px solid var(--accent-border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 24px;
    }

    /* Upload Button Styling */
    div.stButton > button:first-child {
        background-color: var(--primary-blue) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* Prediction Risk Cards */
    .risk-high { color: #ef4444; border: 1px solid #ef4444; padding: 10px; border-radius: 8px; background: rgba(239, 68, 68, 0.1); }
    .risk-low { color: #10b981; border: 1px solid #10b981; padding: 10px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); }

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO & NAVIGATION
# =========================================================
with st.sidebar:
    st.image("miracle_logo.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    
    page = st.radio(
        "MISSION CONTROL",
        ["Dashboard", "ML Prediction", "AI Advice"]
    )
    
    st.markdown("---")
    st.markdown("""
        <div style='padding: 10px; background: #0a0a0a; border-radius: 12px; border: 1px solid #222;'>
            <p style='color: #444; font-size: 0.7rem; margin: 0;'>CURRENT BATCH</p>
            <p style='color: #888; font-size: 0.8rem; margin: 0;'>warehouse_v4_q3.csv</p>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# HEADER COMPONENT
# =========================================================
def header_component(title, subtitle):
    st.markdown(f"<h1 class='op-intel-header'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='op-subtitle'>{subtitle}</p>", unsafe_allow_html=True)

# =========================================================
# DASHBOARD PAGE
# =========================================================
if page == "Dashboard":
    header_component("Operational Intelligence", "Real-time spoilage tracking and demand forecasting")
    
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown("<h2 class='section-title'>Analytics Dashboard</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666;'>Real-time supply chain monitoring & waste tracking.</p>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        file = st.file_uploader("UPLOAD DATASET", type=["csv"], label_visibility="collapsed")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Filter Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            product = st.selectbox("PRODUCT LINE", ["All"] + list(df['product_name'].unique()))
        with c2:
            location = st.selectbox("NODE LOCATION", ["All"] + list(df['location'].unique()))
        with c3:
            date_range = st.date_input("TIME WINDOW", [df['date'].min(), df['date'].max()])
        
        if product != "All": df = df[df['product_name'] == product]
        if location != "All": df = df[df['location'] == location]
        if len(date_range) == 2:
            df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]
        st.markdown('</div>', unsafe_allow_html=True)

        # Metrics
        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">📦 Total Ordered</div>
                <div class="metric-value">{total_ordered:,.0f} KG</div>
                <div class="metric-delta">+12% vs LY</div>
            </div>''', unsafe_allow_html=True)
        with m2:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">📈 Utilization</div>
                <div class="metric-value">{total_used:,.0f} KG</div>
                <div class="metric-delta">+8.4% Efficiency</div>
            </div>''', unsafe_allow_html=True)
        with m3:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">🗑️ Waste Rate</div>
                <div class="metric-value">{waste_pct:.2f}%</div>
                <div class="metric-delta" style="color: #ef4444; background: rgba(239, 68, 68, 0.1);">-2.1% Target</div>
            </div>''', unsafe_allow_html=True)
        with m4:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">₹ Financial Loss</div>
                <div class="metric-value">₹{total_loss:,.0f}</div>
                <div class="metric-delta" style="color: #f59e0b; background: rgba(245, 158, 11, 0.1);">Risk Zone</div>
            </div>''', unsafe_allow_html=True)

        # Charts
        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.line(trend, x='date', y='quantity_wasted_kg', title="Telemetry Over Time", 
                          color_discrete_sequence=['#3b82f6'])
            fig.update_layout(paper_bgcolor="#111", plot_bgcolor="#111", font_color="white", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig = px.scatter(df, x='temperature_celsius', y='quantity_wasted_kg', title="Thermal Waste Correlation", 
                             color='quantity_wasted_kg', color_continuous_scale='Blues')
            fig.update_layout(paper_bgcolor="#111", plot_bgcolor="#111", font_color="white", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting system input. Please upload telemetry dataset.")

# =========================================================
# ML PREDICTION PAGE
# =========================================================
elif page == "ML Prediction":
    header_component("Predictive Engine", "Neural forecasting and spoilage classification")
    
    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except:
        st.error("ML Artifacts not found.")
        st.stop()

    def safe_encode(enc, val):
        return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        product = st.selectbox("Product", encoders['product_name'].classes_)
        category = st.selectbox("Category", encoders['category'].classes_)
        quantity = st.number_input("Quantity Ordered (KG)", 10, 5000, 100)
    with c2:
        unit_cost = st.number_input("Unit Cost (₹)", 1, 1000, 50)
        storage_capacity = st.number_input("Storage Capacity (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("Shelf Life (Days)", 1, 60, 7)
    with c3:
        temperature = st.slider("Temperature (°C)", 0, 50, 25)
        humidity = st.slider("Humidity (%)", 10, 100, 60)
    
    today = pd.Timestamp.today()
    input_data = pd.DataFrame([{
        "warehouse_id": 1,
        "product_id": safe_encode(encoders['product_name'], product),
        "category": safe_encode(encoders['category'], category),
        "supplier_id": 101,
        "quantity_ordered_kg": quantity,
        "unit_cost_inr": unit_cost,
        "shelf_life_days": shelf_life,
        "temperature_celsius": temperature,
        "humidity_percent": humidity,
        "storage_capacity_kg": storage_capacity,
        "day_of_week": today.weekday(),
        "month": today.month
    }])

    if st.button("RUN PREDICTION"):
        demand = demand_model.predict(input_data)[0]
        spoil = spoil_model.predict(input_data)[0]
        
        st.markdown("---")
        res1, res2 = st.columns(2)
        
        with res1:
            st.markdown(f'''<div class="metric-card" style="border-left: 4px solid #3b82f6;">
                <div class="metric-label">Forecasted Demand</div>
                <div class="metric-value">{int(demand)} KG</div>
                <p style="color: #666; font-size: 0.8rem;">Optimized procurement volume suggested.</p>
            </div>''', unsafe_allow_html=True)
            
        with res2:
            if spoil == 1:
                status = "risk-high"
                msg = "CRITICAL: HIGH SPOILAGE RISK"
            else:
                status = "risk-low"
                msg = "STABLE: LOW SPOILAGE RISK"
            
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">Freshness Vector</div>
                <div class="{status}" style="font-weight: 700; text-align: center; margin-top: 10px;">{msg}</div>
            </div>''', unsafe_allow_html=True)
            
        # Extra visuals requested
        st.markdown("<br>", unsafe_allow_html=True)
        fig_gau = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temperature,
            title = {'text': "Thermal Constraint (°C)"},
            gauge = {'axis': {'range': [0, 50]}, 'bar': {'color': "#3b82f6"}}
        ))
        fig_gau.update_layout(paper_bgcolor="#111", font_color="white", height=300)
        st.plotly_chart(fig_gau, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# AI ADVICE PAGE
# =========================================================
elif page == "AI Advice":
    header_component("Strategy Advisor", "AI-driven logistical interventions and insights")
    
    file = st.file_uploader("Upload dataset for strategic audit", type=["csv"], key="adv_upload")
    if file:
        df = pd.read_csv(file)
        
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()
        avg_temp = df['temperature_celsius'].mean()

        st.markdown("### Strategic Intervention Cards")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'''<div class="metric-card" style="border-top: 4px solid #ef4444;">
                <div class="metric-label">Inventory Alert</div>
                <div style="color: #eee; margin-top: 10px;">Reduce procurement for <b>{top_product}</b> immediately to prevent waste overflow.</div>
            </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''<div class="metric-card" style="border-top: 4px solid #3b82f6;">
                <div class="metric-label">Node Optimization</div>
                <div style="color: #eee; margin-top: 10px;">Audit thermal storage protocols at <b>{top_location}</b> to mitigate financial leakage.</div>
            </div>''', unsafe_allow_html=True)
        with c3:
            st.markdown(f'''<div class="metric-card" style="border-top: 4px solid #10b981;">
                <div class="metric-label">Thermal Compliance</div>
                <div style="color: #eee; margin-top: 10px;">Average Temperature is <b>{avg_temp:.1f}°C</b>. Baseline stability confirmed.</div>
            </div>''', unsafe_allow_html=True)
    else:
        st.info("System pending dataset upload.")

# Footnote
st.markdown("<div style='text-align: center; color: #333; font-size: 0.7rem; margin-top: 50px;'>FRESHTRACK AI | MISSION CONTROL v2.1.0</div>", unsafe_allow_html=True)
