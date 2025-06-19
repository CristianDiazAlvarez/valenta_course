from sklearn.metrics import accuracy_score # Libreria requerida para su ejecucion

def evaluar_modelo(modelo, X_test, y_test, nombre_modelo="Modelo"): 
"""Se realizan la entrada de los valores para ejecutar la funcion, en este caso son los datos de testeo de entrada y de salida asi como el nombre del modelo el cual se va a ejecutar
"""
    y_pred = modelo.predict(X_test) # Se realiza el ingreso de la entrada de los datos de testeo
    accuracy = accuracy_score(y_test, y_pred) # Se calcula la presicion del modelo con los datos ingresados
    print(f"Precisión del {nombre_modelo}: {accuracy:.4f}") # Se realiza la impresion de los resultados
    return accuracy # Al final de la funcion se debe retornar el valor, para eso se usa esta linea final
