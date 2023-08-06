from sklearn.base import BaseEstimator,ClassifierMixin


class CustomLogisticRegression(BaseEstimator,ClassifierMixin):
    def __init__(self):
        pass 
    
    def fit(self, x, y):
        pass
    
    def predict(self, x):
        pass 
    
    
    def get_params(self, deep=True):
        return super().get_params(deep)
    
    def set_params(self, **params):
        return super().set_params(**params)