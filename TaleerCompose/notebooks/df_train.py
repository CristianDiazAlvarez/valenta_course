import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

def train_models(X_train, y_train, random_state=42):
    """
    Train multiple classification models on the provided training data.
    
    Parameters:
    -----------
    X_train : pandas.DataFrame or numpy.ndarray
        Training feature data.
    y_train : pandas.Series or numpy.ndarray
        Training target data.
    random_state : int, default=42
        Random state for reproducibility for models that support it.
    
    Returns:
    --------
    dict
        A dictionary containing the trained models.
    """
    
    models = {}

    # 1. KNN
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    models['knn'] = knn

    # 2. Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    rf_model.fit(X_train, y_train)
    models['random_forest'] = rf_model

    # 3. SVM
    svm_model = SVC(kernel='linear', random_state=random_state)
    svm_model.fit(X_train, y_train)
    models['svm'] = svm_model

    # 4. Decision Tree
    dt_model = DecisionTreeClassifier(random_state=random_state)
    dt_model.fit(X_train, y_train)
    models['decision_tree'] = dt_model

    return models

# Example usage:
#if __name__ == "__main__":
    # This is an example of how you would use the train_models function.
    # You would typically load your data and split it before calling this function.
    
    # 1. Load your data (e.g., from a CSV file).
    # df = pd.read_csv('path/to/your/dataset.csv')
    
    # 2. Define features (X) and target (y).
    # X = df.drop('target_column', axis=1)
    # y = df['target_column']
    
    # 3. Split the data into training and testing sets.
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train the models using the training data.
    # trained_models = train_models(X_train, y_train)
    
    # Now you can use the trained_models for predictions or evaluation on the test set.
    # For example, to make a prediction with the Random Forest model:
    # predictions = trained_models['random_forest'].predict(X_test)
    
    # print("Models trained successfully!")
    # print(trained_models)
#    pass


if __name__== "__main__":
    print("Este es train")