# ETL Configs How To
Limesurvey ETL pipeline configurations can consist of a variety of extractors, transformers, and loaders. The following documentation provides a detailed description of how to configure them.

## How to write custom ETL configuration yaml-files
The ETL configuration `-yaml`-file must define three main steps which are explained in detail in the below sections: extract, transform, and load. The basic structure of the yaml-file should look as follows:

```yaml
extract:
    <EXTRACT TYPE CONFIGURATION>

transformation_pipelines:
    - <TRANSFORMATION_PIPELINE_1>
    - <TRANSFORMATION_PIPELINE_2>
    ...
    - <TRANSFORMATION_PIPELINE_3>

load:
    <LOAD TYPE CONFIGURATION>
```

## Step 1: Define the extract step
The extract step defines what data is extracted from limesurvey. Currently, this project only supports extracting data from the Limesurvey DB. Support for the Limesurvey API might be added in the future. Add an extract step of type `limesurvey_extract` (see [example](etl-config-how-to.md#example)) uder the `extract` field of your configuration file:

::: limesurvey_etl.config.extract_config.limesurvey.LimesurveyExtractConfig

##### Example
```yaml
extract_type: limesurvey_extract
  tables:
    - lime_questions
```

## Step 2: Define the transform steps
Transform steps define what sequence of transformations will be applied to the extracted data. You can chain multiple transformation pipelines in one ETL pipeline so that multiple tables will be created in the `staging` schema of your target database.

You can define a transformation pipeline by configuring the following parameters:

::: limesurvey_etl.config.transform_config.transformation_pipeline.TransformationPipelineConfig
####

The `columns`, `data`, and `transform_steps` fields require additional configurations as described below:

::: limesurvey_etl.config.transform_config.transformation_pipeline.Column

::: limesurvey_etl.config.transform_config.select_source_data.SelectSourceDataConfig

::: limesurvey_etl.config.transform_config.select_source_data.SourceTable

::: limesurvey_etl.config.transform_config.select_source_data.Join

##### Example
```yaml
- table_name: subquestions
  staging_schema: staging
  columns:
    - name: subquestion_id
      type: INTEGER
      primary_key: True
      nullable: False
    - name: question_item_id
      type: INTEGER
      nullable: False
      foreign_key: staging.question_items.question_item_id
    - name: subquestion_item_title
      type: VARCHAR(50)
    - name: question_item_title
      type: VARCHAR(50)
  source_data:
    source_tables:
      - table_name: lime_questions
        columns:
          - qid AS subquestion_id
          - title AS subquestion_item_title
      - table_name: lime_questions
        columns:
          - qid AS question_item_id
          - title AS question_item_title
    source_schema: raw
    join:
      type: JOIN
      left_table: lime_questions
      right_table: lime_questions
      left_on: parent_qid
      right_on: qid
    filter: "WHERE left_table.parent_qid != 0"
  transform_steps:
    - transform_type: add_computed_column
      column_name: subquestion_item_title
      input_columns:
        - question_item_title
        - subquestion_item_title
      operator:
        name: concat
        separator: "_"
```
## Full list of transform steps

The `transform_steps` field is a list of transformations that should be applied to the data. There are a number of different transform steps available as documented below.

- `add_columns`
- `melt_data`
- `add_computed_column`
- `fill_null_values`
- `filter_data`
- `join_with_csv_mapping`
- `rename_columns`
- `replace_values`

Note: transformations are applied in order.

::: limesurvey_etl.config.transform_config.add_columns.AddColumnsConfig

##### Example
```yaml
- transform_type: add_columns
  column_names:
    - added_column_1
    - added_column_2
  default_value: 1000
```

::: limesurvey_etl.config.transform_config.melt_data.MeltDataConfig

##### Example
```yaml
- trransform_type: melt_data
  id_vars:
    - id
  value_vars:
    - type
```

::: limesurvey_etl.config.transform_config.add_computed_column.AddComputedColumnConfig

The `add_computed_columns` configuration requires to define an operation in the `operator` field. The following operators are available:

::: limesurvey_etl.config.transform_config.add_computed_column.SumOperator

::: limesurvey_etl.config.transform_config.add_computed_column.ProductOperator

::: limesurvey_etl.config.transform_config.add_computed_column.DifferenceOperator

::: limesurvey_etl.config.transform_config.add_computed_column.ConcatOperator

::: limesurvey_etl.config.transform_config.add_computed_column.SplitOperator

::: limesurvey_etl.config.transform_config.add_computed_column.ExtractOperator

##### Example
```yaml
- transform_type: add_computed_column
  column_name: subquestion_item_title
  input_columns:
    - question_item_title
    - subquestion_item_title
  operator:
    name: concat
    separator: "_"
```

::: limesurvey_etl.config.transform_config.fill_null_values.FillNullValuesConfig

##### Example
```yaml
- transform_type: fill_null_values
  column_name: lang
  value: "99"
```

::: limesurvey_etl.config.transform_config.filter_data.FilterDataConfig

The `filter_data` transform step requires you to set one or multiple filter `conditions` as follows:

::: limesurvey_etl.config.transform_config.filter_data.FilterCondition


##### Example
```yaml
- transform_type: filter_data
  conditions:
    - column: "age"
      value: "30"
      operator: ">="
    - column: "gender"
      value: "female"
      operator: "=="
  logical_operator: AND
```

You can also use the `filter_data` transform step multiple times to perform more sophisticated filter operations.

::: limesurvey_etl.config.transform_config.join_with_csv_mapping.JoinWithCSVMappingConfig

##### Example
```yaml
- transform_type: join_with_csv_mapping
  mapping_path: "/opt/airflow/include/mappings/mapping_question_items.csv"
  mapping_delimiter: ","
  keep_columns:
    - label_major
    - label_minor
  left_on: question_item_title
  right_on: question_item_id
  how: left
```

::: limesurvey_etl.config.transform_config.rename_columns.RenameColumnsConfig

##### Example
```yaml
- transform_type: rename_columns
  colname_to_colname:
    "Fragetyp Major (CFE)": type_major
```

::: limesurvey_etl.config.transform_config.replace_values.ReplaceValuesConfig

##### Example
```yaml
- transform_type: replace_values
  column_name: age
  replacement_values:
    999: 30
    "Unknown": "Other"
```

## Step 3: Define the Load Step
The load step defines how the data from the `staging` schema is loaded to the `reporting` schema of your target database.

::: limesurvey_etl.config.load_config.reporting_db.ReportingDBLoadConfig

##### Example
```yaml
load:
  load_type: reporting_db_load
  staging_schema: staging
  target_schema: reporting
  tables:
    - question_groups
    - question_items
    - subquestions
```

## Example of an ETL configuration file
For a more complicated example, check out `airflow/dags/configs/cfe_limesurvey.yaml` in the repository.

```yaml
extract:
  extract_type: limesurvey_extract
  tables:
    - lime_questions

transformation_pipelines:
  - table_name: question_items
    staging_schema: staging
    columns:
      - name: question_item_id
        type: INTEGER
        primary_key: True
        nullable: False
      - name: question_item_title
        type: VARCHAR(255)
        nullable: True
      - name: question_group_id
        type: INTEGER
        nullable: False
        foreign_key: "staging.question_groups.question_group_id"
      - name: type_major
        type: VARCHAR(255)
        nullable: True
      - name: type_minor
        type: VARCHAR(255)
        nullable: True
    source_data:
      source_tables:
        - table_name: lime_questions
          columns:
            - qid AS question_item_id
            - title AS question_item_title
            - gid AS question_group_id
            - type AS type_major
            - type AS type_minor
      source_schema: raw
    transform_steps:
      - transform_type: join_with_csv_mapping
        mapping_path: /opt/airflow/include/mappings/Mapping_LS-QuestionTypesMajor.csv
        mapping_delimiter: ;
        keep_columns:
          - "Fragetyp Major (CFE)"
        left_on: type_major
        right_on: "Fragetyp-ID (LS)"
        how: left
      - transform_type: rename_columns
        colname_to_colname: "Fragetyp Major (CFE)": type_major

load:
  load_type: reporting_db_load
  staging_schema: staging
  target_schema: reporting
  tables:
      - question_items
```
