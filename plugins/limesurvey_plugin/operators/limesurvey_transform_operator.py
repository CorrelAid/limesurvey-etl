import pandas as pd
import yaml
from airflow.models.baseoperator import BaseOperator
from sqlalchemy import VARCHAR, Integer

from include.utils import (
    connect_to_mariadb,
    create_table_if_not_exists,
    insert_on_duplicate,
    log_missing_values,
)


class LimesurveyTransformOperator(BaseOperator):
    """
    Operator that applies transform operations to a limesurvey table.
    """

    def __init__(self, config_path, table_name, connection_config, *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        with open(config_path, "r") as config_yaml:
            config = yaml.safe_load(config_yaml)
        self.config = config[table_name]
        self.connection_config = connection_config
        self.table_name = table_name

    def execute(self, context):
        print(self.config)
        engine = connect_to_mariadb(
            db_host=self.connection_config["COOLIFY_MARIADB_HOST"],
            db_port=self.connection_config["COOLIFY_MARIADB_PORT"],
            db_user=self.connection_config["COOLIFY_MARIADB_USER"],
            db_password=self.connection_config["COOLIFY_MARIADB_PASSWORD"],
            db_name=self.connection_config["COOLIFY_MARIADB_DATABASE"],
        )

        # create table in reporting layer if not exists
        columns = self.config["columns"]
        for colname in columns.keys():
            columns[colname]["type"] = eval(columns[colname]["type"])
        create_table_if_not_exists(
            engine=engine,
            table_name=self.config["reporting_table_name"],
            columns=self.config["columns"],
            schema="reporting",
        )

        # transform data
        df = pd.read_sql(self.config["sql_stmt"], con=engine)

        if "mapping_path" in self.config.keys():
            mapping_df = pd.read_csv(self.config["mapping_path"], delimiter=",")
            df = df.merge(
                mapping_df,
                on=self.config["mapping_join_on"],
                how="left",
                suffixes=("", "_y"),
            )

        if "empty_columns_to_add" in self.config.keys():
            for col in self.config["empty_columns_to_add"]:
                df[col] = pd.Series(dtype="str")

        target_cols = self.config["target_cols"]
        df = df[target_cols]

        log_missing_values(
            df,
            source_col=self.config["mapping_join_on"],
            target_cols=[
                col for col in target_cols if not col == self.config["mapping_join_on"]
            ],
            log_file_name=self.config["mapping_log_file_name"],
        )

        # fill nans in primary key cols
        for col_name, col in {
            k: v for k, v in self.config["columns"].items() if v.get("primary_key")
        }.items():
            if col["type"] == Integer:
                df[col_name] = df[col_name].fillna(-999)
            else:
                df[col_name] = df[col_name].fillna(99)

        # write df to target reporting table
        df.to_sql(
            name=self.config["reporting_table_name"],
            con=engine,
            schema="reporting",
            if_exists="append",
            index=False,
            method=insert_on_duplicate,
        )
