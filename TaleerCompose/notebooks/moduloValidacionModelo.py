from sklearn.metrics import accuracy_score # Libreria requerida para su ejecucion

def evaluar_modelo(modelos:dict, X_test, y_test):

    """
    Se realizan la entrada de los valores para ejecutar la funcion, en este caso son los datos de testeo de entrada y de salida asi como el nombre del modelo el cual se va a ejecutar
    """
    accuracy_models={}
    for name,model in modelos.items():
        
        y_pred = model.predict(X_test) # Se realiza el ingreso de la entrada de los datos de testeo
        accuracy = accuracy_score(y_test, y_pred) # Se calcula la presicion del modelo con los datos ingresados
        accuracy_models[name]=accuracy
    
    return accuracy_models # Al final de la funcion se debe retornar el valor, para eso se usa esta linea final