from ReadDataframe import read_dataframe
from clean_function import clean_data
from Preprocesamiento import split_data
from df_train import train_models
from moduloValidacionModelo import evaluar_modelo
import joblib
import sys


def train_models2(filename=""):
    assert filename!="","Archivo no definido"
    df=read_dataframe(filename)
    df=clean_data(df)

    X_train, X_test, y_train, y_test=split_data(df)

    models=train_models(X_train,y_train)

    accuracy_models=evaluar_modelo(models,X_test,y_test)

    # ...existing code...

    # Save the Random Forest model as a .pkl file
    with open("model.pkl", "wb") as f:
        joblib.dump(models["random_forest"], f)
    
    # ...existing code...

    #print(df.head())
    #print(len(X_train),len(X_test),len(y_train),len(y_test))
    #print(models)
    #print(accuracy_models)

if __name__== "__main__":
    if len(sys.argv) > 1:
        param1 = sys.argv[1]
        print(param1)
    train_models2(param1)



