import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import warnings
from datetime import datetime

# =========================================================
# CONFIG & SETTINGS
# =========================================================
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="FreshTrack AI | Smart Supply Chain",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROFESSIONAL CSS INJECTION
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main App Background */
    .stApp {
        background-color: #f8fafc;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] hr {
        border-top: 1px solid #334155;
    }

    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }
    
    .sidebar-text {
        color: #94a3b8 !important;
        font-size: 0.9rem;
    }

    /* Section Containers */
    .glass-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }

    /* Custom KPI Cards */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .kpi-card {
        flex: 1;
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-bottom: 4px solid #2563eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .kpi-value {
        font-size: 1.8rem;
        color: #1e293b;
        font-weight: 700;
        margin-top: 8px;
    }

    /* Form Inputs */
    .stSelectbox, .stNumberInput, .stSlider {
        margin-bottom: 15px;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #2563eb;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 2rem;
        border: none;
        width: 100%;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }

    div.stButton > button:first-child:hover {
        background-color: #1d4ed8;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }

    /* Prediction Result Cards */
    .result-card {
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .result-success { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .result-error { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    /* Recommendation Cards */
    .rec-card {
        height: 240px;
        padding: 24px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.3s ease;
    }
    
    .rec-card:hover { transform: scale(1.02); }
    
    .rec-icon { font-size: 2rem; margin-bottom: 10px; }
    .rec-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
    .rec-desc { font-size: 0.95rem; color: #334155; opacity: 0.9; line-height: 1.5; }

    .red-rec { background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left: 6px solid #ef4444; }
    .blue-rec { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 6px solid #2563eb; }
    .orange-rec { background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%); border-left: 6px solid #f59e0b; }
    .green-rec { background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-left: 6px solid #10b981; }

</style>
""", unsafe_allow_html=True)

# Brand Palette
brand_color = "#2563eb"
colors = px.colors.qualitative.Prism

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.image("miracle_logo.png", width=220)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("### 🧭 Main Navigation", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Go To:",
    ["Dashboard", "ML Prediction", "Recommendations"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class='sidebar-text'>
    <b>FreshTrack AI v2.4</b><br>
    Powered by Miracle Software Systems<br>
    © 2024 All Rights Reserved
</div>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD PAGE
# =========================================================
if page == "Dashboard":
    st.markdown("# 📊 Analytics Overview")
    st.markdown("Monitor your fresh produce supply chain health in real-time.")

    file = st.file_uploader(
        "Upload Logistics Dataset (CSV)",
        type=["csv"],
        key="dashboard_upload"
    )

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # Filter Section
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            
            product = c1.selectbox("Filter Product", ["All"] + list(df['product_name'].unique()))
            location = c2.selectbox("Filter Location", ["All"] + list(df['location'].unique()))
            date_range = c3.date_input("Select Period", [df['date'].min(), df['date'].max()])
            
            # Apply Filters
            if product != "All": df = df[df['product_name'] == product]
            if location != "All": df = df[df['location'] == location]
            if len(date_range) == 2:
                df = df[(df['date'] >= pd.to_datetime(date_range[0])) & 
                        (df['date'] <= pd.to_datetime(date_range[1]))]
            st.markdown('</div>', unsafe_allow_html=True)

        # KPI Metrics
        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered) * 100 if total_ordered else 0

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Total Ordered</div>
                <div class="kpi-value">{total_ordered:,.0f} KG</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Quantity Used</div>
                <div class="kpi-value">{total_used:,.0f} KG</div>
            </div>
            <div class="kpi-card" style="border-bottom-color: #ef4444;">
                <div class="kpi-label">Waste Percentage</div>
                <div class="kpi-value" style="color: #ef4444;">{waste_pct:.1f}%</div>
            </div>
            <div class="kpi-card" style="border-bottom-color: #10b981;">
                <div class="kpi-label">Total Financial Loss</div>
                <div class="kpi-value" style="color: #10b981;">₹ {total_loss:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visualizations
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.line(trend, x='date', y='quantity_wasted_kg', title="📈 Waste Trajectory",
                          color_discrete_sequence=[brand_color], template="plotly_white")
            fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.scatter(df, x='temperature_celsius', y='quantity_wasted_kg', 
                            title="🌡️ Spoilage vs Temperature",
                            color_discrete_sequence=[brand_color], template="plotly_white")
            fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("👋 Welcome! Please upload a dataset in the sidebar or main panel to begin analysis.")

# =========================================================
# ML PREDICTION PAGE
# =========================================================
elif page == "ML Prediction":
    st.markdown("# 🧠 AI Prediction Center")
    st.markdown("Use our proprietary ML models to forecast demand and detect spoilage risks.")

    try:
        demand_model = joblib.load("demand_model.pkl")
        spoil_model = joblib.load("spoilage_model.pkl")
        encoders = joblib.load("encoders.pkl")
    except Exception as e:
        st.warning("⚠️ Model files not found. Please ensure PKL files are in the directory.")
        st.stop()

    def safe_encode(enc, val):
        return enc.transform([val])[0] if val in enc.classes_ else 0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Input Parameters")
    
    c1, c2, c3 = st.columns(3)

    with c1:
        product = st.selectbox("Product Selection", encoders['product_name'].classes_)
        category = st.selectbox("Product Category", encoders['category'].classes_)
        quantity = st.number_input("Order Quantity (KG)", 10, 5000, 100)

    with c2:
        temperature = st.slider("Storage Temp (°C)", 0, 50, 25)
        humidity = st.slider("Relative Humidity (%)", 10, 100, 60)
        unit_cost = st.number_input("Unit Cost (₹)", 1, 1000, 50)

    with c3:
        storage_capacity = st.number_input("Warehouse Cap (KG)", 100, 10000, 2000)
        shelf_life = st.number_input("Target Shelf Life (Days)", 1, 60, 7)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("RUN AI ENGINE"):
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
        
        # Ensure correct column order
        cols = ['warehouse_id', 'product_id', 'category', 'supplier_id', 'quantity_ordered_kg', 
                'unit_cost_inr', 'shelf_life_days', 'temperature_celsius', 'humidity_percent', 
                'storage_capacity_kg', 'day_of_week', 'month']
        input_data = input_data[cols]

        demand = demand_model.predict(input_data)[0]
        spoil = spoil_model.predict(input_data)[0]

        st.markdown("<hr>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown(f"""
            <div class="result-card result-success">
                📦 Predicted Demand: <b>{int(demand)} KG</b>
            </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            if spoil == 1:
                st.markdown("""
                <div class="result-card result-error">
                    ⚠️ ALERT: High Spoilage Risk Detected
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-card result-success">
                    ✅ STATUS: Optimal Freshness Guaranteed
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RECOMMENDATIONS PAGE
# =========================================================
elif page == "Recommendations":
    st.markdown("# 💡 AI Recommendation Center")
    st.markdown("Actionable insights generated from your supply chain history.")

    file = st.file_uploader("Upload Data for Analysis", type=["csv"], key="recommendation_upload")

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()
        waste_pct = (total_waste / total_ordered) * 100 if total_ordered else 0
        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()
        avg_temp = df['temperature_celsius'].mean()

        # Strategic Cards
        st.markdown("### 🚀 Critical Strategic Actions")
        rcol1, rcol2, rcol3, rcol4 = st.columns(4)

        with rcol1:
            st.markdown(f"""
            <div class="rec-card red-rec">
                <div>
                   <div class="rec-icon">🔴</div>
                   <div class="rec-title">Procurement Warning</div>
                </div>
                <div class="rec-desc">Excess inventory detected. Suggest reducing <b>{top_product}</b> orders by 15% next week.</div>
            </div>
            """, unsafe_allow_html=True)

        with rcol2:
            st.markdown(f"""
            <div class="rec-card blue-rec">
                <div>
                    <div class="rec-icon">🔵</div>
                    <div class="rec-title">Cold Chain Alert</div>
                </div>
                <div class="rec-desc">Improve storage conditions at <b>{top_location}</b> to mitigate recurring spoilage.</div>
            </div>
            """, unsafe_allow_html=True)

        with rcol3:
            temp_msg = "Critical: Install HVAC sensors." if avg_temp > 30 else "Temp profile looks healthy."
            st.markdown(f"""
            <div class="rec-card orange-rec">
                <div>
                    <div class="rec-icon">🟠</div>
                    <div class="rec-title">Climate Integrity</div>
                </div>
                <div class="rec-desc">{temp_msg} Mean temperature is currently <b>{avg_temp:.1f}°C</b>.</div>
            </div>
            """, unsafe_allow_html=True)

        with rcol4:
            st.markdown("""
            <div class="rec-card green-rec">
                <div>
                    <div class="rec-icon">🟢</div>
                    <div class="rec-title">FIFO Optimization</div>
                </div>
                <div class="rec-desc">Implement strict First-In-First-Out rotation for high-turnover inventory.</div>
            </div>
            """, unsafe_allow_html=True)

        # Detailed Analysis Table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Priority Execution Plan")
        
        actions = pd.DataFrame({
            "Priority": ["🔴 High", "🟡 Medium", "🟡 Medium", "🔵 Low"],
            "Department": ["Procurement", "Operations", "Storage", "Logistics"],
            "Detailed Strategy": [
                f"Aggressive reduction in {top_product} stocks.",
                "Warehouse temperature audit & hardware cooling fix.",
                f"Upgrade storage racks at {top_location}.",
                "Synchronize ML demand forecasts with ERP system."
            ]
        })
        st.dataframe(actions, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts Row
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            waste_products = df.groupby('product_name')['quantity_wasted_kg'].sum().nlargest(5).reset_index()
            fig = px.bar(waste_products, x='quantity_wasted_kg', y='product_name', orientation='h',
                        title="Top 5 Spoilage Contributors", color='quantity_wasted_kg', 
                        color_continuous_scale='Blues', template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            loss_loc = df.groupby('location')['loss_amount_inr'].sum().reset_index()
            fig2 = px.pie(loss_loc, values='loss_amount_inr', names='location', 
                         title="Loss Contribution by Cluster", hole=0.6,
                         color_discrete_sequence=colors, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload your dataset to unlock AI-driven strategic recommendations.")
