import pandas as pd
import os

def read_dataframe(file_path):

    try:
        extension = os.path.splitext(file_path)[-1].lower()

        if extension == ".csv":
            df = pd.read_csv(file_path)
        elif extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)
        else:
            print(f"Error: Unsupported file format ({extension})")
            return None

        print(f"File {extension} loaded successfully.")
        return df

    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
    except pd.errors.ParserError:
        print("Error: Failed to parse the CSV file.")
    except ValueError as ve:
        print(f"Error reading Excel file: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None