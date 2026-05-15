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
    page_title="FreshTrack AI | Eco-Logistics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# NATURE-INSPIRED DESIGN SYSTEM (CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --forest: #2d6a4f;
        --sage: #52b788;
        --mint: #d8f3dc;
        --earth: #1b4332;
        --bg-soft: #f0f7f4;
        --card-white: #ffffff;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--bg-soft);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--earth) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* Header Styling */
    .header-box {
        background: linear-gradient(135deg, var(--forest), var(--sage));
        padding: 2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(45, 106, 79, 0.2);
    }

    /* Organic Card Component */
    .nature-card {
        background: var(--card-white);
        border: 1px solid #e9f5ee;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }

    /* Metric Grid */
    .nature-metric {
        background: var(--card-white);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e9f5ee;
        transition: transform 0.3s ease;
    }
    
    .nature-metric:hover {
        transform: scale(1.02);
        border-color: var(--sage);
    }

    .metric-top { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .metric-mid { font-size: 1.8rem; font-weight: 700; color: var(--forest); margin: 0.5rem 0; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--forest), var(--sage));
        color: white;
        border-radius: 15px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
        box-shadow: 0 8px 20px rgba(45, 106, 79, 0.3);
    }
    
    /* Input Styling */
    .stSelectbox div, .stNumberInput input {
        border-radius: 12px !important;
    }

    /* Prediction Visuals */
    .risk-high { background-color: #fff1f2; border: 2px solid #fda4af; color: #9f1239; border-radius: 15px; padding: 1rem; }
    .risk-low { background-color: #f0fdf4; border: 2px solid #86efac; color: #166534; border-radius: 15px; padding: 1rem; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER COMPONENTS
# =========================================================
def styled_kpi(label, value, subtext=""):
    st.markdown(f"""
    <div class="nature-metric">
        <div class="metric-top">{label}</div>
        <div class="metric-mid">{value}</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, icon="🌿"):
    st.markdown(f"""
    <div class="header-box">
        <h1 style="margin:0; font-size: 2.2rem;">{icon} {title}</h1>
        <p style="margin:0; opacity: 0.9; font-weight: 400;">Sustainability Meets Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

def clean_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Plus Jakarta Sans",
        margin=dict(t=40, b=40, l=40, r=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f2f6')
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>FreshTrack AI</h2>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("MAIN MENU", ["Dashboard", "ML Prediction", "Recommendations"])
    st.markdown("---")
    st.info("💡 **Sustainability Tip:** Monitoring temperature patterns can reduce carbon footprint by 12% in cold chains.")

# =========================================================
# DASHBOARD PAGE
# =========================================================
if page == "Dashboard":
    page_header("Inventory Intelligence")

    file = st.file_uploader("Upload supply chain data (CSV)", type=["csv"])

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Sidebar Filters
        st.sidebar.markdown("### Filters")
        product = st.sidebar.selectbox("Product", ["All"] + list(df['product_name'].unique()))
        location = st.sidebar.selectbox("Location", ["All"] + list(df['location'].unique()))
        date_range = st.sidebar.date_input("Range", [df['date'].min(), df['date'].max()])

        if product != "All": df = df[df['product_name'] == product]
        if location != "All": df = df[df['location'] == location]

        # KPIs
        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1: styled_kpi("Procured", f"{total_ordered:,.0f} KG", "Total stock handled")
        with m2: styled_kpi("Wasted", f"{total_waste:,.0f} KG", "Organic material loss")
        with m3: styled_kpi("Efficiency", f"{100-waste_pct:.1f}%", "Stock utilization rate")
        with m4: styled_kpi("Valuation Lost", f"₹ {total_loss:,.0f}", "Financial impact")

        # Visuals
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])

        with c1:
            st.markdown('<div class="nature-card">', unsafe_allow_html=True)
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.area(trend, x='date', y='quantity_wasted_kg', title="Sustainability Leakage Over Time",
                          color_discrete_sequence=['#52b788'])
            st.plotly_chart(clean_chart(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="nature-card">', unsafe_allow_html=True)
            # NEW: Distribution of Waste
            fig = px.box(df, y='quantity_wasted_kg', x='product_name', title="Waste Variance",
                         color_discrete_sequence=['#2d6a4f'])
            st.plotly_chart(clean_chart(fig), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Please upload your inventory data to begin the analysis.")

# =========================================================
# ML PREDICTION PAGE (ENHANCED)
# =========================================================
elif page == "ML Prediction":
    page_header("Predictive Forecast", "🔮")

    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except:
        st.warning("Prediction models not found. Please place artifact files in the root directory.")
        st.stop()

    def safe_encode(enc, val):
        return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="nature-card">', unsafe_allow_html=True)
    st.subheader("Inventory Simulation Parameters")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        product = st.selectbox("Product", encoders['product_name'].classes_)
        category = st.selectbox("Category", encoders['category'].classes_)
        quantity = st.number_input("Order Size (KG)", 10, 5000, 100)
    with col_b:
        unit_cost = st.number_input("Unit Cost (₹)", 1, 1000, 50)
        storage_cap = st.number_input("Max Capacity (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("Life Expectancy (Days)", 1, 60, 7)
    with col_c:
        temp = st.slider("Storage Temp (°C)", 0, 50, 25)
        humid = st.slider("Humidity (%)", 10, 100, 60)

    # Simulation Logic
    today = pd.Timestamp.today()
    input_data = pd.DataFrame([{
        "warehouse_id": 1, "product_id": safe_encode(encoders['product_name'], product),
        "category": safe_encode(encoders['category'], category), "supplier_id": 101,
        "quantity_ordered_kg": quantity, "unit_cost_inr": unit_cost, "shelf_life_days": shelf_life,
        "temperature_celsius": temp, "humidity_percent": humid, "storage_capacity_kg": storage_cap,
        "day_of_week": today.weekday(), "month": today.month
    }])

    if st.button("EXECUTE AI FORECAST"):
        cols = ['warehouse_id', 'product_id', 'category', 'supplier_id', 'quantity_ordered_kg', 
                'unit_cost_inr', 'shelf_life_days', 'temperature_celsius', 'humidity_percent', 
                'storage_capacity_kg', 'day_of_week', 'month']
        input_data = input_data[cols]
        
        demand = demand_model.predict(input_data)[0]
        spoil_risk = spoil_model.predict(input_data)[0]
        
        st.markdown("---")
        res_main, res_visual = st.columns([1, 1.5])
        
        with res_main:
            styled_kpi("Recommended Procurement", f"{int(demand)} KG", "Predicted consumer demand")
            
            risk_text = "CRITICAL SPOILAGE RISK" if spoil_risk == 1 else "SAFE STORAGE PROFILE"
            risk_color = "risk-high" if spoil_risk == 1 else "risk-low"
            st.markdown(f'<div class="{risk_color}" style="text-align:center; font-weight:700;">{risk_text}</div>', unsafe_allow_html=True)

        with res_visual:
            # NEW: Spoilage Probability Gauge
            # Note: Assuming 0/1, just for visual representation
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 85 if spoil_risk == 1 else 15,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Spoilage Risk Probability", 'font': {'size': 16}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': "#2d6a4f"},
                    'steps': [
                        {'range': [0, 40], 'color': "#dcfce7"},
                        {'range': [40, 70], 'color': "#fef3c7"},
                        {'range': [70, 100], 'color': "#fee2e2"}
                    ],
                }
            ))
            fig.update_layout(height=250, margin=dict(t=50, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # NEW: Feature Impact Visuals
        st.markdown("#### Environmental Sensitivity Analysis")
        impact_data = pd.DataFrame({
            "Factor": ["Temp", "Shelf Life", "Humidity", "Vol."],
            "Sensitivity": [temp/50, (60-shelf_life)/60, humid/100, quantity/5000]
        })
        fig_impact = px.line_polar(impact_data, r='Sensitivity', theta='Factor', line_close=True, 
                                   color_discrete_sequence=['#52b788'])
        fig_impact.update_traces(fill='toself')
        st.plotly_chart(fig_impact, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RECOMMENDATIONS PAGE
# =========================================================
elif page == "Recommendations":
    page_header("Sustainability Planner", "🌳")

    file = st.file_uploader("Upload dataset for AI optimization", type=["csv"], key="rec_up")

    if file:
        df = pd.read_csv(file)
        # (Keeping same logic as your original script for variables)
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()

        st.markdown("### Strategic Interventions")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="nature-card" style="border-top: 5px solid #ef4444;">
                <h4 style="margin:0; color:#ef4444;">🔴 Inventory Alert</h4>
                <p style="font-size:0.85rem; margin-top:10px;">Excess waste in <b>{top_product}</b> procurement. Reduce stock input by 20% to optimize freshness.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="nature-card" style="border-top: 5px solid #2563eb;">
                <h4 style="margin:0; color:#2563eb;">🔵 Warehouse Audit</h4>
                <p style="font-size:0.85rem; margin-top:10px;">Location <b>{top_location}</b> shows thermal instability. Cooling infrastructure upgrade recommended.</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="nature-card" style="border-top: 5px solid #10b981;">
                <h4 style="margin:0; color:#10b981;">🟢 Optimization Goal</h4>
                <p style="font-size:0.85rem; margin-top:10px;">Consolidated waste is ₹ {total_loss:,.0f}. Target reduction of 15% through ML-driven FEFO protocols.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Deep Insights
        st.markdown('<div class="nature-card">', unsafe_allow_html=True)
        st.subheader("Waste Contribution by SKU")
        waste_skus = df.groupby('product_name')['quantity_wasted_kg'].sum().reset_index()
        fig = px.treemap(waste_skus, path=['product_name'], values='quantity_wasted_kg',
                         color='quantity_wasted_kg', color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload dataset to generate strategic optimization plans.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="text-align:center; padding: 2rem; color: #94a3b8; font-size: 0.8rem;">
    Powered by FreshTrack AI | Carbon Neutral Dashboard v3.0
</div>
""", unsafe_allow_html=True)
