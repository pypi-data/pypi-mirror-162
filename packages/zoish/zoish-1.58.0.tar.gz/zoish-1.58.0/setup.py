# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zoish', 'zoish.examples', 'zoish.feature_selectors', 'zoish.utils']

package_data = \
{'': ['*']}

install_requires = \
['catboost>=1.0.6,<2.0.0',
 'category-encoders>=2.5.0,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'fasttreeshap>=0.1.2,<0.2.0',
 'feature-engine>=1.4.1,<2.0.0',
 'imblearn>=0.0,<0.1',
 'lightgbm>=3.3.2,<4.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numba>=0.55.2,<0.56.0',
 'numpy<1.58.0',
 'optuna>=2.10.1,<3.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pip-licenses>=3.5.4,<4.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'shap>=0.41.0,<0.42.0',
 'xgboost>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'zoish',
    'version': '1.58.0',
    'description': 'This project uses shapely values for selecting Top n features compatible with scikit learn pipeline',
    'long_description': '# Zoish\n\nZoish is a package built to ease machine learning development. One of its main parts is a class that uses  [SHAP](https://arxiv.org/abs/1705.07874) (SHapley Additive exPlanation)  for a better feature selection. It is compatible with [scikit-learn](https://scikit-learn.org) pipeline . This package  uses [FastTreeSHAP](https://arxiv.org/abs/2109.09847) while calculation shap values and [SHAP](https://shap.readthedocs.io/en/latest/index.html) for plotting. \n\n\n## Introduction\n\nScallyShapFeatureSelector of Zoish package can receive various parameters. From a tree-based estimator class to its tunning parameters and from Grid search, Random Search, or Optuna to their parameters. Samples will be split to train and validation set, and then optimization will estimate optimal related parameters.\n\n After that, the best subset of features with higher shap values will be returned. This subset can be used as the next steps of the Sklearn pipeline. \n\n\n## Installation\n\nZoish package is available on PyPI and can be installed with pip:\n\n```sh\npip install zoish\n```\n\n\n## Supported estimators\n\n- XGBRegressor  [XGBoost](https://github.com/dmlc/xgboost)\n- XGBClassifier [XGBoost](https://github.com/dmlc/xgboost)\n- RandomForestClassifier \n- RandomForestRegressor \n- CatBoostClassifier \n- CatBoostRegressor \n- BalancedRandomForestClassifier \n- LGBMClassifier [LightGBM](https://github.com/microsoft/LightGBM)\n- LGBMRegressor [LightGBM](https://github.com/microsoft/LightGBM)\n\n## Usage\n\n- Find features using specific tree-based models with the highest shap values after hyper-parameter optimization\n- Plot the shap summary plot for selected features\n- Return a sorted two-column Pandas data frame with a list of features and shap values. \n\n\n## Examples \n\n### Import required libraries\n```\nfrom zoish.feature_selectors.optunashap import OptunaShapFeatureSelector\nimport xgboost\nfrom optuna.pruners import HyperbandPruner\nfrom optuna.samplers._tpe.sampler import TPESampler\nfrom sklearn.model_selection import KFold,train_test_split\nimport pandas as pd\nfrom sklearn.pipeline import Pipeline\nfrom feature_engine.imputation import (\n    CategoricalImputer,\n    MeanMedianImputer\n    )\nfrom category_encoders import OrdinalEncoder\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import (\n    classification_report,\n    confusion_matrix,\n    f1_score)\nimport lightgbm\nimport matplotlib.pyplot as plt\nimport optuna\n\n```\n\n### Computer Hardware Data Set (a classification problem)\n```\nurldata= "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"\n# column names\ncol_names=["age", "workclass", "fnlwgt" , "education" ,"education-num",\n"marital-status","occupation","relationship","race","sex","capital-gain","capital-loss","hours-per-week",\n"native-country","label"\n]\n# read data\ndata = pd.read_csv(urldata,header=None,names=col_names,sep=\',\')\ndata.head()\n\ndata.loc[data[\'label\']==\'<=50K\',\'label\']=0\ndata.loc[data[\'label\']==\' <=50K\',\'label\']=0\n\ndata.loc[data[\'label\']==\'>50K\',\'label\']=1\ndata.loc[data[\'label\']==\' >50K\',\'label\']=1\n\ndata[\'label\']=data[\'label\'].astype(int)\n\n```\n### Train test split\n```\nX = data.loc[:, data.columns != "label"]\ny = data.loc[:, data.columns == "label"]\n\nX_train, X_test, y_train, y_test =train_test_split(X, y, test_size=0.33, stratify=y[\'label\'], random_state=42)\n\n\n```\n### Find feature types for later use\n```\nint_cols =  X_train.select_dtypes(include=[\'int\']).columns.tolist()\nfloat_cols =  X_train.select_dtypes(include=[\'float\']).columns.tolist()\ncat_cols =  X_train.select_dtypes(include=[\'object\']).columns.tolist()\n```\n\n###  Define Feature selector and set its arguments  \n```\noptuna_classification_lgb = OptunaShapFeatureSelector(\n        # general argument setting        \n        verbose=1,\n        random_state=0,\n        logging_basicConfig = None,\n        # general argument setting        \n        n_features=4,\n        list_of_obligatory_features_that_must_be_in_model=[],\n        list_of_features_to_drop_before_any_selection=[],\n        # shap argument setting        \n        estimator=lightgbm.LGBMClassifier(),\n        estimator_params={\n        "max_depth": [4, 9],\n        "reg_alpha": [0, 1],\n\n        },\n        # shap arguments\n        model_output="raw", \n        feature_perturbation="interventional", \n        algorithm="auto", \n        shap_n_jobs=-1, \n        memory_tolerance=-1, \n        feature_names=None, \n        approximate=False, \n        shortcut=False, \n        plot_shap_summary=False,\n        save_shap_summary_plot=True,\n        path_to_save_plot = \'./summary_plot.png\',\n        shap_fig = plt.figure(),\n        ## optuna params\n        test_size=0.33,\n        with_stratified = False,\n        performance_metric = \'f1\',\n        # optuna study init params\n        study = optuna.create_study(\n            storage = None,\n            sampler = TPESampler(),\n            pruner= HyperbandPruner(),\n            study_name  = None,\n            direction = "maximize",\n            load_if_exists = False,\n            directions  = None,\n            ),\n        study_optimize_objective_n_trials=10, \n\n)\n```\n\n### Build sklearn Pipeline  \n```\n\n\npipeline =Pipeline([\n            # int missing values imputers\n            (\'intimputer\', MeanMedianImputer(\n                imputation_method=\'median\', variables=int_cols)),\n            # category missing values imputers\n            (\'catimputer\', CategoricalImputer(variables=cat_cols)),\n            #\n            (\'catencoder\', OrdinalEncoder()),\n            # feature selection\n            (\'optuna_classification_lgb\', optuna_classification_lgb),\n            # classification model\n            (\'logistic\', LogisticRegression())\n\n\n ])\n\n\npipeline.fit(X_train,y_train)\ny_pred = pipeline.predict(X_test)\n\n\nprint(\'F1 score : \')\nprint(f1_score(y_test,y_pred))\nprint(\'Classification report : \')\nprint(classification_report(y_test,y_pred))\nprint(\'Confusion matrix : \')\nprint(confusion_matrix(y_test,y_pred))\n\n```\n\nMore examples are available in the [examples](https://github.com/drhosseinjavedani/zoish/tree/main/zoish/examples). \n\n## License\nLicensed under the [BSD 2-Clause](https://opensource.org/licenses/BSD-2-Clause) License.',
    'author': 'drhosseinjavedani',
    'author_email': 'h.javedani@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/drhosseinjavedani/zoish',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
