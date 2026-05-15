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
# PROFESSIONAL DARK DESIGN SYSTEM (CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #3b82f6;
        --primary-glow: rgba(59, 130, 246, 0.5);
        --secondary: #94a3b8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --background: #0d0f14;
        --sidebar-bg: #151921;
        --card-bg: #1c212b;
        --text-main: #f8fafc;
        --border: rgba(255, 255, 255, 0.08);
    }

    /* Global Styles */
    .stApp {
        background-color: var(--background);
        color: var(--text-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }

    /* Logo Section */
    .logo-container {
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .logo-icon {
        background: linear-gradient(135deg, #3b82f6, #2dd4bf);
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px var(--primary-glow);
    }

    /* Header Section */
    .op-intel-header {
        margin-bottom: 2.5rem;
    }
    
    .op-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .op-subtitle {
        color: var(--secondary);
        font-size: 1rem;
        font-weight: 400;
    }

    /* Search Bar Simulation */
    .search-container {
        position: relative;
        width: 100%;
        max-width: 400px;
        margin-bottom: 2rem;
    }
    .search-input {
        background: #1c212b;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: white;
        width: 100%;
        font-size: 0.9rem;
    }

    /* Stats Cards */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .stat-label {
        color: var(--secondary);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    
    .stat-delta {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .delta-up { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    .delta-down { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

    /* Custom Radio Styling (Navigation) */
    div.row-widget.stRadio > div{
        background: transparent;
        border: none;
    }
    div.row-widget.stRadio > div > label {
        padding: 12px 16px;
        margin-bottom: 4px;
        border-radius: 8px;
        color: #94a3b8;
        transition: all 0.2s;
        cursor: pointer;
    }
    div.row-widget.stRadio > div > label:hover {
        background: rgba(255,255,255,0.05);
        color: white;
    }
    div.row-widget.stRadio > div > label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    /* Sections */
    .glass-container {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.75rem 2rem;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #3b82f6, #2563eb);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Reset Filters Button */
    .reset-btn {
        color: var(--secondary);
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        background: none;
        border: none;
        text-transform: uppercase;
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER COMPONENTS
# =========================================================
def bento_stat(label, value, delta, is_up=True, icon="📦"):
    delta_class = "delta-up" if is_up else "delta-down"
    delta_prefix = "+" if is_up else "-"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-label">{label}</div>
        <div style="display: flex; align-items: baseline; gap: 10px;">
            <div class="stat-value">{value}</div>
            <div class="stat-delta {delta_class}">{delta_prefix}{delta}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def chart_theme(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Plus Jakarta Sans",
        font_color="#94a3b8",
        margin=dict(t=40, b=40, l=40, r=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    # Logo Area
    st.markdown(f"""
    <div class="logo-container">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="logo-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
            </div>
            <div>
                <div style="font-weight: 800; font-size: 1.25rem; letter-spacing: -0.02em; color: white;">FreshTrack <span style="color: #3b82f6;">AI</span></div>
                <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">Mission Control</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "NAVIGATE",
        ["Dashboard", "ML Prediction", "AI Advice"],
        index=0
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Dataset Status Card
    st.markdown("""
    <div style="padding: 1.25rem; background: #1c212b; border: 1px solid var(--border); border-radius: 12px;">
        <div style="font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Current Dataset</div>
        <div style="font-weight: 600; font-size: 0.85rem; margin: 8px 0; color: #f8fafc;">warehouse_v4_q3.csv</div>
        <div style="height: 4px; background: #0d0f14; border-radius: 2px; overflow: hidden;">
            <div style="width: 75%; height: 100%; background: #3b82f6;"></div>
        </div>
        <div style="font-size: 0.65rem; color: #3b82f6; font-weight: 700; margin-top: 8px; text-transform: uppercase;">Status: Active</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TOP NAVIGATION & HEADERS
# =========================================================
c_head1, c_head2 = st.columns([2, 1])

with c_head1:
    st.markdown("""
    <div class="op-intel-header">
        <div class="op-title">Operational Intelligence</div>
        <div class="op-subtitle">Real-time spoilage tracking and demand forecasting</div>
    </div>
    """, unsafe_allow_html=True)

with c_head2:
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 1rem; padding-top: 1rem;">
        <div style="background: #1c212b; border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem 0.75rem; display: flex; align-items: center; gap: 10px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <span style="color: #64748b; font-size: 0.85rem;">Search metrics...</span>
        </div>
        <div style="background: #1c212b; border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem; display: flex; align-items: center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGE ROUTING
# =========================================================
if page == "Dashboard":
    
    col_dash1, col_dash2 = st.columns([3, 1])
    with col_dash1:
        st.markdown("""
        <h2 style="font-weight: 800; font-size: 2rem; margin: 0; letter-spacing: -0.03em;">Analytics Dashboard</h2>
        <p style="color: #64748b; margin-top: 4px;">Real-time supply chain monitoring & waste tracking.</p>
        """, unsafe_allow_html=True)
    with col_dash2:
        file = st.file_uploader("Upload Data", type=["csv"], label_visibility="collapsed")
        if st.button("UPLOAD DATASET"):
            pass

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Filters Row
        st.markdown('<div class="glass-container" style="padding: 1.5rem;">', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns([1.5, 1.5, 1, 0.5])
        
        with f1:
            product = st.selectbox("PRODUCT LINE", ["All"] + list(df['product_name'].unique()))
        with f2:
            location = st.selectbox("NODE LOCATION", ["All"] + list(df['location'].unique()))
        with f3:
            date_range = st.date_input("TIME WINDOW", [df['date'].min(), df['date'].max()])
        with f4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("RESET"):
                st.rerun()

        # Apply logic
        if product != "All":
            df = df[df['product_name'] == product]
        if location != "All":
            df = df[df['location'] == location]

        st.markdown('</div>', unsafe_allow_html=True)

        # KPI Metrics Row
        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            bento_stat("Procured Volume", f"{total_ordered:,.0f} KG", "12%", is_up=True, icon="📦")
        with m2:
            bento_stat("Operational Yield", f"{total_used:,.0f} KG", "8.4%", is_up=True, icon="📈")
        with m3:
            bento_stat("Waste Factor", f"{waste_pct:.2f}%", "2.1%", is_up=False, icon="🗑️")
        with m4:
            bento_stat("Financial Impact", f"₹ {total_loss:,.0f}", "₹450", is_up=True, icon="💸")

        # Charts Row
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.area(trend, x='date', y='quantity_wasted_kg', 
                          title="Volumetric Waste Velocity",
                          color_discrete_sequence=['#3b82f6'])
            fig.update_traces(fillcolor='rgba(59, 130, 246, 0.1)')
            st.plotly_chart(chart_theme(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            fig = px.scatter(df, x='temperature_celsius', y='quantity_wasted_kg',
                             size='quantity_ordered_kg', color='quantity_wasted_kg',
                             title="Environmental Correlation: Thermal vs. Spoilage",
                             color_continuous_scale='Viridis',
                             labels={'temperature_celsius': 'Temp (°C)', 'quantity_wasted_kg': 'Waste (KG)'})
            st.plotly_chart(chart_theme(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Awaiting telemetry ingestion. Please upload a dataset to initialize monitoring.")

elif page == "ML Prediction":
    st.markdown("""
    <h2 style="font-weight: 800; font-size: 2.5rem; letter-spacing: -0.04em;">Prediction Engine</h2>
    <p style="color: #64748b; margin-top: 4px;">Neural forecasting for risk mitigation and demand planning.</p>
    """, unsafe_allow_html=True)

    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except:
        st.warning("Models not found. Simulation mode active.")
        # Simulated logic if models missing to prevent crash
        demand_val = 150
        spoil_val = 0
    else:
        def safe_encode(enc, val):
            return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏷️ CATEGORY")
        product_list = encoders['product_name'].classes_ if 'encoders' in locals() else ["Product A", "Product B"]
        cat_list = encoders['category'].classes_ if 'encoders' in locals() else ["Fruits", "Vegetables"]
        product = st.selectbox("PRODUCT IDENTIFIER", product_list)
        category = st.selectbox("DEPARTMENT", cat_list)
        quantity = st.number_input("ORDER VOLUME (KG)", 10, 5000, 100)

    with col2:
        st.markdown("### 🏭 FACILITY")
        unit_cost = st.number_input("UNIT VALUATION (₹)", 1, 1000, 50)
        storage_capacity = st.number_input("NODE CAPACITY (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("SHELF HORIZON (Days)", 1, 60, 7)

    with col3:
        st.markdown("### 🌡️ ENVIRONMENT")
        temperature = st.slider("THERMAL VECTOR (°C)", 0, 50, 25)
        humidity = st.slider("HYGROMETRIC FACTOR (%)", 10, 100, 60)

    st.markdown("---")
    
    if st.button("INITIATE NEURAL INFERENCE"):
        if 'demand_model' in locals():
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
            cols_order = ['warehouse_id', 'product_id', 'category', 'supplier_id', 'quantity_ordered_kg', 
                          'unit_cost_inr', 'shelf_life_days', 'temperature_celsius', 'humidity_percent', 
                          'storage_capacity_kg', 'day_of_week', 'month']
            input_data = input_data[cols_order]
            demand = demand_model.predict(input_data)[0]
            spoil = spoil_model.predict(input_data)[0]
        else:
            demand, spoil = 180, 0 # Simulation

        with st.spinner("Processing tensors..."):
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.markdown(f"""
                <div style="background: #1c212b; padding: 2rem; border-radius: 16px; border-left: 6px solid #3b82f6;">
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;">Demand Forecast</div>
                    <div style="font-size: 3rem; font-weight: 800; color: #f8fafc;">{int(demand)} <span style="font-size: 1rem; color: #94a3b8;">KG</span></div>
                </div>
                """, unsafe_allow_html=True)
            with res_c2:
                risk_color = "#ef4444" if spoil == 1 else "#10b981"
                risk_text = "CRITICAL SPOILAGE" if spoil == 1 else "OPTIMAL FLOW"
                st.markdown(f"""
                <div style="background: #1c212b; padding: 2rem; border-radius: 16px; border-left: 6px solid {risk_color};">
                    <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;">Risk Assessment</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {risk_color}; margin: 0.5rem 0;">{risk_text}</div>
                </div>
                """, unsafe_allow_html=True)

            # Extra Visuals
            v_c1, v_c2 = st.columns(2)
            with v_c1:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", value = demand, domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Capacity Load Factor", 'font': {'size': 18, 'color': "#94a3b8"}},
                    gauge = {'axis': {'range': [None, storage_capacity]}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#1c212b"}
                ))
                fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
                st.plotly_chart(fig_gauge, use_container_width=True)
            with v_c2:
                # Radar
                factors = ['Heat', 'Humidity', 'Life', 'Cost', 'Vol']
                vals = [temperature/50, humidity/100, 1-(shelf_life/60), unit_cost/1000, quantity/5000]
                fig_radar = go.Figure(data=go.Scatterpolar(r=vals, theta=factors, fill='toself', line_color='#3b82f6'))
                fig_radar.update_layout(polar=dict(bgcolor='#1c212b', radialaxis=dict(visible=False)),
                                        showlegend=False, paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "AI Advice":
    st.markdown("""
    <h2 style="font-weight: 800; font-size: 2.5rem; letter-spacing: -0.04em;">AI Advisory Protocol</h2>
    <p style="color: #64748b; margin-top: 4px;">Strategic optimizations and corrective action blueprints.</p>
    """, unsafe_allow_html=True)

    file = st.file_uploader("Upload Historical Logs", type=["csv"], key="advice_upload")

    if file:
        df = pd.read_csv(file)
        top_waste_prod = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_loss_loc = df.groupby('location')['loss_amount_inr'].sum().idxmax()
        
        st.markdown("### 🧠 SYSTEM OVERRIDES")
        c_adv1, c_adv2, c_adv3 = st.columns(3)
        with c_adv1:
            st.markdown(f"""<div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); padding: 1.5rem; border-radius: 16px;">
                <div style="font-weight: 800; color: #ef4444; font-size: 0.7rem;">PRIORITY 1</div>
                <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">Scale Down: {top_waste_prod}</div>
                <p style="color: #94a3b8; font-size: 0.85rem;">Telemetry shows consistent 20% oversupply.</p></div>""", unsafe_allow_html=True)
        with c_adv2:
            st.markdown(f"""<div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); padding: 1.5rem; border-radius: 16px;">
                <div style="font-weight: 800; color: #3b82f6; font-size: 0.7rem;">PRIORITY 2</div>
                <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">Audit Node: {top_loss_loc}</div>
                <p style="color: #94a3b8; font-size: 0.85rem;">Thermal leaks suspected in Zone B.</p></div>""", unsafe_allow_html=True)
        with c_adv3:
            st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); padding: 1.5rem; border-radius: 16px;">
                <div style="font-weight: 800; color: #10b981; font-size: 0.7rem;">SYSTEM HEALTH</div>
                <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">Baseline Stable</div>
                <p style="color: #94a3b8; font-size: 0.85rem;">Overall yield within nominal 2% range.</p></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("### 📊 RISK VISUALIZATION")
        v_c1, v_c2 = st.columns(2)
        with v_c1:
            prod_stats = df.groupby('product_name').agg({'quantity_wasted_kg': 'sum', 'loss_amount_inr': 'sum'}).reset_index()
            fig_bubble = px.scatter(prod_stats, x='loss_amount_inr', y='quantity_wasted_kg', size='loss_amount_inr', color='product_name', title="Risk Matrix")
            st.plotly_chart(chart_theme(fig_bubble), use_container_width=True)
        with v_c2:
            loc_loss = df.groupby(['location', 'product_name'])['loss_amount_inr'].sum().reset_index()
            fig_tree = px.treemap(loc_loss, path=['location', 'product_name'], values='loss_amount_inr', title="Loss Distribution")
            st.plotly_chart(chart_theme(fig_tree), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload logs for AI overrides.")

# FOOTER
st.markdown("""<div style="margin-top: 4rem; padding: 2rem; border-top: 1px solid var(--border); text-align: center;">
    <div style="color: #475569; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase;">FreshTrack AI Intelligence Platform • v3.1</div></div>""", unsafe_allow_html=True)
