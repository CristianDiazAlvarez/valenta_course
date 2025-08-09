#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from mod02_data_functions import get_mysql_cursor, delete_covertype_table
import numpy as np

# -----------------------------------
# 1. Load data from raw_data
# -----------------------------------
def load_new_raw_data():
    cursor, conn = get_mysql_cursor()
    try:
        # --- 1. Check if clean_data table exists ---
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = 'clean_data';
        """)
        table_exists = cursor.fetchone()[0] > 0

        existing_ids = set()

        # --- 2. If clean_data exists, get its raw_id values ---
        if table_exists:
            cursor.execute("SELECT raw_id FROM clean_data")
            existing_ids = {row[0] for row in cursor.fetchall()}

        # --- 3. Build query to fetch only new rows ---
        if existing_ids:
            query = f"""
                SELECT id, Elevation, Aspect, Slope,
                       Horizontal_Distance_To_Hydrology, Vertical_Distance_To_Hydrology,
                       Horizontal_Distance_To_Roadways, Hillshade_9am, Hillshade_Noon, Hillshade_3pm,
                       Horizontal_Distance_To_Fire_Points, Wilderness_Area, Soil_Type, Cover_Type
                FROM raw_data
                WHERE id NOT IN ({','.join(map(str, existing_ids))});
            """
        else:
            # If no table or no processed IDs, get all rows
            query = """
                SELECT id, Elevation, Aspect, Slope,
                       Horizontal_Distance_To_Hydrology, Vertical_Distance_To_Hydrology,
                       Horizontal_Distance_To_Roadways, Hillshade_9am, Hillshade_Noon, Hillshade_3pm,
                       Horizontal_Distance_To_Fire_Points, Wilderness_Area, Soil_Type, Cover_Type
                FROM raw_data;
            """

        df = pd.read_sql(query, conn)
        return df

    except Exception as e:
        print(f"Error loading new raw data: {e}")
        return pd.DataFrame()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -----------------------------------
# 2. Custom feature engineering
# -----------------------------------
def add_hillshade_avg(df):
    df = df.copy()
    df["Hillshade_Avg"] = df[["Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm"]].mean(axis=1)
    return df

# -----------------------------------
# 3. Build preprocessing pipeline
# -----------------------------------
def build_pipeline():
    # Distance features
    distance_features = [
        "Horizontal_Distance_To_Hydrology",
        "Vertical_Distance_To_Hydrology",
        "Horizontal_Distance_To_Roadways",
        "Horizontal_Distance_To_Fire_Points"
    ]

    # Numerical features (including hillshade avg)
    numerical_features = [
        "Elevation", "Aspect", "Slope",
        "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm", "Hillshade_Avg"
    ] + distance_features

    # Categorical features
    categorical_features = ["Wilderness_Area", "Soil_Type"]

    # Transformers
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        #("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Full preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ("hillshade_avg", FunctionTransformer(add_hillshade_avg)),
        ("drop_duplicates", FunctionTransformer(lambda df: df.drop_duplicates())),
        ("preprocessor", preprocessor)
    ])
    return pipeline

# -----------------------------------
# 4. Save processed data into clean_data
# -----------------------------------
def save_clean_data(processed_array, feature_names, raw_ids, cover_types):
    """
    Saves processed numeric data into clean_data without duplication,
    using raw_data.id as the uniqueness key. Also stores Cover_Type
    (classification target) without preprocessing.

    processed_array : numpy.ndarray
        Fully processed numeric features (scaled/encoded).
    feature_names : list
        Names of processed features (numeric + encoded columns).
    raw_ids : list or array
        The id column values from raw_data corresponding to processed_array rows.
    cover_types : list or array
        The target Cover_Type values from raw_data (not processed).
    """
    cursor, conn = get_mysql_cursor()
    try:
        # 1. Create table if it does not exist
        columns_def = ",\n".join([f"`{col}` DOUBLE" for col in feature_names])
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS clean_data (
                raw_id INT UNIQUE,
                {columns_def},
                Cover_Type INT
            );
        """
        cursor.execute(create_sql)

        # 2. Fetch existing raw_ids
        cursor.execute("SELECT raw_id FROM clean_data")
        existing_ids = {row[0] for row in cursor.fetchall()}

        # 3. Prepare only new rows
        new_rows = []
        for idx, row, cover in zip(raw_ids, processed_array.tolist(), cover_types):
            if idx not in existing_ids:
                new_rows.append((idx, *[float(v) if v is not None else None for v in row], int(cover)))

        # 4. Insert new rows
        if new_rows:
            insert_sql = f"""
                INSERT INTO clean_data (raw_id, {', '.join(f'`{col}`' for col in feature_names)}, Cover_Type)
                VALUES ({', '.join(['%s'] * (len(feature_names) + 2))})
            """
            cursor.executemany(insert_sql, new_rows)
            conn.commit()
            print(f"Inserted {len(new_rows)} new processed rows into 'clean_data'.")
        else:
            print("No new rows to insert into 'clean_data'.")

    except Exception as e:
        print(f"Error saving clean data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -----------------------------------
# 5. Run full preprocessing and save
# -----------------------------------

def main():
    # Load only new rows
    new_df = load_new_raw_data()

    if new_df.empty:
        print("No new data to process.")
    else:
        raw_ids = new_df["id"].tolist()
        cover_types = new_df["Cover_Type"].tolist()  # target values

        # Drop the ID and target columns before transformation
        features_df = new_df.drop(columns=["id", "Cover_Type"])

        # Build and run the pipeline
        pipeline = build_pipeline()
        processed_array = pipeline.fit_transform(features_df)

        # Get feature names
        numeric_cols = [
            "Elevation", "Aspect", "Slope",
            "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm", "Hillshade_Avg",
            "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
            "Horizontal_Distance_To_Roadways", "Horizontal_Distance_To_Fire_Points"
        ]
        ohe = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
        cat_cols = ohe.get_feature_names_out(["Wilderness_Area", "Soil_Type"]).tolist()
        all_feature_names = numeric_cols + cat_cols

        # Save only new processed rows with target
        save_clean_data(processed_array, all_feature_names, raw_ids, cover_types)

    

if __name__ == "__main__":
    main()    

