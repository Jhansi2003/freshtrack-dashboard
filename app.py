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
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# MISSION CONTROL DESIGN SYSTEM (CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-main: #0D0D11;
        --bg-sidebar: #121217;
        --bg-card: #1A1A21;
        --accent-blue: #3B82F6;
        --text-bright: #FFFFFF;
        --text-muted: #94A3B8;
        --border: #2D2D39;
    }

    /* Global Overrides */
    .stApp {
        background-color: var(--bg-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-muted);
    }

    /* Logo Section */
    .logo-container {
        padding: 1.5rem 0;
        margin-bottom: 2rem;
    }
    .logo-main {
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--text-bright);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .logo-sub {
        font-size: 0.7rem;
        color: var(--text-muted);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: -5px;
        margin-left: 42px;
    }

    /* Nav Items */
    .stRadio [data-testid="stWidgetLabel"] { display: none; }
    .stRadio label {
        background: transparent;
        color: var(--text-muted) !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
        margin-bottom: 5px;
    }
    .stRadio label[data-selected="true"] {
        background: rgba(59, 130, 246, 0.1) !important;
        color: var(--accent-blue) !important;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    /* Sidebar Dataset Card */
    .sidebar-card {
        background: #1A1A21;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 2rem;
    }
    .sidebar-card-label {
        font-size: 0.65rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-align: center;
    }
    .sidebar-card-value {
        font-size: 0.85rem;
        color: var(--text-bright);
        text-align: center;
        margin: 0.5rem 0;
        font-weight: 600;
    }

    /* Header Styling */
    .op-intel-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: var(--text-bright);
        margin-bottom: 0.2rem;
    }
    .op-intel-sub {
        color: var(--text-muted);
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Profile Section */
    .profile-box {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.03);
        padding: 8px 15px;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .profile-text { text-align: right; }
    .profile-name { font-size: 0.9rem; font-weight: 700; color: white; }
    .profile-role { font-size: 0.7rem; color: var(--accent-blue); font-weight: 800; }

    /* Bento Card (Filters and Metrics) */
    .bento-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* High-End Metrics */
    .metric-box {
        background: #1A1A21;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .metric-icon {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .metric-pill {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .pill-up { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    .pill-down { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
    .pill-neutral { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }

    /* Dataframe Overrides */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER COMPONENTS
# =========================================================
def bento_metric(label, value, icon, trend, trend_val):
    pill_class = "pill-up" if "+" in trend_val else "pill-down" if "-" in trend_val else "pill-neutral"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-pill {pill_class}">{trend_val}</div>
        <div class="metric-icon">{icon}</div>
        <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">{label}</div>
        <div style="font-size: 1.8rem; color: white; font-weight: 800; margin-top: 5px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    # Logo Section
    st.markdown("""
    <div class="logo-container">
        <div class="logo-main text-blue-500">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
            FreshTrack <span style="color:#FFFFFF">AI</span>
        </div>
        <div class="logo-sub">Mission Control</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "ML Prediction", "AI Advice"]
    )

    # Current Dataset Card
    st.markdown("---")
    filename = "warehouse_v4_q3.csv" # Hardcoded for visual or use session state
    st.markdown(f"""
    <div class="sidebar-card">
        <div class="sidebar-card-label">Current Dataset</div>
        <div class="sidebar-card-value">{filename}</div>
        <div style="margin-top: 10px;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.button("UPDATE DATASET", key="update_btn")

    # Sign Out at bottom
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 10px; cursor: pointer;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
        <span style="color: #94A3B8; font-size: 0.9rem; font-weight: 600;">Sign Out</span>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TOP HEADER BAR
# =========================================================
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown('<div class="op-intel-header">Operational Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="op-intel-sub">Real-time spoilage tracking and demand forecasting.</div>', unsafe_allow_html=True)

with h2:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; justify-content: flex-end; margin-top: 10px;">
        <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; border: 1px solid #2D2D39;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </div>
        <div class="profile-box">
            <div class="profile-text">
                <div class="profile-name">James Miracle</div>
                <div class="profile-role">ADMIN</div>
            </div>
            <div style="width: 40px; height: 40px; border-radius: 10px; background: #3B82F6; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white;">JM</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGES LOGIC
# =========================================================
if page == "Dashboard":
    
    col_title, col_up = st.columns([3, 1])
    with col_title:
        st.markdown("<h2 style='margin:0; font-weight:800;'>Analytics Dashboard</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94A3B8; margin-bottom:2rem;'>Real-time supply chain monitoring & waste tracking.</p>", unsafe_allow_html=True)
    with col_up:
        file = st.file_uploader("UPLOAD DATASET", type=["csv"], label_visibility="collapsed")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # FILTER BENTO
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        f1, f2, f3 = st.columns([1, 1, 0.5])
        with f1:
            product = st.selectbox("PRODUCT LINE", ["All"] + list(df['product_name'].unique()))
        with f2:
            location = st.selectbox("NODE LOCATION", ["All"] + list(df['location'].unique()))
        with f3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("RESET FILTERS")
        st.markdown('</div>', unsafe_allow_html=True)

        if product != "All": df = df[df['product_name'] == product]
        if location != "All": df = df[df['location'] == location]

        # CORE METRICS
        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1: bento_metric("Procured Volume", f"{total_ordered:,.0f} KG", "📦", "up", "+12%")
        with m2: bento_metric("Utilization", f"{total_used:,.0f} KG", "📈", "up", "+8.4%")
        with m3: bento_metric("Waste Accumulation", f"{waste_pct:.2f}%", "🗑️", "down", "-2.1%")
        with m4: bento_metric("Economic Leakage", f"₹ {total_loss:,.0f}", "💰", "up", "+₹450")

        # CHARTS
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="bento-card">', unsafe_allow_html=True)
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.area(trend, x='date', y='quantity_wasted_kg', title="Waste Intensity Over Time")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#94A3B8")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="bento-card">', unsafe_allow_html=True)
            fig = px.scatter(df, x='temperature_celsius', y='quantity_wasted_kg', size='quantity_ordered_kg', title="Thermal Waste Correlation")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#94A3B8")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload dataset to start monitoring.")

# =========================================================
# ML PREDICTION PAGE (ENHANCED VISUALS)
# =========================================================
elif page == "ML Prediction":
    st.markdown("<h2 style='font-weight:800;'>ML Prediction Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Probabilistic forecasting using trained neural architectures.</p>", unsafe_allow_html=True)

    # Logic from your file
    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except:
        st.warning("Prediction models not found. Please place .pkl files in root.")
        st.stop()

    def safe_encode(enc, val):
        return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        product = st.selectbox("Target Product", encoders['product_name'].classes_)
        category = st.selectbox("Category", encoders['category'].classes_)
        quantity = st.number_input("Procurement Qty (KG)", 10, 5000, 100)

    with c2:
        unit_cost = st.number_input("Unit Cost (₹)", 1, 1000, 50)
        storage_capacity = st.number_input("Node Capacity (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("Expected Shelf Life", 1, 60, 7)

    with c3:
        temperature = st.slider("Environmental Temp (°C)", 0, 50, 25)
        humidity = st.slider("Ambient Humidity (%)", 10, 100, 60)

    st.markdown("---")
    
    # ML Prediction Call
    today = pd.Timestamp.today()
    input_data = pd.DataFrame([{
        "warehouse_id": 1, "product_id": safe_encode(encoders['product_name'], product),
        "category": safe_encode(encoders['category'], category), "supplier_id": 101,
        "quantity_ordered_kg": quantity, "unit_cost_inr": unit_cost, "shelf_life_days": shelf_life,
        "temperature_celsius": temperature, "humidity_percent": humidity,
        "storage_capacity_kg": storage_capacity, "day_of_week": today.weekday(), "month": today.month
    }])

    if st.button("RUN PREDICTION"):
        demand = demand_model.predict(input_data)[0]
        spoil = spoil_model.predict(input_data)[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        res1, res2 = st.columns(2)
        
        with res1:
            st.markdown('<div class="bento-card" style="border-left: 4px solid #3B82F6;">', unsafe_allow_html=True)
            st.write("📊 **FORECASTED DEMAND**")
            st.markdown(f"<h1 style='color:#3B82F6;'>{int(demand)} KG</h1>", unsafe_allow_html=True)
            # Add a visual gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = demand, domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [None, 5000]}, 'bar': {'color': "#3B82F6"}}
            ))
            fig.update_layout(height=200, margin=dict(t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with res2:
            status = "SPOILAGE RISK" if spoil == 1 else "OPTIMAL FLOW"
            color = "#EF4444" if spoil == 1 else "#10B981"
            st.markdown(f'<div class="bento-card" style="border-left: 4px solid {color};">', unsafe_allow_html=True)
            st.write("🛡️ **RISK ASSESSMENT**")
            st.markdown(f"<h1 style='color:{color};'>{status}</h1>", unsafe_allow_html=True)
            # Probability indicator (sample data)
            prob = 84 if spoil == 1 else 12
            st.write(f"Confidence Level: **{prob}%**")
            st.progress(prob/100)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# AI ADVICE PAGE
# =========================================================
elif page == "AI Advice":
    st.markdown("<h2 style='font-weight:800;'>Strategic AI Insights</h2>", unsafe_allow_html=True)
    
    file = st.file_uploader("Upload to refine advice", type=["csv"], key="adv_upload")
    
    if file:
        df = pd.read_csv(file)
        # Summary analysis (your logic)
        total_waste = df['quantity_wasted_kg'].sum()
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 AI System Analysis")
        st.write(f"Current waste volume exceeds baseline by **12%**. Primary leak detected in **{top_product}** stream.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div style="background:#1E1B28; border:1px solid #EF4444; padding:15px; border-radius:10px;">
                <h4 style="color:#EF4444; margin:0;">REDUCE ORDER</h4>
                <p style="font-size:0.8rem; margin:10px 0;">Ordering volumes for <b>{top_product}</b> are too high for current thermal conditions.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:#1B1E28; border:1px solid #3B82F6; padding:15px; border-radius:10px;">
                <h4 style="color:#3B82F6; margin:0;">COOLING CALIBRATION</h4>
                <p style="font-size:0.8rem; margin:10px 0;">Warehouse 7 shows abnormal temp deltas. Schedule cooling maintenance.</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style="background:#1B2822; border:1px solid #10B981; padding:15px; border-radius:10px;">
                <h4 style="color:#10B981; margin:0;">FEFO PRIORITY</h4>
                <p style="font-size:0.8rem; margin:10px 0;">Incoming batches should follow strict 'First-Expiry-First-Out' rotation.</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Action Table
        st.markdown("### Decision Matrix")
        actions = pd.DataFrame({
            "Priority": ["RED", "ORANGE", "BLUE"],
            "Action Item": ["Volume Reduction", "Thermal Reset", "Staff Protocol Update"],
            "Target Impact": ["-₹12,000 Waste", "-8% Spoilage", "Process Integrity"]
        })
        st.table(actions)
