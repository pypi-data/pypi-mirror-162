

from raptor_functions.supervised.feature_extraction import  *
# from raptor_functions.unsupervised.train import *
# from raptor_functions.supervised.preprocess import  *
import optuna
import mlflow
import os

# try:
#     from sklearn.utils import safe_indexing
# except ImportError:
#     from sklearn.utils import _safe_indexing

from pathlib import Path
from mlflow.models.signature import infer_signature
from pycaret.clustering import *
from .ss_clustering import *
# from raptor_functions.semi_supervised.ss_clustering import *



# Importing the Packages:
import optuna
import mlflow
import os

# try:
#     from sklearn.utils import safe_indexing
# except ImportError:
#     from sklearn.utils import _safe_indexing

from pathlib import Path
from mlflow.models.signature import infer_signature
from explainerdashboard import ExplainerDashboard, ClassifierExplainer


















SENSORS_FEATURES = [
    "sensor_1",
    "sensor_2",
    "sensor_3",
    "sensor_4",
    "sensor_5",
    "sensor_6",
    "sensor_7",
    "sensor_8",
    "sensor_9",
    "sensor_10",
    "sensor_11",
    "sensor_12",
    "sensor_13",
    "sensor_14",
    "sensor_15",
    "sensor_16",
    "sensor_17",
    "sensor_18",
    "sensor_19",
    "sensor_20",
    "sensor_21",
    "sensor_22",
    "sensor_23",
    "sensor_24",
]

STAGES = ["baseline", "absorb", "pause", "desorb", "flush"]
TARGET_COL = "result"
# REMOTE_TRACKING_URI = "http://ec2-3-10-175-206.eu-west-2.compute.amazonaws.com:5000/"
REMOTE_TRACKING_URI = "http://ec2-18-133-140-90.eu-west-2.compute.amazonaws.com:5000/"



# 'http://ec2-3-10-210-150.eu-west-2.compute.amazonaws.com:5000/'



def get_plots(model):

    model_attributes = dir(model)

    plot_dir = os.path.join(os.getcwd(), "plots")
    Path(plot_dir).mkdir(parents=True, exist_ok=True)

    try:
        plot_model(model, 'elbow', save=plot_dir)
    except:
        pass

    try:
        plot_model(model, 'cluster', save=plot_dir)
    except:
        pass

    try:
        plot_model(model, 'tsne', save=plot_dir)
    except:
        pass

    try:
        plot_model(model, 'silhoutte', save=plot_dir)
    except:
        pass

    try:
        plot_model(model, 'distance', save=plot_dir)
    except:
        pass

    try:
        plot_model(model, 'distribution', save=plot_dir)
    except:
        pass

    
    
    
    
    

    
    mlflow.log_artifact(plot_dir)





def objective(trial, df, study_name, model_mode):



    mlflow.set_experiment(study_name)

    mlflow.set_tracking_uri(REMOTE_TRACKING_URI)


    unique_id = 'exp_unique_id'
    label = 'result'
    num_clusters = 2
    # model_name='kmeans'


    

    df_offset = df.filter(regex='offset')
    df_gradient = df.filter(regex='gradient')

    if len(df_offset.columns) > 0:
        offset = True
    else:
        offset = False

    if len(df_gradient.columns) > 0:
        gradient = True
    else:
        gradient = False

    mlflow.start_run()


    X = df.drop(TARGET_COL, axis=1)

    features = X
    relevant_features = list(X.columns)
    df_cluster, centroids, map_dict = get_cluster_labels(df)

    model = SSC(centroids, map_dict)

    # # remove unwanted characters from the column names
    # df_copy.columns = df_copy.columns.str.replace('["]', "")

    # features = df_copy.drop(TARGET_COL, axis=1)

    # df_copy["result"] = df_copy["result"].replace({"Control": 0, "Covid": 1})





    model_name = "ssc"
    

    # get_plots(model)

    # metrics = get_metrics()
    # print(metrics)
    # mlflow.log_metrics(metrics)


    # try:
        # signature = infer_signature(features, predict_model(model, data=features))
    # signature = infer_signature(features, np.array(ss_predictions(X, centroids)))

    # mlflow.pyfunc.log_model(model)
    mlflow.pyfunc.log_model(artifact_path=model_name,python_model=model)
    # mlflow.pyfunc.log_model(artifact_path=model_name,python_model=model, signature=signature)


    # mlflow.pyfunc.log_model(artifact_path="model",python_model=ETS_Exogen, conda_env=conda_env)


        # mlflow.sklearn.log_model(model, artifact_path=model_name, signature=signature)
    # mlflow.pyfunc.log_model(model, artifact_path=model_name, signature=signature)


    # except:
    #     pass


    # model_params = model.get_params()



        
    

    




    # mlflow.log_metrics(metrics)

    try:
        # mlflow.set_tag('features', features)
        mlflow.set_tag("relevant_features", relevant_features)

    except:
        pass

    mlflow.set_tag("model_name", model_name)
    mlflow.set_tag("centroids", centroids)

    mlflow.set_tag("offset", offset)
    mlflow.set_tag("gradient", gradient)
    mlflow.set_tag("map_dict", map_dict)


    # mlflow.set_tag("model_mode", model_mode)

    mlflow.end_run()


def train_experiments(
    df, study_name="semi-supervised", direction="maximize", model_mode="random", n_trials=5
):
    """trains several models during different trials and logs them. Experiemnt can be tracked on "http://ec2-3-10-175-206.eu-west-2.compute.amazonaws.com:5000/"


    Args:
        df (pandas dataframe): dataframe of cyclic sensor data to be used for training
        study_name (str, optional): optuna study name to use. Defaults to 'unsupervised'.
        direction (str, optional): direction of objective. Defaults to 'maximize'.
        model_mode (str, optional): _description_. Defaults to 'random'.
        n_trials (int, optional): number of times to run experiments. Defaults to 5.
    """

    study = optuna.create_study(study_name=study_name, direction=direction)
    study.optimize(
        lambda trial: objective(trial, df, study_name, model_mode), n_trials=n_trials
    )

    print("Click on this link to track experiments: ", REMOTE_TRACKING_URI)



























