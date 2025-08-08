import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from mod02_data_functions import get_mysql_cursor
import os
import boto3


def fetch_clean_data():
    """Fetch all rows from MySQL clean_data table and return as DataFrame."""
    cursor, conn = get_mysql_cursor()
    try:
        cursor.execute("SELECT * FROM `clean_data`;")
        results = cursor.fetchall()

        cursor.execute("SHOW COLUMNS FROM `clean_data`;")
        columns = [col[0] for col in cursor.fetchall()]

        return pd.DataFrame(results, columns=columns)
    finally:
        cursor.close()
        conn.close()


def prepare_data(df):
    """Split clean_data DataFrame into train/test sets."""
    X = df.drop(columns=["raw_id", "Cover_Type"])
    y = df["Cover_Type"]

    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_and_log_model(X_train, X_test, y_train, y_test, params):
    """Train RandomForest model, log to MLflow, and print metrics."""
    with mlflow.start_run(run_name="RandomForest_CoverType"):
        clf = RandomForestClassifier(**params)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        print("Accuracy:", acc)
        print("\nClassification Report:\n", classification_report(y_test, y_pred))

        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(
            sk_model=clf,
            artifact_path="random_forest_cover_type"
        )

        print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")


def main():
    """Main pipeline for training and logging Cover_Type model to MLflow."""
    mlflow.set_tracking_uri("http://mlflow:5000")  # or localhost:5001 if outside Docker
    mlflow.set_experiment("cover_type_experiment")

    df = fetch_clean_data()
    X_train, X_test, y_train, y_test = prepare_data(df)
    params = {"n_estimators": 100, "random_state": 42}
    train_and_log_model(X_train, X_test, y_train, y_test, params)


if __name__ == "__main__":
    main()
