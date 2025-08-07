from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

# Import the function from DB_test_connection.py
from db_functions.DB_test_connection import mysql_test_connection


def print_hello():
    print("Hello MLOPS_PUJ")


def mysql_test_conn():
    mysql_test_connection()


with DAG(
    dag_id="01_db_test_connection",
    description="DB -- testing connection",
    schedule_interval="@once",
    #start_date=datetime(2023, 5, 1),
) as dag:

    t1 = PythonOperator(task_id="Test_print_hello", python_callable=print_hello)
    t2 = PythonOperator(task_id="DB_test_connection", python_callable=mysql_test_conn)
    

    t1 >> t2 
