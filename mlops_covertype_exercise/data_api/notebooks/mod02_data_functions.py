#!/usr/bin/env python
# coding: utf-8

import requests
import mysql.connector
from mysql.connector import Error
import os

# # Database Functions

# ## Create cursor

# In[5]:


def get_mysql_cursor():
    """
    Establishes a MySQL connection using environment variables and returns the cursor and connection.
    """
    conn = None
    try:
        host = os.getenv("MYSQL_HOST")
        port = int(os.getenv("MYSQL_PORT"))
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")
    
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        if conn.is_connected():
            print("MySQL cursor created successfully")
            return conn.cursor(), conn
        else:
            print("Failed to connect to MySQL.")
            return None, None

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None, None

## Get DBs and Tables

def list_mysql_databases_and_tables():
    """
    Lists all databases and their tables in the connected MySQL server.
    """
    cursor, conn = get_mysql_cursor()
    try:
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        print("Databases and their tables:")

        for (db_name,) in databases:
            print(f"\n📁 Database: {db_name}")
            try:
                cursor.execute(f"USE `{db_name}`;")
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                if tables:
                    for (table_name,) in tables:
                        print(f"  - 🗂️ {table_name}")
                else:
                    print("  (No tables found)")
            except Error as e:
                print(f"  ⚠️ Could not access tables in '{db_name}': {e}")
    finally:
        cursor.close()
        conn.close()




# ## Create Table

# In[6]:


def create_covertype_table(table_name):
    """
    Creates a table with the specified name in the MySQL database if it does not exist.
    Credentials and connection info are read from environment variables.
    
    Parameters:
    - table_name (str): Name of the table to be created.
    """

    cursor, conn = get_mysql_cursor()
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Elevation INT,
        Aspect INT,
        Slope INT,
        Horizontal_Distance_To_Hydrology INT,
        Vertical_Distance_To_Hydrology INT,
        Horizontal_Distance_To_Roadways INT,
        Hillshade_9am INT,
        Hillshade_Noon INT,
        Hillshade_3pm INT,
        Horizontal_Distance_To_Fire_Points INT,
        Wilderness_Area VARCHAR(20),
        Soil_Type VARCHAR(20),
        Cover_Type INT
    );
    """
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Table '{table_name}' created or already exists.")
    
    finally:
        cursor.close()
        conn.close()


# ## Delete table

# In[7]:


def delete_covertype_table(table_name):
    """
    Deletes the covertype_data table from the specified MySQL database if it exists.
    Credentials and connection info are read from environment variables.
    Parameters:
    - table_name (str): Name of the table to be DELETED.
    """
    cursor, conn = get_mysql_cursor()

    delete_table_sql = f"""DROP TABLE IF EXISTS `{table_name}`;"""

    try:
        cursor.execute(delete_table_sql)
        conn.commit()
        print(f"Table '{table_name}' deleted if it existed.")
    
    finally:
        cursor.close()
        conn.close()



# ## Read Table - get all data

# In[8]:


def fetch_all_covertype_records(table_name):
    """
    Fetches all records from the covertype_data table and prints the total number of records.
    Returns the result as a list of tuples.
    Parameters:
    - table_name (str): Name of the table.
    """
    cursor, conn = get_mysql_cursor()

    select_sql = f"""SELECT * FROM `{table_name}`;"""
    

    try:
        cursor.execute(select_sql)
        results = cursor.fetchall()
        print(f"Total records in '{table_name}': {len(results)}")
        #for row in results:
        #    print(row)
        return results
    finally:
        cursor.close()
        conn.close()



# # API Functions

# ## Get batch from API

# In[ ]:


def get_data_from_api(group_number):
    """
    Retrieves data from the API for the given group number.
    Raises an exception if the API indicates that there is no more data.
    """
    url = "http://api:80/data"
    params = {"group_number": group_number}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        print(f"Number of records retrieved on this batch: {len(data)}")
        if not data:
            raise ValueError("No more data available from the API.")

        return data

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        raise

    except ValueError as ve:
        print(f"API response error: {ve}")
        raise



# ## Insert batch into Table (with data validation - duplicates)

# In[9]:


def insert_unique_covertype_data(data, table_name):
    """
    Inserts only new records into the specified table.
    Checks for duplicates before inserting.

    Parameters:
    - data (list of tuples): Rows to insert.
    - table_name (str): Name of the table to insert data into.
    """
    cursor, conn = get_mysql_cursor()

    # Use parameterized table name safely
    check_sql = f"""
        SELECT COUNT(*) FROM `{table_name}`
        WHERE Elevation = %s AND Aspect = %s AND Slope = %s AND
              Horizontal_Distance_To_Hydrology = %s AND Vertical_Distance_To_Hydrology = %s AND
              Horizontal_Distance_To_Roadways = %s AND Hillshade_9am = %s AND
              Hillshade_Noon = %s AND Hillshade_3pm = %s AND
              Horizontal_Distance_To_Fire_Points = %s AND Wilderness_Area = %s AND
              Soil_Type = %s AND Cover_Type = %s
    """

    insert_sql = f"""
        INSERT INTO `{table_name}` (
            Elevation, Aspect, Slope, Horizontal_Distance_To_Hydrology,
            Vertical_Distance_To_Hydrology, Horizontal_Distance_To_Roadways,
            Hillshade_9am, Hillshade_Noon, Hillshade_3pm,
            Horizontal_Distance_To_Fire_Points, Wilderness_Area,
            Soil_Type, Cover_Type
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    inserted_count = 0

    try:
        for row in data:
            cursor.execute(check_sql, tuple(row))
            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute(insert_sql, tuple(row))
                inserted_count += 1

        conn.commit()
        print(f"Inserted {inserted_count} new rows into '{table_name}'.")
    finally:
        cursor.close()
        conn.close()



