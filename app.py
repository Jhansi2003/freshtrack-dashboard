import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="FreshTrack AI",
    layout="wide"
)

# =========================================================
# CUSTOM STYLING
# =========================================================
st.markdown("""
<style>

/* Main App Background */
.stApp {
    background-color: #f5f7fa;
}

/* Section Cards */
.section {
    background-color: white;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* KPI Cards */
[data-testid="stMetric"] {
    background-color: white;
    border-left: 4px solid #2563eb;
    padding: 12px;
    border-radius: 12px;
}

/* KPI Text */
[data-testid="stMetricValue"] {
    font-size: 22px;
    color: #111827;
}

[data-testid="stMetricLabel"] {
    font-size: 13px;
    color: #6b7280;
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
    width: 100%;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

/* Dropdown */
div[data-baseweb="select"] > div {
    border-radius: 8px;
}

/* Headers */
h1, h2, h3 {
    color: #111827;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

brand_color = "#2563eb"
colors = px.colors.qualitative.Set2

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
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

        # =================================================
        # FILTERS
        # =================================================
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

        # =================================================
        # KPI METRICS
        # =================================================
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

        c1.metric(
            "Ordered",
            f"{total_ordered:,.0f} KG"
        )

        c2.metric(
            "Used",
            f"{total_used:,.0f} KG"
        )

        c3.metric(
            "Waste %",
            f"{waste_pct:.2f}%"
        )

        c4.metric(
            "Loss",
            f"₹ {total_loss:,.0f}"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # =================================================
        # INSIGHTS
        # =================================================
        st.markdown('<div class="section">', unsafe_allow_html=True)

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

        # =================================================
        # CHARTS
        # =================================================
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
                height=320
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
                height=320
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

    st.title("ML Prediction Center")

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

    st.title("AI Recommendation Center")
    st.caption(
        "Smart insights for inventory optimization and spoilage reduction"
    )

    file = st.file_uploader(
        "Upload Dataset",
        type=["csv"],
        key="recommendation_upload"
    )

    if file:

        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])

        # =================================================
        # CALCULATIONS
        # =================================================
        total_ordered = df['quantity_ordered_kg'].sum()
        total_waste = df['quantity_wasted_kg'].sum()
        total_loss = df['loss_amount_inr'].sum()

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

        # =================================================
        # SUMMARY METRICS
        # =================================================
        st.markdown('<div class="section">', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Waste %",
            f"{waste_pct:.2f}%"
        )

        c2.metric(
            "Total Waste",
            f"{total_waste:,.0f} KG"
        )

        c3.metric(
            "Financial Loss",
            f"₹ {total_loss:,.0f}"
        )

        c4.metric(
            "Anomalies",
            anomaly_count
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # =================================================
        # RECOMMENDATION CARDS
        # =================================================
        st.subheader("Strategic Recommendations")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(f"""
            <div style="
                background:white;
                padding:20px;
                border-radius:14px;
                margin-bottom:15px;
                box-shadow:0 2px 10px rgba(0,0,0,0.05);
                border-left:5px solid #ef4444;
            ">
                <h4>High Waste Product</h4>
                <p>
                Reduce procurement quantity for 
                <b>{top_product}</b> 
                to minimize spoilage losses.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="
                background:white;
                padding:20px;
                border-radius:14px;
                margin-bottom:15px;
                box-shadow:0 2px 10px rgba(0,0,0,0.05);
                border-left:5px solid #2563eb;
            ">
                <h4>Storage Optimization</h4>
                <p>
                Improve warehouse handling and storage
                conditions in <b>{top_location}</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:

            if avg_temp > 30:

                st.markdown("""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:14px;
                    margin-bottom:15px;
                    box-shadow:0 2px 10px rgba(0,0,0,0.05);
                    border-left:5px solid #f59e0b;
                ">
                    <h4>Temperature Risk</h4>
                    <p>
                    High warehouse temperature detected.
                    Deploy cooling optimization strategies.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style="
                background:white;
                padding:20px;
                border-radius:14px;
                margin-bottom:15px;
                box-shadow:0 2px 10px rgba(0,0,0,0.05);
                border-left:5px solid #10b981;
            ">
                <h4>Inventory Rotation</h4>
                <p>
                Prioritize low shelf-life inventory to
                reduce future wastage.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # =================================================
        # CHARTS
        # =================================================
        st.markdown('<div class="section">', unsafe_allow_html=True)

        st.subheader("Operational Insights")

        c1, c2 = st.columns(2)

        with c1:

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
                title="Top Waste Products",
                color_discrete_sequence=[brand_color]
            )

            fig.update_layout(
                height=350,
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            loss_loc = (
                df.groupby('location')['loss_amount_inr']
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                loss_loc,
                x='location',
                y='loss_amount_inr',
                title="Loss by Location",
                color_discrete_sequence=["#ef4444"]
            )

            fig2.update_layout(
                height=350,
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # =================================================
        # ACTION PLAN TABLE
        # =================================================
        st.markdown('<div class="section">', unsafe_allow_html=True)

        st.subheader("Priority Action Plan")

        actions = pd.DataFrame({

            "Priority": [
                "High",
                "Medium",
                "Medium",
                "Low"
            ],

            "Area": [
                "Inventory Planning",
                "Warehouse Cooling",
                "Storage Optimization",
                "Demand Forecasting"
            ],

            "Recommendation": [
                f"Reduce ordering for {top_product}",
                "Monitor warehouse temperature",
                f"Improve storage in {top_location}",
                "Use ML prediction before procurement"
            ]
        })

        st.dataframe(
            actions,
            use_container_width=True,
            hide_index=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info(
            "Upload dataset to generate AI recommendations."
        )
