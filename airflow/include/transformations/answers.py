from utils import connect_to_mariadb
import pandas as pd


def get_answers(config):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )

    # reformat the question titles
    with engine.connect() as con:
        question_names = pd.read_sql(sql="SELECT qid, parent_qid, title FROM raw.lime_questions", con=con)
        df = pd.read_sql(sql="SELECT * FROM raw.lime_survey_916481", con=con) 
        df.drop(["token", "submitdate", "lastpage", "startlanguage", "seed"], axis=1, inplace=True)
        columns = df.columns
        col_qids = (columns.str.extract("^.*(?<=X)(\d+)")[0]
                    .fillna(0)
                    .astype("int64"))
        merged = pd.merge(col_qids.rename("qid"), question_names, on="qid", how="left").drop_duplicates("qid")
        columns_formatted = (columns.str.extract("^.*(?<=X)(\d+)(SQ\d\d\d)?(comment|other)?"))
        columns_formatted[0] = (columns_formatted[0][columns_formatted[0].notna()]
                             .apply(lambda x: merged.loc[merged.qid == int(x), "title"].values[0]))
        columns_formatted[1] = columns_formatted[1].iloc[1:].fillna("SQ001") 
        columns_formatted[2] = columns_formatted[columns_formatted[2].notna()][2].str[0]
        columns_formatted = columns_formatted.fillna("")
        columns_formatted = list(columns_formatted[0].str.cat(columns_formatted[2], sep="").iloc[1:].str.cat(columns_formatted[1], sep="_"))
        columns_formatted.insert(0, "respondent_id")
        df.columns = columns_formatted
        df.to_sql(
                name="question_responses",
                con=con,
                schema="reporting",
                if_exists="replace",
                index=False
                ) 

