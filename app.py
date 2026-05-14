import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="FreshTrack AI",
    layout="wide"
)

# -----------------------------
# PROFESSIONAL THEME
# -----------------------------
st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #f5f7fa;
}

/* Section Containers */
.section {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* KPI Cards */
[data-testid="stMetric"] {
    background-color: white;
    border-left: 4px solid #3b82f6;
    padding: 10px;
    border-radius: 10px;
}

/* KPI Text */
[data-testid="stMetricValue"] {
    font-size: 22px;
}

[data-testid="stMetricLabel"] {
    font-size: 13px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Buttons */
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    height: 42px;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

/* Dropdown */
div[data-baseweb="select"] > div {
    border-radius: 8px;
    border: 1px solid #d1d5db;
}

/* Titles */
h1, h2, h3 {
    color: #1f2937;
}

</style>
""", unsafe_allow_html=True)

brand_color = "#3b82f6"
colors = px.colors.qualitative.Set2

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("FreshTrack AI")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "ML Prediction", "Recommendations"]
)

# =========================================================
# DASHBOARD PAGE
# =========================================================
if page == "Dashboard":

    st.title("FreshTrack AI Dashboard")

    file = st.file_uploader(
        "Upload Dataset",
        type=["csv"],
        key="dashboard_upload"
    )

    if file:

        df = pd.read_csv(file)

        df['date'] = pd.to_datetime(df['date'])

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        product = c1.selectbox(
            "Select Product",
            ["All"] + list(df['product_name'].unique())
        )

        location = c2.selectbox(
            "Select Location",
            ["All"] + list(df['location'].unique())
        )

        date_range = c3.date_input(
            "Date Range",
            [df['date'].min(), df['date'].max()]
        )

        # Apply Filters
        if product != "All":
            df = df[df['product_name'] == product]

        if location != "All":
            df = df[df['location'] == location]

        df = df[
            (df['date'] >= pd.to_datetime(date_range[0])) &
            (df['date'] <= pd.to_datetime(date_range[1]))
        ]

        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------
        # KPI METRICS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        total_ordered = df['quantity_ordered_kg'].sum()
        total_used = df['quantity_used_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()

        waste_pct = (
            (total_waste / total_ordered) * 100
            if total_ordered else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Ordered", f"{total_ordered:,.0f} KG")
        c2.metric("Used", f"{total_used:,.0f} KG")
        c3.metric("Waste %", f"{waste_pct:.2f}%")
        c4.metric("Loss", f"₹ {total_loss:,.0f}")

        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------
        # INSIGHTS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        top_product = df.groupby(
            'product_name'
        )['quantity_wasted_kg'].sum().idxmax()

        top_location = df.groupby(
            'location'
        )['loss_amount_inr'].sum().idxmax()

        mean = df['quantity_wasted_kg'].mean()
        std = df['quantity_wasted_kg'].std()

        df['anomaly'] = (
            df['quantity_wasted_kg'] > (mean + 2 * std)
        )

        anomalies = df[df['anomaly']]

        score = 100

        if waste_pct > 10:
            score -= 30

        if df['temperature_celsius'].mean() > 30:
            score -= 20

        if len(anomalies) > len(df) * 0.1:
            score -= 20

        c1, c2, c3 = st.columns(3)

        c1.metric("Health Score", f"{score}/100")
        c2.metric("Anomalies", len(anomalies))
        c3.metric(
            "Anomaly %",
            f"{(len(anomalies)/len(df))*100:.2f}%"
        )

        st.success(f"Top Waste Product: {top_product}")
        st.warning(f"High Loss Location: {top_location}")

        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------
        # CHARTS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:

            st.subheader("Waste Trend Over Time")

            trend = (
                df.groupby('date')['quantity_wasted_kg']
                .sum()
                .reset_index()
            )

            fig = px.line(
                trend,
                x='date',
                y='quantity_wasted_kg',
                height=300
            )

            fig.update_traces(
                line=dict(color=brand_color)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            st.subheader("Temperature vs Waste")

            fig = px.scatter(
                df,
                x='temperature_celsius',
                y='quantity_wasted_kg',
                color_discrete_sequence=[brand_color],
                height=300
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        c3, c4 = st.columns(2)

        with c3:

            st.subheader("Waste by Category")

            waste_cat = (
                df.groupby('category')['quantity_wasted_kg']
                .sum()
                .reset_index()
            )

            fig = px.pie(
                waste_cat,
                values='quantity_wasted_kg',
                names='category',
                hole=0.5,
                color_discrete_sequence=colors
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c4:

            st.subheader("Loss by Location")

            loss_loc = (
                df.groupby('location')['loss_amount_inr']
                .sum()
                .reset_index()
            )

            fig = px.bar(
                loss_loc,
                x='loss_amount_inr',
                y='location',
                orientation='h',
                color_discrete_sequence=[brand_color]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload dataset to begin.")

# =========================================================
# ML PREDICTION PAGE
# =========================================================
elif page == "ML Prediction":

    st.title("ML Prediction")

    demand_model = joblib.load("demand_model.pkl")
    spoil_model = joblib.load("spoilage_model.pkl")
    encoders = joblib.load("encoders.pkl")

    def safe_encode(enc, val):
        return (
            enc.transform([val])[0]
            if val in enc.classes_
            else -1
        )

    st.markdown('<div class="section">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:

        product = st.selectbox(
            "Product",
            encoders['product_name'].classes_
        )

        location = st.selectbox(
            "Location",
            encoders['location'].classes_
        )

    with c2:

        quantity = st.number_input(
            "Quantity",
            10,
            1000,
            100
        )

        temperature = st.slider(
            "Temperature",
            10,
            50,
            25
        )

        humidity = st.slider(
            "Humidity",
            20,
            100,
            60
        )

    with c3:

        unit_cost = st.number_input(
            "Unit Cost",
            10,
            200,
            50
        )

        storage_capacity = st.number_input(
            "Storage Capacity",
            500,
            5000,
            2000
        )

        shelf_life = st.number_input(
            "Shelf Life",
            1,
            30,
            7
        )

    category = st.selectbox(
        "Category",
        encoders['category'].classes_
    )

    today = pd.Timestamp.today()

    input_data = np.array([
        [
            1,
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
            today.month
        ]
    ])

    if st.button("Predict"):

        demand = demand_model.predict(input_data)[0]

        spoil = spoil_model.predict(input_data)[0]

        st.success(
            f"Predicted Demand: {int(demand)}"
        )

        if spoil == 1:
            st.error("High Spoilage Risk")
        else:
            st.success("Low Spoilage Risk")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RECOMMENDATIONS PAGE
# =========================================================
elif page == "Recommendations":

    st.title("Smart Recommendations")

    file = st.file_uploader(
        "Upload Dataset",
        type=["csv"],
        key="recommendation_upload"
    )

    if file:

        df = pd.read_csv(file)

        df['date'] = pd.to_datetime(df['date'])

        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()

        waste_pct = (
            (total_waste / total_ordered) * 100
            if total_ordered else 0
        )

        top_product = (
            df.groupby('product_name')['quantity_wasted_kg']
            .sum()
            .idxmax()
        )

        top_location = (
            df.groupby('location')['loss_amount_inr']
            .sum()
            .idxmax()
        )

        avg_temp = df['temperature_celsius'].mean()

        mean = df['quantity_wasted_kg'].mean()
        std = df['quantity_wasted_kg'].std()

        df['anomaly'] = (
            df['quantity_wasted_kg'] > (mean + 2 * std)
        )

        anomaly_count = len(df[df['anomaly']])

        # -------------------------------------------------
        # RECOMMENDATION CARDS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        st.subheader("AI Recommendations")

        if waste_pct > 10:
            st.warning(
                f"High waste detected ({waste_pct:.2f}%). "
                f"Reduce ordering for {top_product}."
            )
        else:
            st.success("Waste levels are healthy.")

        st.info(
            f"Improve storage conditions in "
            f"{top_location}."
        )

        if avg_temp > 30:
            st.error(
                "Warehouse temperature is high. "
                "Optimize cooling systems."
            )

        if anomaly_count > 0:
            st.warning(
                f"{anomaly_count} anomalies detected."
            )

        low_shelf = df[df['shelf_life_days'] < 5]

        if len(low_shelf) > 0:
            st.info(
                "Low shelf-life products detected. "
                "Prioritize inventory rotation."
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------
        # CHARTS
        # -------------------------------------------------
        st.markdown('<div class="section">', unsafe_allow_html=True)

        st.subheader("Recommendation Insights")

        waste_products = (
            df.groupby('product_name')['quantity_wasted_kg']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        fig = px.bar(
            waste_products,
            x='product_name',
            y='quantity_wasted_kg',
            color_discrete_sequence=[brand_color]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        loss_loc = (
            df.groupby('location')['loss_amount_inr']
            .sum()
            .reset_index()
        )

        fig2 = px.bar(
            loss_loc,
            x='location',
            y='loss_amount_inr',
            color_discrete_sequence=[brand_color]
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload dataset to generate recommendations.")
