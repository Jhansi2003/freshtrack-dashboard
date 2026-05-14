import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, accuracy_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv("fnb_poc_dataset .csv")

# =========================================================
# DATE PROCESSING
# =========================================================
df['date'] = pd.to_datetime(df['date'])

# Create Time Features
df['day_of_week'] = df['date'].dt.weekday
df['month'] = df['date'].dt.month

# =========================================================
# HANDLE MISSING VALUES
# =========================================================
df = df.dropna(
    subset=[
        'quantity_used_kg',
        'spoilage_flag'
    ]
)

df = df.fillna(0)

df['spoilage_flag'] = (
    df['spoilage_flag']
    .astype(int)
)

# =========================================================
# CREATE REQUIRED IDs
# =========================================================

# Product ID
if 'product_id' not in df.columns:

    product_encoder = LabelEncoder()

    df['product_id'] = product_encoder.fit_transform(
        df['product_name']
    )

# Supplier ID
if 'supplier_id' not in df.columns:

    supplier_encoder = LabelEncoder()

    df['supplier_id'] = supplier_encoder.fit_transform(
        df['supplier_name']
    )

# Warehouse ID
if 'warehouse_id' not in df.columns:

    warehouse_encoder = LabelEncoder()

    df['warehouse_id'] = warehouse_encoder.fit_transform(
        df['location']
    )

# =========================================================
# ENCODING CATEGORICAL COLUMNS
# =========================================================
cat_cols = [
    'product_name',
    'category',
    'supplier_name',
    'weather_condition',
    'storage_type',
    'location'
]

encoders = {}

for col in cat_cols:

    le = LabelEncoder()

    df[col] = le.fit_transform(
        df[col].astype(str)
    )

    encoders[col] = le

# =========================================================
# FEATURE SELECTION
# =========================================================
features = [

    'warehouse_id',

    'product_id',

    'category',

    'supplier_id',

    'quantity_ordered_kg',

    'unit_cost_inr',

    'shelf_life_days',

    'temperature_celsius',

    'humidity_percent',

    'storage_capacity_kg',

    'day_of_week',

    'month'
]

# Keep Only Existing Columns
features = [
    col for col in features
    if col in df.columns
]

X = df[features]

# =========================================================
# TARGET VARIABLES
# =========================================================
y_demand = df['quantity_used_kg']

y_spoil = df['spoilage_flag']

# =========================================================
# TRAIN TEST SPLIT - DEMAND
# =========================================================
X_train_d,
X_test_d,
y_train_d,
y_test_d = train_test_split(
    X,
    y_demand,
    test_size=0.2,
    random_state=42
)

# =========================================================
# DEMAND MODEL
# =========================================================
demand_model = RandomForestRegressor(

    n_estimators=50,

    max_depth=10,

    min_samples_split=5,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1
)

demand_model.fit(
    X_train_d,
    y_train_d
)

pred_demand = demand_model.predict(
    X_test_d
)

mae = mean_absolute_error(
    y_test_d,
    pred_demand
)

print("\n📈 Demand Model MAE:", round(mae, 2))

# =========================================================
# TRAIN TEST SPLIT - SPOILAGE
# =========================================================
X_train_s,
X_test_s,
y_train_s,
y_test_s = train_test_split(
    X,
    y_spoil,
    test_size=0.2,
    random_state=42
)

# =========================================================
# SPOILAGE MODEL
# =========================================================
spoil_model = RandomForestClassifier(

    n_estimators=50,

    max_depth=10,

    min_samples_split=5,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1
)

spoil_model.fit(
    X_train_s,
    y_train_s
)

pred_spoil = spoil_model.predict(
    X_test_s
)

accuracy = accuracy_score(
    y_test_s,
    pred_spoil
)

print(
    "⚠️ Spoilage Model Accuracy:",
    round(accuracy * 100, 2),
    "%"
)

# =========================================================
# SAVE MODELS
# =========================================================
joblib.dump(
    demand_model,
    "demand_model.pkl",
    compress=5
)

joblib.dump(
    spoil_model,
    "spoilage_model.pkl",
    compress=5
)

joblib.dump(
    encoders,
    "encoders.pkl",
    compress=3
)

print("\n✅ Models saved successfully!")

# =========================================================
# FEATURE CHECK
# =========================================================
print("\n✅ Training Features Used:")

for feature in features:
    print("-", feature)
