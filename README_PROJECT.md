# What is this project about? - The Problem & Goal

To become more data driven in their work, non-profits need to collect data. As an open source and privacy-aware software, [Limesurvey](https://www.limesurvey.org/) is a good choice, especially for German NPOs.

CFE uses Limesurvey to collect anti-discrimination and inclusion data (also known as equality data). Right now, data extraction from Limesurvey and initial data cleaning is done with a quite hacky R script with 1500 lines.

The goal of this  project track is to design a pipeline to

1. **extract** data from Limesurvey from its database via SSH tunnel
2. perform necessary **transformations** to clean the raw data such as flagging speeders, creating variables for GDPR consent etc. and log the number of affected respondents for each step.
3. **load** the cleaned data into a Postgres database

The goal is that the resulting code is not specific to CFE data, but can be used by CFE and other NPOs working with Limesurvey in a “plug-and-play” way.

# Setup

## Project Organization

TO BE DISCUSSED:

------------

    ├── LICENSE
    ├── Makefile            <- Makefile with commands like `make data` or `make train`
    ├── README.md           <- The top-level README for developers using this project.
    ├── data                <- see README in data folder
    │   ├── processed_gdpr
    │   ├── processed
    │   └── raw
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
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
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------
## Dependency Management: Installing Packages

TODO add information on python package management

How can an environment for your project be created/updated?

Please make sure that the setup steps are:

- platform-independent (e.g. be aware of issues [like this](https://stackoverflow.com/questions/41274007/anaconda-export-environment-file)), at least MacOS and Windows (this is important in case CorrelAid employees have to provide support after the project has ended.
- computer-independent: must work for all team members!

## Data Access

You need the following data files in order to run this project:

``` r
system2("tree", c("data/raw")) # works on mac and potentially linux.
```

To access the data for this project, you first need to get
secrets/passwords.

To get them, proceed as follows:

1.  Check the description below for the “yopass link” to access the auth info
2.  Lisa will share the password to decrypt the message
3.  Click on the link and enter the password to decrypt the message
4.  Follow the specific instructions for your data below.

### Access Data in Limesurvey Playground Server

To access the data from the self-hosted Limesurvey Server and its MariaDB, you need to:

1. connect to the virtual machine/server that Limesurvey is running on. This you do using SSH.
2. then you can connect to the SQL database where the data is stored

Interesting tables to take a look at first are probably:

- 'lime_questions'
- 'lime_question_attributes'
- 'lime_survey_916481'
- 'lime_survey_916481_timings'
- 'lime_labels'
- 'lime_answers'

#### Connect with your DB-Tool of Choice (e.g. Beekeeper Studio)
Enter the information provided in the Yopass Textfile and save the connection.

#### Connect with Python
TODO

Store the authentification information in your local environment (it should never be commited to the git repo).

Copy the content from the decrypted secret link. It should look something like this:
```
# logins for LimeSurvey Server and MariaDB
LIMESURVEY_SSH_HOST='your-limesurvey-ssh-url'
LIMESURVEY_SSH_USER='your-limesurvey-ssh-user'
LIMESURVEY_SSH_PASSWORD='your-limesurvey-ssh-pw'
LIMESURVEY_SSH_PORT='22'
LIMESURVEY_DB_USER='your-limesurvey-db-user'
LIMESURVEY_DB_PASSWORD='your-limesurvey-db-pw'
LIMESURVEY_DB_DEFAULT='your-limesurvey-db-name'
LIMESURVEY_DB_PORT='3306'
```

#### Connect with RStudio
To do this, let's first store some information in the `.Renviron` file so that we don't accidentally commit secret information to GitHub:

```
# set up information in .Renviron
usethis::edit_r_environ()
```

Copy the content from the decrypted secret link. It should look something like this:
```
# logins for LimeSurvey Server and MariaDB
LIMESURVEY_SSH_HOST='116.203.20.255'
LIMESURVEY_SSH_USER='your-limesurvey-ssh-user'
LIMESURVEY_SSH_PASSWORD='your-limesurvey-ssh-pw'
LIMESURVEY_SSH_PORT='22'
LIMESURVEY_DB_USER='your-limesurvey-db-user'
LIMESURVEY_DB_PASSWORD='your-limesurvey-db-pw'
LIMESURVEY_DB_DEFAULT='your-limesurvey-db-name'
LIMESURVEY_DB_PORT='3306'
```

Restart your R session (Session -> Restart R Session or `.rs.restartR()`)

Now you have to create the SSH tunnel - don't worry if you don't know what this means. In essence, it allows us to a) connect from our laptop to the server and then b) use this connection to connect and interact with the Limesurvey database.

In the R console, run:

```
glue::glue("ssh -L localhost:5555:127.0.0.1:3306 {ssh_user}@{ssh_host}")
```

this builds a "tunnel" from your local machine on port 5555 to the port 3306 (the MariaDB port) on the server. We can then use port 5555 on our machine to connect and communicate with the MariaDB.

##### MacOS/Linux/Windows with WSL or working SSH
If you have:

- MacOS
- Linux
- a Windows machine but have a way to run SSH commands in the console (e.g. in [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install))

Copy the command to your terminal of choice and run it. You'll be prompted to enter a password which you can copy from the `.Renviron` file (`LIMESURVEY_SSH_PASSWORD`)

Once you have successfully opened the connection, run `src/00-setup-limesurvey.R`

:warning: the SSH connection might close after a couple of minutes, so you might have to reconnect in the terminal.

##### Windows
If you have never worked with SSH before, ask Frie or the project lead about it. They'll have a look together with you.


### Access Cleaned Data in Coolify Postgres Database

This project team will try to create the pipeline that leads to a “cleaned data” structure in a Postgres. This means
that data is already Q&A'ed, cleaned and restructured. For reference to the end state, you can connect to the Coolify Postgres DB which contains the current state of CFE's cleaned data.

Follow the instructions above, but instead use the credentials for the COOLIFY_PG database.

Copy the content from the decrypted secret link. It should look something like this:

```
# logins for Coolify Postgres DB
COOLIFY_PG_NAME='your-postgres-default-db-name'
COOLIFY_PG_HOST='your-postgres-url'
COOLIFY_PG_PORT='9001'
COOLIFY_PG_USER='your-postgres-user-name'
COOLIFY_PG_PASSWORD='your-postgres-pw'
```

### Access Empty Coolify MariaDB Database

Follow the instructions above, but instead use the credentials for the COOLIFY_PG database.
Copy the content from the decrypted secret link. It should look something like this:

```
# logins for Coolify Postgres DB
COOLIFY_MARIA_NAME='your-maria-default-db-name'
COOLIFY_MARIA_HOST='your-maria-url'
COOLIFY_MARIA_PORT='9000'
COOLIFY_MARIA_USER='your-maria-user-name'
COOLIFY_MARIA_PASSWORD='your-maria-user-pw'
```

### Access Coolify Playground Postgres for Development

let Lisa know if this is needed

# Developer information
[the following can also be moved to the wiki if you decide to have one]

## Definition of Done
Default Definition of Done can be found [here](https://github.com/CorrelAid/definition-of-done). Adapt if needed.

## Code styling

TODO

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
