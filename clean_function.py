import numpy as np
import pandas as pd

def clean_data(df):
    df.drop('ID_paciente', axis=1, inplace=True)
    df.drop('Registro', axis=1, inplace=True)
    df.drop('Notas', axis=1, inplace=True)

    # Change: Pass a list of values to replace to the .replace method for the 'Gender' column
    df['Gender'] = df['Gender'].replace(['mle','m','MALE','Male','M'], 1)
    df['Gender'] = df['Gender'].replace(['Female','f','femlae','FEMALE','F'], 0)
    df['class'] = df['class'].replace({'Positive': 1, 'Negative': 0})

    for col in df.columns :
        if col != 'Gender' and col != 'class':
            print(col)
            df[col].replace(['Y', 'YES', 'Yes', 'yes', '1'], 1,inplace=True)
            df[col].replace(['N', 'NO', 'No', 'no', '0'], 0,inplace=True)
        else:
            pass

    df['Age'] = df['Age'].apply(lambda x: x if 16 <= x <= 90 else np.nan)
    df['Age'].fillna(df['Age'].median(), inplace=True)
    df['Age'] = df['Age'].astype(int)
    df['Polyur1a']=df['Polyur1a'].fillna(df['Polyur1a'].mode()[0])
    df['Obesity']=df['Obesity'].fillna(df['Obesity'].mode()[0])