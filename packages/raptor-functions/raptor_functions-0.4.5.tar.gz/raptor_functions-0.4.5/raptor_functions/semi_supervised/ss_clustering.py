
from itertools import combinations, product
import numpy as np
import pandas as pd
from .copkmeans.cop_kmeans import cop_kmeans
import random
import mlflow.pyfunc
from scipy.spatial import distance_matrix
from scipy.spatial.distance import cdist


def make_random_choice(lst, links):
    new_list = []
    for x in range(links):
        choice = random.choice(lst)
        new_list.append(choice)
        if choice in new_list:
            lst.remove(choice)
    return new_list


def get_must_link(control_idx, covid_idx, links):
    control_comb = list(combinations(control_idx, 2))
    covid_comb = list(combinations(covid_idx, 2))
    
    must_link_control = make_random_choice(control_comb, links//2)
    must_link_covid = make_random_choice(covid_comb, links//2)

    return must_link_control + must_link_covid

  
def get_cannot_link(control_idx, covid_idx, links):
    covid_control_comb = list(product(covid_idx, control_idx))
    must_link_covid = make_random_choice(covid_control_comb, links)
    return must_link_covid



def get_constraints(df, links=4):

    control_idx = list(df[df['result'] == 'Control'].index)
    covid_idx = list(df[df['result'] == 'Covid'].index)

    must_link = get_must_link(control_idx, covid_idx, links)
    cannot_link = get_cannot_link(control_idx, covid_idx, links)
    
    return must_link, cannot_link

def replace_sample(df, column, fraction, val_replace):

    df_copy = df.copy()
    idx = df_copy[column].sample(frac=fraction).index
    df_copy.loc[idx, column] = val_replace

    return df_copy

def map(combined_df, label):
    df = combined_df[combined_df['result'] == label]
    cluster_value_counts = df['cluster'].value_counts()
    
    print('df: ', df)
    print('df_cluster: ', df['cluster'])
    print('label: ', label)
    print('cluster_value_counts: ', cluster_value_counts)
    print('cluster_value_value_type: ', type(cluster_value_counts))
    cluster = cluster_value_counts.idxmax()
    cluster_len = cluster_value_counts[cluster]
    if cluster_len / len(df) > 0.5:  
        return {cluster: label}
    return {cluster: -1}

def get_mappings(combined_df):
    
    map_dict = {}
    covid_map = map(combined_df, 'Covid')
    control_map = map(combined_df, 'Control')

    map_dict.update(control_map)
    map_dict.update(covid_map)

    return map_dict


def get_cluster_labels(df, k=2, links=4):

    must_link, cannot_link = get_constraints(df, links)

    print('must_link: ', must_link)
    print('cannot_link: ', cannot_link)
    X = df.drop('result', axis=1)

    input_matrix = X.values
    print('input_matrix: ', input_matrix)

    clusters, centroids = cop_kmeans(dataset=input_matrix, k=k, ml=must_link, cl=cannot_link)

    print('clusters: ', clusters)
    print('centroids: ', centroids)
    print('clusters len: ', len(centroids))
    print('clusters len: ', len(clusters))
    

    combined_df = df.join(pd.DataFrame(clusters, columns=['cluster']))

    map_dict = get_mappings(combined_df)

    map_dict = {0: 'Control', 1: 'Covid'}

    print('map_dict: ', map_dict)

    combined_df['cluster_label'] = combined_df['cluster'].map(map_dict)

    return combined_df, centroids, map_dict






def ss_prediction(prediction_data, centroids):

    # prediction_data = np.array(prediction_data)

    # print('Type: ', type(prediction_data))

    # print('N Shape: ', prediction_data.shape)
    # print('N Dimensions: ', prediction_data.ndim)

    print('Type: ', type(prediction_data))
    print('prediction data: ', prediction_data)

    if len(prediction_data.columns) == 1:
    
    # if prediction_data.ndim == 0:

        dist_matrix = pd.DataFrame(cdist(np.array(prediction_data).reshape(-1,1), centroids))
        cluster = dist_matrix.idxmin(axis=1)
        return cluster#.values[0]
    

    if len(prediction_data.columns) > 1:

    # if prediction_data.ndim == 1:


        dist_matrix = pd.DataFrame(cdist(np.array(prediction_data).reshape(-1,1), centroids))
        cluster = dist_matrix.idxmin(axis=1)
        return cluster#.values[0]

        
def pred(data, centroids):
    distances = [np.linalg.norm(data - centroid) for centroid in centroids]
    classification = distances.index(min(distances))
    return classification

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
        return pd.DataFrame(np.array(preds))

    pred = ss_prediction(prediction_data, centroids)
    return pred
    
    # if prediction_data.ndim == 0:
    #     pred = ss_prediction(prediction_data, centroids)
    #     return pred
    # if prediction_data.ndim == 1:
    #     pred = ss_prediction(prediction_data, centroids)
    #     return pred

    # print(prediction_data)
    # return preds

# Define the model class
class SSC(mlflow.pyfunc.PythonModel):

    def __init__(self, centroids, map_dict):
        self.centroids = centroids
        self.map_dict = map_dict

    def predict(self, context, model_input):

        prediction = pred(model_input, self.centroids)

        return [prediction]

        # return self.map_dict[prediction]


