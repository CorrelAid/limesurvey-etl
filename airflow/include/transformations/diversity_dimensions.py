import pandas as pd

from utils import connect_to_mariadb, insert_on_duplicate, \
    create_table_if_not_exists

### TO DO: load actual data, this is only a placeholder
def get_diversity_items(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )

    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine,
        table_name="diversity_items",
        columns=columns,
        schema="reporting"
    )

    #### TO DO: load the actual data

    sql_stmt = None # TO DO

    