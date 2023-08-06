# from raptor_functions.supervised.prediction import get_production_model, make_prediction_with_pm
from raptor_functions.supervised.datasets import get_data
import pandas as pd
from raptor_functions.supervised.prediction import make_ensemble_prediction, make_prediction_with_pm










unique_id = 'exp_unique_id'
label = 'result'





def label(row, preds):
    for i, pred in enumerate(preds):
        if i == row['exp_unique_id']:
            return pred




def get_pseudo_labeled_data(X):

    preds = make_prediction_with_pm(X)
    X[label] = X.apply(lambda row: label(row, preds), axis=1)

    return X

def retrain(df_labeled, df_unlabeled):

    X_unlabeled = df_unlabeled.drop(label, axis=1)
    pseudo_labeled_data = get_pseudo_labeled_data(X_unlabeled)
    df_all = pd.concat([df_labeled, pseudo_labeled_data])

    return df_all


