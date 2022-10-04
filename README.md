cookiecutter-python-analysis
==============================

Cookiecutter inspired template for CorrelAid Python analysis projects.
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

# What is this project about?
summarize in three sentences what this project is about and what central features it has.
# Setup 
## Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data                <- see README in data folder
    │   ├── processed_gdpr        
    │   ├── processed     
    │   └── raw        
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         and a short `-` delimited description, e.g.
    │                         `01-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------



## Installing Packages

How can a environment for your project be created/updated? 

Please make sure that the setup steps are:

- platform-independent (e.g. be aware of issues [like this](https://stackoverflow.com/questions/41274007/anaconda-export-environment-file)), at least MacOS and Windows (this is important in case CorrelAid employees have to provide support after the project has ended.
- computer-independent: must work for all team members!

## Data

You need the following data files in order to run this project: 

_include output from `tree` command (or similar on windows)_
# Developer information
[the following can also be moved to the wiki if you decide to have one]

## Definition of Done
Default Definition of Done can be found [here](https://github.com/CorrelAid/definition-of-done). Adapt if needed.

## Code styling

# How to operate this project?
[the following can also be moved to the wiki if you decide to have one]

explain how the output(s) of this project can be handled/operated, for example:

- how to create reports
- where to create/find the data visualizations 
- how to update data 
- what would need to be updated if someone wanted to re-run your analysis with different data

# Limitations

be honest about the limitations of your project, e.g.: 

- methodological: maybe another model would be more suitable?
- reproducibility: what are limits of reproducibility? is there something hard-coded/specific to the data that you used?
- best practices: maybe some code is particularly messy and people working on it in the future should know about it in advance?


