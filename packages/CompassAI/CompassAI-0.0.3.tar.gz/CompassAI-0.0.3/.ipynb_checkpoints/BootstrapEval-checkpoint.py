import seaborn as sns
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.utils import resample

def bootstrap_eval(metrics, model, X, y, B=50, optional_output="sh", seed=None, return_train_score=False, return_estimator=False, **kwargs):
    """Model evaluation via bootstrap.
       Samples should be independent. Inappropriate for correlated samples, mixed model.
       Used for model evaluation. Selection and evaluation together should use nested CV instead.
    
    Args:
        metrics (dict): Dictionary of metric functions taking argument (y_true, y_pred) or (y_true, y_score). Common metrics include:
                        classification_metrics = {"accuracy": accuracy_score,
                                                  "average_precision": average_precision_score
                                                  "f1": f1_score,
                                                  "precision": precision_score,
                                                  "recall": recall_score,
                                                  "roc_auc": roc_auc_score}
                        clustering_metrics = {"adj_rand": adjusted_rand_score}
                        regression_metrics = {"mae": mean_absolute_error,
                                              "mse": mean_squared_error,
                                              "r2": r2_score}
                        `See sklearn.metrics for full list <https://scikit-learn.org/stable/modules/model_evaluation.html>`.
        model (object): Model object with method predict() and fit(). 
        X (array, DataFrame): Independent variables used to predict outcome y.
        y (array): Dependent variable.
        B (int, optional): Number of bootstrap resamples. Defaults to 50.
        optional_output (string, optional): String to specify if summary statistics and/or histogram should also be returned.
                                            If string contains "s", summary statistics is also printed.
                                            If string contains "h", histogram is also displayed.
                                            Defaults to "sh" (returning both summary statistics and histogram).
        seed (int, optional): Seed for random number generator. Defaults to None.
        return_train_score (boolean, optional): Whether to include train scores. Defaults to False.
        return_estimator (boolean, optional): Whether to return the estimators fitted on each bootstrap sample. Defaults to False.
        **kwargs (kwarg): Keyword argument for model object. For example, `batch_size=128, epochs=5`.
    Returns:
        (DataFrame): DataFrame containing bootstrap OOB evaluation for each metric
    """
    if seed:
        np.random.seed(seed)
        
    # fit and predict with full data
    model.fit(X, y, **kwargs)  # add handling for unsupervised task (clustering). add *kwarg

    # predict
    score_full = pd.Series(index=metrics.keys(), dtype="float")
    for metric in metrics: 
        score_full[metric] = metrics[metric](y, model.predict(X))
    

    # one bootstrap resmapling, model fitting, and evaluation
    def _one_bootstrap_eval(X, y, model, metrics, return_train_score, return_estimator, **kwargs):
        # bootstrap sample. OOB (not in bootstrap sample) is test set.
        train_index = resample(range(len(X)), replace=True, n_samples=len(X))
        test_index = np.setdiff1d(range(len(X)), train_index)
        if type(X) is pd.DataFrame:
            X_train = X.iloc[train_index]
            X_test = X.iloc[test_index]
        else:
            X_train = X[train_index,:]
            X_test = X[test_index,:]
        if type(y) is pd.DataFrame or type(y) is pd.Series:     
            y_train = y.iloc[train_index]
            y_test = y.iloc[test_index]
        else:
            y_train = y[train_index,:]
            y_test = y[test_index,:]

        # fit
        model.fit(X_train, y_train, **kwargs)  # add handling for unsupervised task (clustering). add *kwarg
        
        # predict
        score_test = pd.Series(index=metrics.keys(), dtype="float")
        for metric in metrics: 
            score_test[metric] = metrics[metric](y_test, model.predict(X_test))
        score = {"test_score": score_test}
        
        # train score
        if return_train_score is True:
            score_train = pd.Series(index=metrics.keys(), dtype="float")
            for metric in metrics:
                score_train[metric] = metrics[metric](y_train, model.predict(X_train))
            score.update({"train_score": score_train})
            
        # estimator
        if return_estimator is True:
            score.update({"estimator": model})
            
        return score

    out_parallel = Parallel(n_jobs=-2)( # -2 for all but one core. Use -1 for all cores.
        delayed(_one_bootstrap_eval)(
            X=X,
            y=y,
            model=model,
            metrics=metrics,
            return_train_score=return_train_score,
            return_estimator=return_estimator,
            **kwargs
        )
        for _ in range(B)
    )

    test_score = pd.DataFrame([i["test_score"] for i in out_parallel])
    
    if "s" in optional_output:
        print("Summary statistics of OOB scores")
        print(test_score.describe())
    if "h" in optional_output:
        ## bootstrap plot
        print("Distribution of OOB scores. Red points/lines indicate value from full data fit.")
        g = sns.PairGrid(test_score)
        # g.map_upper(sns.histplot)
        g.map_lower(sns.kdeplot, fill=True)
        g.map_diag(sns.histplot, kde=True)
        ## point on scatterplot for full data
        g.data = pd.DataFrame(score_full).T
        # g.map_upper(sns.scatterplot, color='red')
        g.map_lower(sns.scatterplot, color='red')
        ## line on histogram for full data
        for i in range(len(score_full)):
            g.axes[i][i].axvline(x=score_full[i], ls='--', linewidth=1, c='red')
    
    output = {"test_score": test_score}
    if "train_score" in out_parallel[0]:
        train_score = pd.DataFrame([i["train_score"] for i in out_parallel])
        output.update({"train_score": train_score})
    if "estimator" in out_parallel[0]:
        estimator = [i["estimator"] for i in out_parallel]
        output.update({"estimator": estimator})
    

    
    return output