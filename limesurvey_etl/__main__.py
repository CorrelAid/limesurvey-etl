import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv

from limesurvey_etl.etl_pipeline import Pipeline

load_dotenv()
logging.getLogger(__name__).setLevel(logging.INFO)


parser = argparse.ArgumentParser(
    description="Run a Limesurvey ETL pipeline or a single pipeline step based on a yaml configuration file."
)
parser.add_argument(
    "-c",
    "--config_file",
    metavar="--config-file",
    help="Path to the yaml configuration file for the Limesurvey ETL pipeline.",
)
parser.add_argument(
    "-s",
    "--step",
    help="Pipeline step(s) to be executed.",
    choices=["extract", "transform", "load", "all"],
)


def cli(pipeline_step: str, config_file: Path) -> None:
    pipeline = Pipeline.get_pipeline(config_file)

    try:
        if pipeline_step == "extract":
            logging.info("Executing extract step.")
            pipeline.run_extract()
            logging.info("Finished executing extract step.")

        elif pipeline_step == "transform":
            logging.info("Executing transform step.")
            pipeline.run_transform()
            logging.info("Finished executing transform step.")

        elif pipeline_step == "load":
            logging.info("Executing load step.")
            pipeline.run_load()
            logging.info("Finished executing load step.")

        elif pipeline_step == "all":
            logging.info("Start running pipeline.")
            pipeline.run_all()
            logging.info("Finished running pipeline.")
    except Exception as e:
        logging.critical("An uncaught exception occured!", exc_info=e)
        raise


if __name__ == "__main__":
    args = parser.parse_args()
    pipeline_step = args.step
    config_file = Path(args.config_file)
    cli(pipeline_step=pipeline_step, config_file=config_file)
