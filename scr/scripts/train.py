
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

def split_train_val_test(df, target_variable, test_size=0.2, val_size=0.2):
    X = df.drop(columns=['timestamp', target_variable])
    y = df[target_variable]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_size, shuffle=False)
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_xgboost(X_train, y_train, X_val, y_val, params):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    model = xgb.train(params, dtrain, num_boost_round=1000, evals=[(dtrain, 'train'), (dval, 'val')], early_stopping_rounds=10)
    return model

def predict_xgboost(model, X_test):
    dtest = xgb.DMatrix(X_test)
    y_pred = model.predict(dtest)
    return y_pred