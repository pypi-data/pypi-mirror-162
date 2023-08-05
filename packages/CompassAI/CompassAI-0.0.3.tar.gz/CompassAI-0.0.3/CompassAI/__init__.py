from .BootstrapEval import bootstrap_eval
from .FairlearnAssess import assess
from .ModelCard import plot_to_str
import model_card_toolkit as mctlib
from IPython import display
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from interpret.ext.blackbox import TabularExplainer
import seaborn as sns
import warnings
import copy
from math import pi


def CompassAICard(metrics, model, X_test, y_test, sensitive_features, model_card_json, path, show_fi=True, **bs_kwargs):
    # get bootstrap plot
    plt.ioff() # suppress plotting
    bs_plot, metrics_full, metrics_ci = bootstrap_eval(metrics, model, X_test, y_test) #**bs_kwargs
    bs_plot = plot_to_str()
    
    # configure fairlearn plot layout
    n_lower = math.floor(math.sqrt(len(metrics)))
    if len(metrics) == n_lower*n_lower:
        layout = [n_lower, n_lower]
    elif len(metrics) <= n_lower*(n_lower+1):
        layout = [n_lower, n_lower+1]
    else:
        layout = [n_lower+1, n_lower+1]
        
    # get fairlearn plot
    fairlearn_plot, fairlearn_by_group, fairlearn_diff = assess(metrics, model, X_test, y_test, sensitive_features, layout=layout)
    fairness_plot = plot_to_str()
    
    if show_fi == True:
        # get feature importance plot
        if "pipeline" in str(type(model)):
            raw_model = model.steps[-1][1]
            preprocessor = model.steps[0][1]
        else:
            raw_model = model
            preprocessor = None
        with warnings.catch_warnings(): #suppress interpretml warning
            warnings.simplefilter("ignore")
            explainer = TabularExplainer(raw_model,
                                         initialization_examples=X_test, 
                                         features=X_test.columns, 
                                         # classes=['0', '1'], ##only for binary
                                         transformations=preprocessor
                                         )
            global_explanation = explainer.explain_global(X_test)
            importance_dict = global_explanation.get_feature_importance_dict()

        plt.figure() #new plot
        if len(importance_dict) > 10:
            n_keep = 10
        else:
            n_keep = len(importance_dict)
        importance_plot = sns.barplot(x=list(importance_dict.keys())[:n_keep],
                                      y=list(importance_dict.values())[:n_keep],
                                      color = sns.color_palette()[0]
                                      )
        plt.xticks(rotation=90)
        importance_plot = plot_to_str()
    

    
    # init and populate model card from json
    mct = mctlib.ModelCardToolkit(path)
    model_card = mct.scaffold_assets()
    model_card.from_json(model_card_json)
    
    # add disparity
    model_card.quantitative_analysis.performance_metrics = [
        mctlib.PerformanceMetric(type=f"{metrics_full.index[i]}",
                                 value=str(np.round(metrics_full[i], 4)),
                                 confidence_interval=mctlib.ConfidenceInterval(lower_bound=str(np.round(metrics_ci.iat[0,i], 4)),
                                                                               upper_bound=str(np.round(metrics_ci.iat[1,i], 4))
                                                                               )
                                )
        for i in range(len(metrics))
    ]
    
    ##### model registry output
    ## feature redundance
    # grab features that have less than 10% importance
    factor = 1.0/sum(importance_dict.values())
    trimmed_dict = {k: v*factor for k, v in importance_dict.items() if v*factor <= 0.1}
    reversed_dict = dict(reversed(list(trimmed_dict.items())))
    X_test_copy = copy.deepcopy(X_test)

    # normalize mse, mae
    normalizer = pd.Series(index=metrics.keys(), dtype="float")
    metrics_to_normalize = ["mean_absolute_error", "mean_squared_error"]
    for metric in metrics:
        if bool([x for x in metrics_to_normalize if(x in str(metrics[metric]))]):
            normalizer[metric] = metrics[metric](y_test, [np.mean(y_test)]*len(y_test))
        else:
            normalizer[metric] = 1

    redundance_counter = pd.Series(0, index=metrics.keys(), dtype="float")
    stopper = pd.Series(0, index=metrics.keys(), dtype="float")
    for key in reversed_dict.keys():
        if X_test_copy[key].dtype.kind in "biufc":  #bool, int, unsigned int, float, complex
            X_test_copy[key] = 0
        else:
            X_test_copy[key] = X_test_copy[key][0]  # set to first value
        # get performance
        score_trimmed = pd.Series(index=metrics.keys(), dtype="float")
        for metric in metrics: 
            score_trimmed[metric] = metrics[metric](y_test, model.predict(X_test_copy))
        change = ((metrics_full - score_trimmed)/normalizer)
        # only add to counter if change is small and stopper is zero (never crossed threshold before)
        redundance_counter = redundance_counter + ((np.abs(change) < 0.02)&(stopper==0)+0)
        # increase stopper if change crosses threshold
        stopper = stopper + (np.abs(change) >= 0.02)
        # stop when all metrics have crossed threshold at least once
        if np.prod(stopper) != 0:
            break
    redundance_rating = 1-redundance_counter/len(importance_dict)
    
    ## performance 
    performance_rating = metrics_full/normalizer
    
    ## reliability
    normalized_ci = metrics_ci/normalizer
    reliability_rating = 1-(normalized_ci.iloc[1,:] - normalized_ci.iloc[0,:])
    
    ## fairness
    fairness_rating = 1 - fairlearn_diff/normalizer
    
    ## model registry output
    model_registry_output = pd.concat([performance_rating, reliability_rating, redundance_rating, fairness_rating], axis=1)
    model_registry_output.columns = ["Performance", "Reliability", "Feature_robustness", "Fairness"]
    model_registry_output = model_registry_output*100
    
    ## radar plot
    def _make_spider(df, layout, index, title):

        # number of variable
        categories=list(df)
        N = len(categories)

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        ax = plt.subplot(layout[0],layout[1],index+1, polar=True, )

        # If you want the first axis to be on top:
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)

        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles[:-1], categories, color='grey', size=8)

        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([20,40,60,80], ["20","40","60","80"], color="grey", size=7)
        plt.ylim(0,100)

        # Ind1
        values = df.iloc[index,].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, color=sns.color_palette()[0], linewidth=2, linestyle='solid')
        ax.fill(angles, values, color=sns.color_palette()[0], alpha=0.4)

        # Add a title
        plt.title(title, size=11, y=1.1)
        
    radar_plot = plt.figure(facecolor="white")
    for row in range(0, len(model_registry_output.index)):
        _make_spider(df=model_registry_output, layout=layout, index=row, title=model_registry_output.index[row])
    radar_plot = plot_to_str()
    
    
    plt.ion() # turn plotting back on
    # add plot
    model_card.quantitative_analysis.graphics.description = ('Feature importance, bootstrapped performance (red indicates full test set), fairness assessment, model rating.')
    if show_fi == True:
        model_card.quantitative_analysis.graphics.collection = [
            mctlib.Graphic(image=importance_plot),
            mctlib.Graphic(image=bs_plot),
            mctlib.Graphic(image=fairness_plot),
            mctlib.Graphic(image=radar_plot),
        ]
    else:
        model_card.quantitative_analysis.graphics.collection = [
            mctlib.Graphic(image=bs_plot),
            mctlib.Graphic(image=fairness_plot),
            mctlib.Graphic(image=radar_plot),
        ]
    

    

    
    # update model card and display
    mct.update_model_card(model_card)
    html = mct.export_format()
    display.display(display.HTML(html))
    
    print(fairlearn_by_group)
    
    return model_registry_output