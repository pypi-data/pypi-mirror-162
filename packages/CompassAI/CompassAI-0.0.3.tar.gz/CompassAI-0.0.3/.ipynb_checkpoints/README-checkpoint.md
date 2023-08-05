# Themis

Themis is a Python library that combines bootstrapping test set, feature importance, fairness evaluation, and model card into one wrapper.

## Installation

```bash
pip install -e "git+https://github.com/optum-labs/Themis#egg=Themis"
```

## Usage
           
Please see [binary_demo.ipynb](https://github.com/optum-labs/Themis/blob/main/Themis/notebooks/binary_demo.ipynb) for full example.
- `metrics` is dictionary of metrics
- `model` must have method `predict`. If model is sklearn pipeline, it should be composed of sklearn.compose.ColumnTransformer and the actual model.
- `X_test` is array-like object of shape (n_samples, n_features)
- `y_test` is array-like objecto of shape (n_samples,) or (n_samples, n_outputs)
- `sensitive_features` is array-like object of shape (n_samples,)
- `model_card_json` is a dictionary with specific schema (see below)
- `path` to specify where model card should be saved


```python
## Common metrics:
# classification_metrics = {"accuracy": accuracy_score,
#                           "average_precision": average_precision_score
#                           "f1": f1_score,
#                           "precision": precision_score,
#                           "recall": recall_score,
#                           "roc_auc": roc_auc_score}
# clustering_metrics = {"adj_rand": adjusted_rand_score}
# regression_metrics = {"mae": mean_absolute_error,
#                       "mse": mean_squared_error,
#                       "r2": r2_score}
# `See sklearn.metrics for full list <https://scikit-learn.org/stable/modules/model_evaluation.html>`.

import os
from Themis import ThemisCard
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

metrics = {"Accuracy": accuracy_score,
           "F1": f1_score,
           "Precision": precision_score,
           "Recall": recall_score}

# All model card dictionary keys are fixed and should not be changed (will throw an error)
model_card_json = \
{
    "model_details": {
        "name": "Census Dataset",
        "overview": "Logistic regression to predict whether income is >=50k",
        "owners": [
            {
                "name": "Pat Samranvedhya",
                "contact": "jirapat.samranvedhya@optum.com"
            }
        ],
        "version": {
            "name": "0.1",
            "date": "4/20/2022"
        },
        "references": [
            {
                "reference": "https://fairlearn.org/v0.7.0/api_reference/fairlearn.datasets.html?highlight=fetch_adult"
            }
        ]
    },
    "considerations": {
        "users": [
            {
                "description": "Data scientist"
            },
            {
                "description": "ML researchers"
            }
        ],
        "use_cases": [
            {
                "description": "Demonstrate Themis using Adult census"
            }
        ],
        "limitations": [
            {
                "description": "For demo purposes only"
            }
        ],
        "ethical_considerations": [
            {
                "name": "Performance might not be similar between race groups",
                "mitigation_strategy": "None. Parity difference is acceptable."
            }
        ]
    }
}

ThemisCard(metrics=metrics,
           model=unmitigated_estimator,
           X_test=X_test,
           y_test=y_test,
           sensitive_features=A_test,
           model_card_json=model_card_json,
           path = os.getcwd()
           )
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
