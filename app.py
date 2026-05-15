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
    page_title="FreshTrack AI | Smart Logistics",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROFESSIONAL DESIGN SYSTEM (CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #2563eb;
        --secondary: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --background: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #1e293b;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--background);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9 !important;
    }

    /* Header Styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-main);
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1rem;
        color: var(--secondary);
        margin-bottom: 2rem;
    }

    /* Card Component */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Metric Grid */
    .custom-metric {
        background: var(--card-bg);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    
    .custom-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-main);
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-high { background: #fee2e2; color: #ef4444; border: 1px solid #fecaca; }
    .status-low { background: #dcfce7; color: #10b981; border: 1px solid #bbf7d0; }

    /* Buttons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    
    /* Recommendation Tiles */
    .rec-tile {
        height: 100%;
        padding: 1.5rem;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .rec-critical { background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; }
    .rec-info { background: #eff6ff; border: 1px solid #dbeafe; color: #1e40af; }
    .rec-warning { background: #fffbeb; border: 1px solid #fef3c7; color: #92400e; }
    .rec-success { background: #ecfdf5; border: 1px solid #d1fae5; color: #065f46; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def styled_metric(label, value, icon=""):
    st.markdown(f"""
    <div class="custom-metric">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def section_header(title, subtitle):
    st.markdown(f"""
    <div style="margin-top: 1rem;">
        <div class="main-header">{title}</div>
        <div class="sub-header">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def chart_wrapper(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        title_font_size=18,
        margin=dict(t=50, b=30, l=40, r=20),
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0; text-align: center;">
        <h1 style="color: white; font-size: 1.5rem; margin-bottom: 0;">FreshTrack <span style="color: #60a5fa;">AI</span></h1>
        <p style="color: #94a3b8; font-size: 0.8rem;">Intelligence in Fresh Logistics</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    page = st.radio("NAVIGATION", ["Analytics Dashboard", "ML Prediction Engine", "Strategic Insights"])
    st.markdown("---")
    st.markdown("""<p style="font-size: 0.75rem; color: #94a3b8;">v2.4.0-Stable</p>""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD PAGE
# =========================================================
if page == "Analytics Dashboard":
    section_header("Control Center", "Real-time supply chain freshness analytics and waste monitoring.")

    file = st.file_uploader("Ingest supply chain dataset (.csv)", type=["csv"], key="dashboard_upload")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Filter Section
        with st.expander("🔍 Advanced Filtering", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1: product = st.selectbox("Product Line", ["All Products"] + list(df['product_name'].unique()))
            with c2: location = st.selectbox("Warehouse Node", ["All Locations"] + list(df['location'].unique()))
            with c3: date_range = st.date_input("Observation Window", [df['date'].min(), df['date'].max()])

        if product != "All Products": df = df[df['product_name'] == product]
        if location != "All Locations": df = df[df['location'] == location]
        if len(date_range) == 2:
            df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]

        # KPIs
        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1: styled_metric("Procured Volume", f"{total_ordered:,.0f} KG", "📦")
        with m2: styled_metric("Utilization", f"{df['quantity_used_kg'].sum():,.0f} KG", "⚙️")
        with m3: styled_metric("Waste Rate", f"{waste_pct:.2f}%", "♻️")
        with m4: styled_metric("Economic Leakage", f"₹ {total_loss:,.0f}", "📉")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.area(trend, x='date', y='quantity_wasted_kg', title="Temporal Distribution", color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(chart_wrapper(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig = px.scatter(df, x='temperature_celsius', y='quantity_wasted_kg', size='quantity_ordered_kg', title="Thermal Impact", color_continuous_scale='Reds')
            st.plotly_chart(chart_wrapper(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Ingest dataset to initialize the telemetry dashboard.")

# =========================================================
# ML PREDICTION PAGE
# =========================================================
elif page == "ML Prediction Engine":
    section_header("Inference Engine", "Neural-enhanced forecasting for demand and spoilage risk assessment.")
    
    demand_model = joblib.load("demand_model.pkl")
    spoil_model = joblib.load("spoilage_model.pkl")
    encoders = joblib.load("encoders.pkl")

    def safe_encode(enc, val): return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        product = st.selectbox("Target Product", encoders['product_name'].classes_)
        category = st.selectbox("Category", encoders['category'].classes_)
    with c2:
        quantity = st.number_input("Input Quantity (KG)", 10, 5000, 100)
        temperature = st.slider("Temp (°C)", 0, 50, 25)
    with c3:
        unit_cost = st.number_input("Cost (₹)", 1, 1000, 50)
        storage_capacity = st.number_input("Capacity (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("Life (Days)", 1, 60, 7)
        humidity = st.slider("Humidity (%)", 10, 100, 60)

    if st.button("RUN INFERENCE MODEL"):
        input_data = pd.DataFrame([{
            "warehouse_id": 1, "product_id": safe_encode(encoders['product_name'], product),
            "category": safe_encode(encoders['category'], category), "supplier_id": 101,
            "quantity_ordered_kg": quantity, "unit_cost_inr": unit_cost, "shelf_life_days": shelf_life,
            "temperature_celsius": temperature, "humidity_percent": humidity, "storage_capacity_kg": storage_capacity,
            "day_of_week": pd.Timestamp.today().weekday(), "month": pd.Timestamp.today().month
        }])
        demand = demand_model.predict(input_data)[0]
        spoil = spoil_model.predict(input_data)[0]
        
        st.markdown("---")
        res1, res2 = st.columns(2)
        with res1: styled_metric("Predicted Demand", f"{int(demand)} KG", "📈")
        with res2:
            status_class = "status-high" if spoil == 1 else "status-low"
            st.markdown(f'<div class="custom-metric"><div class="metric-label">Risk</div><div class="status-badge {status_class}">{ "⚠️ HIGH RISK" if spoil == 1 else "✅ STABLE" }</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RECOMMENDATIONS PAGE
# =========================================================
elif page == "Strategic Insights":
    section_header("Intelligence Center", "AI-driven optimizations and strategic logistics recommendations.")
    file = st.file_uploader("Upload dataset", type=["csv"], key="recommendation_upload")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="rec-tile rec-critical"><strong>Inventory Recal</strong><p>Reduce {top_product} proc.</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="rec-tile rec-info"><strong>Facility Opt</strong><p>Audit {top_location}.</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="rec-tile rec-warning"><strong>Thermal Control</strong><p>Cooling required.</p></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="rec-tile rec-success"><strong>FEFO Protocol</strong><p>Rotate stock now.</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Priority": ["🔴 Critical", "🟠 High"], "Action": [f"Adjust {top_product}", "Audit Storage"]}), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload dataset for AI-driven insights.")
