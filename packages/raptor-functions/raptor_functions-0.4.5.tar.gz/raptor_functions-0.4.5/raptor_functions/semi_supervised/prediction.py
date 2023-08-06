
import joblib
from io import BytesIO
import boto3
import mlflow
from mlflow.tracking import MlflowClient
from tsfresh.feature_extraction import settings, extract_features

from itertools import combinations, product
import numpy as np
import pandas as pd
from .copkmeans.cop_kmeans import cop_kmeans
import random
import mlflow.pyfunc
from scipy.spatial import distance_matrix
from scipy.spatial.distance import cdist

from supervised.feature_extraction import add_offset_gradient




# REMOTE_TRACKING_URI = 'http://ec2-3-10-175-206.eu-west-2.compute.amazonaws.com:5000/'
REMOTE_TRACKING_URI = "http://ec2-18-133-140-90.eu-west-2.compute.amazonaws.com:5000/"




def get_model_and_features(model_uri, tracking_uri=REMOTE_TRACKING_URI):
    
    client = MlflowClient(tracking_uri=REMOTE_TRACKING_URI)
    
    # Load model as a Sklearn Model.
    loaded_model = mlflow.pyfunc.load_model(model_uri)
    run_id = loaded_model.metadata.run_id
    relevant_features = client.get_run(run_id).data.tags['relevant_features'].replace("'", '')[1:-1].split(', ')
    offset = bool(client.get_run(run_id).data.tags['offset'])
    gradient = bool(client.get_run(run_id).data.tags['gradient'])

    return loaded_model, relevant_features, offset, gradient




def get_prediction_features(
    X, model_uri, tracking_uri=REMOTE_TRACKING_URI,  id="exp_unique_id", timesteps="timesteps"
):


    
    _, relevant_features, offset, gradient = get_model_and_features(model_uri)

    X = add_offset_gradient(X, offset=offset, gradient=gradient)
    # df = X.join(y)

    fc_parameters = settings.from_columns(relevant_features)

    prediction_data = extract_features(
        X, kind_to_fc_parameters=fc_parameters, column_id=id, column_sort=timesteps
    )

    prediction_data.columns = prediction_data.columns.str.replace('["]', "")


    return prediction_data




def ss_prediction(prediction_data, centroids):

    prediction_data = np.array(prediction_data)

    # print('Type: ', type(prediction_data))

    # print('N Shape: ', prediction_data.shape)
    # print('N Dimensions: ', prediction_data.ndim)

    # if prediction_data.ndim == 1:
    
    if prediction_data.ndim == 0:

        dist_matrix = pd.DataFrame(cdist(np.array(prediction_data).reshape(-1,1), centroids))
        cluster = dist_matrix.idxmin(axis=1)
        return cluster
    
    if prediction_data.ndim == 1:
        dist_matrix = pd.DataFrame(cdist(np.array(prediction_data).reshape(1,-1), centroids))
        cluster = dist_matrix.idxmin(axis=1)
        return cluster

        

def ss_predictions(prediction_data, centroids, mode='single'):
    # print('type: ', type(prediction_data))

    if (isinstance(prediction_data, pd.Series)) and mode=='multi':
        preds = prediction_data.apply(ss_prediction, centroids=centroids)
        return preds

    if (isinstance(prediction_data, pd.DataFrame)):
        preds = []
        for i in prediction_data.values:
        # print()
            pred = ss_prediction(i, centroids)
            preds.append(pred)
        return preds

    pred = ss_prediction(prediction_data, centroids)
    return pred


def make_prediction(df, model_uri, tracking_uri=REMOTE_TRACKING_URI,  id="exp_unique_id", timesteps="timesteps"):

    

    loaded_model, _, _, _ = get_model_and_features(model_uri, tracking_uri=REMOTE_TRACKING_URI)

    prediction_data = get_prediction_features(df, model_uri, tracking_uri,  id, timesteps)

    prediction = loaded_model.predict(prediction_data)

    return prediction