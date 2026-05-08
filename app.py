import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import streamlit as st
import joblib


# -----------------------------
# SUBTLE PROFESSIONAL THEME
# -----------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #f5f7fa;
}

/* Section cards */
.section {
    background-color: white;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* Compact KPI */
[data-testid="stMetric"] {
    background-color: white;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 6px 8px;
    margin: 2px;
}

[data-testid="stMetricValue"] {
    font-size: 18px;
}

[data-testid="stMetricLabel"] {
    font-size: 12px;
}

/* Titles */
h1, h2, h3 {
    color: #1f2937;
}

/* Buttons */
.stButton > button {
    background-color: #3b82f6;
    color: white;
    border-radius: 6px;
    border: none;
}
.stButton > button:hover {
    background-color: #2563eb;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

brand_color = "#3b82f6"
colors = px.colors.qualitative.Set2

# -----------------------------
# NAVIGATION
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Dashboard", "ML Prediction"])

# =============================
# DASHBOARD
# =============================
if page == "Dashboard":

    st.title("FreshTrack AI Dashboard")

    file = st.file_uploader("Upload Dataset", type=["csv"])

    if file:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # -----------------------------
        # FILTERS
        # -----------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        product = c1.multiselect("Product", df['product_name'].unique(), df['product_name'].unique())
        location = c2.multiselect("Location", df['location'].unique(), df['location'].unique())
        date_range = c3.date_input("Date Range", [df['date'].min(), df['date'].max()])

        df = df[
            (df['product_name'].isin(product)) &
            (df['location'].isin(location)) &
            (df['date'] >= pd.to_datetime(date_range[0])) &
            (df['date'] <= pd.to_datetime(date_range[1]))
        ]

        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # KPIs (Compact)
        # -----------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()

        waste_pct = (total_waste / total_ordered * 100) if total_ordered else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ordered", f"{total_ordered:,.0f}")
        c2.metric("Used", f"{total_used:,.0f}")
        c3.metric("Waste %", f"{waste_pct:.2f}%")
        c4.metric("Loss ₹", f"{total_loss:,.0f}")

        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # INSIGHTS + METRICS ALIGN
        # -----------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        top_product = df.groupby('product_name')['quantity_wasted_kg'].sum().idxmax()
        top_location = df.groupby('location')['loss_amount_inr'].sum().idxmax()

        col_i1, col_i2 = st.columns(2)
        col_i1.success(f"Top Waste Product: {top_product}")
        col_i2.warning(f"High Loss Location: {top_location}")

        # Anomaly calc
        mean = df['quantity_wasted_kg'].mean()
        std = df['quantity_wasted_kg'].std()

        df['anomaly'] = df['quantity_wasted_kg'] > (mean + 2 * std)
        anomalies = df[df['anomaly']]

        # Health score
        score = 100
        if waste_pct > 10: score -= 30
        if df['temperature_celsius'].mean() > 30: score -= 20
        if len(anomalies) > len(df)*0.1: score -= 20

        # 👉 SINGLE ROW METRICS
        c1, c2, c3 = st.columns(3)
        c1.metric("Health Score", f"{score}/100")
        c2.metric("Anomalies", len(anomalies))
        c3.metric("Anomaly %", f"{(len(anomalies)/len(df))*100:.2f}%")

        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # CHARTS
        # -----------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Waste Trend Over Time**")
            trend = df.groupby('date')['quantity_wasted_kg'].sum().reset_index()
            fig = px.line(trend, x='date', y='quantity_wasted_kg', height=280)
            fig.update_traces(line=dict(color=brand_color))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("**Temperature vs Waste**")
            fig = px.scatter(df,
                             x='temperature_celsius',
                             y='quantity_wasted_kg',
                             color_discrete_sequence=[brand_color],
                             height=280)
            st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            st.markdown("**Waste by Category**")
            waste_cat = df.groupby('category')['quantity_wasted_kg'].sum().reset_index()
            fig = px.pie(waste_cat, values='quantity_wasted_kg',
                         names='category', hole=0.5,
                         color_discrete_sequence=colors)
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            st.markdown("**Loss by Location**")
            loss_loc = df.groupby('location')['loss_amount_inr'].sum().reset_index()
            fig = px.bar(loss_loc, x='loss_amount_inr', y='location',
                         orientation='h',
                         color_discrete_sequence=[brand_color])
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # RECOMMENDATIONS
        # -----------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Recommendations")
        st.info(f"Reduce ordering for {top_product}")
        st.info(f"Improve storage in {top_location}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload dataset to begin")

# =============================
# ML PAGE
# =============================
else:

    st.title("ML Prediction")

    demand_model = joblib.load("demand_model.pkl")
    spoil_model = joblib.load("spoilage_model.pkl")
    encoders = joblib.load("encoders.pkl")

    def safe_encode(enc, val):
        return enc.transform([val])[0] if val in enc.classes_ else -1

    st.markdown('<div class="section">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        product = st.selectbox("Product", encoders['product_name'].classes_)
        location = st.selectbox("Location", encoders['location'].classes_)

    with c2:
        quantity = st.number_input("Quantity", 10, 1000, 100)
        temperature = st.slider("Temperature", 10, 50, 25)
        humidity = st.slider("Humidity", 20, 100, 60)

    with c3:
        unit_cost = st.number_input("Unit Cost", 10, 200, 50)
        storage_capacity = st.number_input("Storage Capacity", 500, 5000, 2000)
        shelf_life = st.number_input("Shelf Life", 1, 30, 7)

    category = st.selectbox("Category", encoders['category'].classes_)

    today = pd.Timestamp.today()

    input_data = np.array([[1,
                            safe_encode(encoders['product_name'], product),
                            safe_encode(encoders['category'], category),
                            101,
                            quantity,
                            unit_cost,
                            shelf_life,
                            temperature,
                            humidity,
                            storage_capacity,
                            today.weekday(),
                            today.month]])

    if st.button("Predict"):
        demand = demand_model.predict(input_data)[0]
        spoil = spoil_model.predict(input_data)[0]

        st.success(f"Predicted Demand: {int(demand)}")

        if spoil == 1:
            st.error("High Spoilage Risk")
        else:
            st.success("Low Spoilage Risk")

    st.markdown('</div>', unsafe_allow_html=True)
