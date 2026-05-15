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
    page_title="FreshTrack AI | Premium Logistics",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# BLUE & WHITE PREMIUM DESIGN SYSTEM (CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #1e40af;    /* Deep Blue */
        --accent: #3b82f6;     /* Bright Blue */
        --bg-main: #f8fafc;    /* Very Light Blue/Gray */
        --card-white: #ffffff;
        --border-soft: #e2e8f0;
        --text-dark: #0f172a;
        --text-muted: #64748b;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--bg-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Logo Positioning */
    [data-testid="stSidebarNav"]::before {
        content: "";
        background-image: url("miracle_logo.png");
        background-repeat: no-repeat;
        background-size: contain;
        display: block;
        margin: 20px auto;
        width: 200px;
        height: 60px;
    }

    /* Modern Container Cards */
    .glass-card {
        background: var(--card-white);
        border: 1px solid var(--border-soft);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }

    /* Metric Styling */
    .metric-card {
        padding: 20px;
        background: white;
        border-radius: 16px;
        border: 1px solid #f1f5f9;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        border-color: var(--accent);
        transform: translateY(-4px);
    }
    .metric-label { 
        color: var(--text-muted); 
        font-size: 0.85rem; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 0.025em;
    }
    .metric-value { 
        color: var(--primary); 
        font-size: 1.8rem; 
        font-weight: 700; 
        margin-top: 4px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid var(--border-soft);
    }
    
    /* Recommendations - Colored Tiles */
    .rec-tile {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid transparent;
        height: 100%;
    }
    .blue-tile { background: #eff6ff; border-color: #dbeafe; color: #1e3a8a; }
    .sky-tile { background: #f0f9ff; border-color: #e0f2fe; color: #0369a1; }
    .indigo-tile { background: #eef2ff; border-color: #e0e7ff; color: #3730a3; }

    /* Custom Button */
    .stButton > button {
        background: var(--primary);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: var(--accent);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }

    /* Input Overrides */
    div[data-baseweb="select"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# UTILITIES
# =========================================================
def create_stat(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def chart_theme(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Plus Jakarta Sans",
        margin=dict(t=40, b=20, l=40, r=20),
        colorway=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd']
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    return fig

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "MAIN NAVIGATION",
    ["Executive Dashboard", "Predictive Intelligence", "Strategic Recommendations"]
)

# =========================================================
# DASHBOARD
# =========================================================
if page == "Executive Dashboard":
    st.markdown('<h1 style="color: #0f172a; font-weight: 800; margin-bottom: 0;">Supply Chain Telemetry</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b; margin-top: 0; margin-bottom: 2rem;">Holistic view of waste patterns and operational performance.</p>', unsafe_allow_html=True)

    file = st.file_uploader("Ingest Telemetry Data (CSV)", type=["csv"], key="dashboard_upload")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Sidebar Filters (Compact)
        with st.sidebar:
            st.markdown("### Filters")
            product = st.selectbox("Filter Product", ["All Products"] + list(df['product_name'].unique()))
            location = st.selectbox("Filter Location", ["All Locations"] + list(df['location'].unique()))
            date_range = st.date_input("Filter Date Range", [df['date'].min(), df['date'].max()])

        # Apply Filters
        if product != "All Products": df = df[df['product_name'] == product]
        if location != "All Locations": df = df[df['location'] == location]
        if len(date_range) == 2:
            df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]

        # KPIs row
        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1: create_stat("Total Procured", f"{total_ordered:,.0f}")
        with m2: create_stat("Net Loss", f"₹ {total_loss:,.0f}")
        with m3: create_stat("Waste Efficiency", f"{waste_pct:.1f}%")
        with m4: create_stat("Avg Location Temperature", f"{df['temperature_celsius'].mean():.1f}°C")

        st.markdown("<br>", unsafe_allow_html=True)

        # Dashboard Visuals
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Waste Dynamics Over Time")
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.area(trend, x='date', y='quantity_wasted_kg', color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(chart_theme(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Waste Intensity Heatmap")
            # Added a Heatmap: Product vs Location Waste
            heatmap_data = df.groupby(['product_name', 'location'])['quantity_wasted_kg'].sum().unstack().fillna(0)
            fig = px.imshow(heatmap_data, color_continuous_scale='Blues', text_auto=True)
            st.plotly_chart(chart_theme(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Added Visual: Distribution Box Plot
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Volume Variability by Product")
        fig = px.box(df, x='product_name', y='quantity_ordered_kg', color='product_name', notched=True)
        st.plotly_chart(chart_theme(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("System Ready. Please upload a supply chain dataset to populate telemetry.")

# =========================================================
# PREDICTION
# =========================================================
elif page == "Predictive Intelligence":
    st.markdown('<h1 style="color: #0f172a; font-weight: 800;">Risk Prediction Engine</h1>', unsafe_allow_html=True)

    # Simulation context (keeps variables matching previous script)
    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except:
        st.error("Model artifacts (pkl files) not detected. Please verify presence of model files.")
        st.stop()

    def safe_encode(enc, val): return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c_in1, c_in2, c_in3 = st.columns(3)
    
    with c_in1:
        product = st.selectbox("Product Node", encoders['product_name'].classes_)
        category = st.selectbox("Strategic Category", encoders['category'].classes_)
        quantity = st.number_input("Input Quantity (KG)", 10, 10000, 100)

    with c_in2:
        unit_cost = st.number_input("Economic Cost (₹)", 1, 5000, 50)
        storage_capacity = st.number_input("Buffer Capacity (KG)", 100, 20000, 2000)
        shelf_life = st.number_input("Stability Window (Days)", 1, 90, 7)

    with c_in3:
        temperature = st.slider("Target Temp (°C)", 0, 50, 25)
        humidity = st.slider("Ambience Humidity (%)", 10, 100, 60)

    st.markdown("</div>", unsafe_allow_html=True)

    # Prediction Build
    today = pd.Timestamp.today()
    input_data = pd.DataFrame([{
        "warehouse_id": 1, "product_id": safe_encode(encoders['product_name'], product),
        "category": safe_encode(encoders['category'], category), "supplier_id": 101,
        "quantity_ordered_kg": quantity, "unit_cost_inr": unit_cost, "shelf_life_days": shelf_life,
        "temperature_celsius": temperature, "humidity_percent": humidity, "storage_capacity_kg": storage_capacity,
        "day_of_week": today.weekday(), "month": today.month
    }])
    
    # Matching exact feature names
    input_data = input_data[['warehouse_id', 'product_id', 'category', 'supplier_id', 'quantity_ordered_kg', 
                           'unit_cost_inr', 'shelf_life_days', 'temperature_celsius', 'humidity_percent', 
                           'storage_capacity_kg', 'day_of_week', 'month']]

    if st.button("EXECUTE PREDICTIVE ANALYSIS"):
        with st.spinner("Analyzing data patterns..."):
            demand = demand_model.predict(input_data)[0]
            spoil = spoil_model.predict(input_data)[0]
            
            st.markdown("<br>", unsafe_allow_html=True)
            res_left, res_right = st.columns([1, 1])
            
            with res_left:
                st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
                st.markdown("### Demand Forecast")
                st.markdown(f'<h1 style="color: #1e40af; font-size: 3.5rem;">{int(demand)}</h1>', unsafe_allow_html=True)
                st.markdown('<p style="color: #64748b;">Optimized KG Procurement</p>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with res_right:
                st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
                st.markdown("### Risk Probability Gauge")
                # Added New Visual: Gauge Chart for Spoilage Risk
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = 85 if spoil == 1 else 15,
                    title = {'text': "Spoilage Likelihood"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#1e3a8a"},
                        'steps': [
                            {'range': [0, 30], 'color': "#dcfce7"},
                            {'range': [30, 70], 'color': "#fef3c7"},
                            {'range': [70, 100], 'color': "#fee2e2"}
                        ],
                    }
                ))
                st.plotly_chart(chart_theme(fig_gauge), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Strategic Recommendations":
    st.markdown('<h1 style="color: #0f172a; font-weight: 800;">AI Optimization Center</h1>', unsafe_allow_html=True)

    file = st.file_uploader("Upload Data for Insight Extraction", type=["csv"], key="rec_upload")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Data aggregation
        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()
        avg_temp = df['temperature_celsius'].mean()

        # Modern Tile row
        st.markdown("### Top Priority Interventions")
        t1, t2, t3, t4 = st.columns(4)
        
        with t1:
            st.markdown(f"""<div class="rec-tile blue-tile"><strong>Product Risk</strong><br>Adjust procurement for <b>{top_product}</b> to mitigate {waste_pct:.1f}% waste rate.</div>""", unsafe_allow_html=True)
        with t2:
            st.markdown(f"""<div class="rec-tile sky-tile"><strong>Node Leakage</strong><br><b>{top_location}</b> identified as thermal loss center. Check facility cooling.</div>""", unsafe_allow_html=True)
        with t3:
            st.markdown(f"""<div class="rec-tile indigo-tile"><strong>Thermal Pulse</strong><br>Operating at <b>{avg_temp:.1f}°C</b>. {"Deploy active cooling." if avg_temp > 28 else "Stable thermal state."}</div>""", unsafe_allow_html=True)
        with t4:
            st.markdown(f"""<div class="rec-tile blue-tile"><strong>Velocity Plan</strong><br>Accelerate inventory turnover for items with <7 day shelf life.</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphs
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.markdown("#### Financial Leakage by Node")
            fig = px.pie(df.groupby('location')['loss_amount_inr'].sum().reset_index(), names='location', values='loss_amount_inr', hole=0.5)
            st.plotly_chart(chart_theme(fig), use_container_width=True)
        with c_v2:
            st.markdown("#### Waste Volume Contribution")
            # Added a Funnel Chart for waste contribution
            funnel_data = df.groupby('product_name')['quantity_wasted_kg'].sum().sort_values(ascending=False).head(5).reset_index()
            fig = px.funnel(funnel_data, x='quantity_wasted_kg', y='product_name')
            st.plotly_chart(chart_theme(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Final Table
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Smart Procurement Schedule")
        plan = pd.DataFrame({
            "Logic Type": ["Demand Driven", "Risk Based", "Facility Opt.", "Temporal"],
            "Target Group": [top_product, "High Spoilage Items", top_location, "Weekend Buffer"],
            "AI Recommendation": [f"Cap orders at {int(total_ordered*0.8)}kg", "Trigger secondary scan", "Check insulation seals", "Advance 24hr delivery"]
        })
        st.table(plan)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("System online. Standby for data ingestion.")
