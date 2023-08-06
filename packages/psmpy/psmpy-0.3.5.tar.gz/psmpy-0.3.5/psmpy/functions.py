import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import math

def cohenD(df, treatment, metricName):
    """
    knn_matched -- Match data using k-nn algorithm
    Parameters
    ----------
    df : dataframe
       dataframe as input
    treatment : str
       intervention under invetigation
    metricName : str
       column being processed
    Returns
    balanced_match : float
      Cohen D value returned
    """
    treated_metric = df[df[treatment] == 1][metricName]
    untreated_metric = df[df[treatment] == 0][metricName]
    d = (treated_metric.mean() - untreated_metric.mean()) / math.sqrt(((treated_metric.count()-1)*treated_metric.std() **
                                                                       2 + (untreated_metric.count()-1)*untreated_metric.std()**2) / (treated_metric.count() + untreated_metric.count()-2))
    return d
