from utils import connect_to_mariadb


def get_answers(config):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )

    # execute transformation
    sql_stmt = """
        CREATE TABLE reporting.answers AS SELECT * FROM raw.lime_survey_916481
    """ # needs refactoring to be more consistent with the current structure
    # why did I do it like this? Bc there are too many tables that would otherwise
    # need specific configurations when calling utils.create_table_if_not_exists
    with engine.connect() as con:
        if not engine.dialect.has_table(
                con,
                table_name="answers",
                schema="reporting"
                ):

            con.execute(sql_stmt)

