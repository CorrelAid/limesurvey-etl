# Welcome to Limesurvey ETL

This is the documentation of the Limesurvey ETL project. The goal is to provide an ETLaaS (ETL as a Service) application to process data from [Limesurvey](https://www.limesurvey.org/).


## What is this project about? - The Problem & Goal

To become more data driven in their work, non-profits need to collect data. As an open source and privacy-aware software, [Limesurvey](https://www.limesurvey.org/) is a good choice, especially for German NPOs.

CFE uses Limesurvey to collect anti-discrimination and inclusion data (also known as equality data). Right now, data extraction from Limesurvey and initial data cleaning is done with a quite hacky R script with 1500 lines.

The goal of this  project track is to design a pipeline to

1. **extract** data from Limesurvey from its database via SSH tunnel
2. perform necessary **transformations** to clean the raw data such as flagging speeders, creating variables for GDPR consent etc. and log the number of affected respondents for each step.
3. **load** the cleaned data into a Postgres database

The goal is that the resulting code is not specific to CFE data, but can be used by CFE and other NPOs working with Limesurvey in a “plug-and-play” way.

(from the [Calls for
Applications](https://citizensforeurope.notion.site/Calls-for-Applications-Data4Good-Projects-A-survey-research-ecosystem-for-diversity-and-visibility-ed7b72486a8d4bff8b74eaa851b3f029#873799b87fff4abe86b932e9a261972f))

## Project Organization

TO BE DISCUSSED:

------------

    ├── LICENSE
    ├── README.md           <- The top-level README for developers using this project.
    │
    ├── docs               <- Markdown files used my [mkdocs](https://www.mkdocs.org/) to generate documentation.
    │
    ├── requirements.txt   <- The requirements file used in the docker-compose.yml
    │
    ├── limesurvey_etl     <- Source code for use in this project.
    │   ├── config         <- Contains the pydantic models for configuring ETL jobs
    │   │   └── extract_config
    │   │   └── transform_config
    │   │   └── load_config
    │   │
    │   ├── connectors         <- Contains the code used to connect to external systems
    │   ├── extract            <- Contains the code used to extract data
    │   │
    │   ├── transform          <- Contains the code used to transform data
    │   │
    │   ├── load               <- Contains the code used to load data to target systems
    │   │
    │   ├── etl_pipeline.py               <- Contains code used to define an ETL pipeline
    │   └── transformation_pipline.py <- Contains code defining a transformation pipeline
    │
    └── poetry.

### Access Data in Limesurvey Playground Server

[Yopass Link](https://yopass.se/#/s/f3683c87-c3ee-42f6-affa-f0a94ac596c1)

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

### Access Cleaned Data in Coolify Postgres Database
[Yopass Link](https://yopass.se/#/s/810842d9-b75b-4448-81d9-26bfd9e02d24)

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
[Yopass Link](https://yopass.se/#/s/c5d632ea-a00a-4f9d-aa74-432a70c4f8f9)

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

# Limitations

- This project is still work-in-progress. Please report any bugs you may encounter.
- We couldn't collect any user feedback so far and the project structure solely relies on our own assumptions re. how to offer an ETLaaS (ETL as a Service) platform for Limesurvey data.
- Adding proper unit and integration tests is an open todo. There might be uncaught bugs in this application.

# Partner organization

This project was conducted in collaboration with the [Vielfalt entscheidet](https://citizensforeurope.org/advocating_for_inclusion_page/) project of Citizens For Europe gUG.
