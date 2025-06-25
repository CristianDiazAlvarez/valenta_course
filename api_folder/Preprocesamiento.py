from sklearn.model_selection import train_test_split

def split_data(df):

    #Receives a DataFramde and separates X and Y into Test and Train

    #Parameters:
        #df (pd.dataframe)
    #Returns
        #X_train, X_test, y_train, y_ttest


    #Separate features and target
    X = df.drop(columns=['class'])
    y = df['class']

    #Split
    X_train, X_test, y_train, y_test =  train_test_split(X,y, test_size=0.3, random_state=42)

    return X_train, X_test, y_train, y_test