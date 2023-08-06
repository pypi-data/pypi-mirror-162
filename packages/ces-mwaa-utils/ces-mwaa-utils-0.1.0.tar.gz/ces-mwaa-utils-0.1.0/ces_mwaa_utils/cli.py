import argparse
import json
import logging
import os
from base64 import b64decode
from typing import Any, Union, Hashable, List, Dict

import boto3
import requests
import yaml


class Constants:
    DAG_DIRECTORY_EXCLUDE = ["helpers"]
    ENVIRONMENT_DIR = "environments"
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    LOG_FORMATS = {
        "detailed": "%(asctime)s::%(name)s::%(levelname)s - %(message)s",
        "skinny": "%(message)s",
    }
    MWAA_ENVIRONMENTS = {
        "stg": "data-intelligence-shared-stg",
        "prd": "data-intelligence-shared-prd",
    }


def get_logger(name: str, level: str = "info", log_format: str = "skinny"):
    """
    Create custom console logger
    :param name: logger name
    :param level: logging level
    :param log_format: format name to use. to choose between detailed and skinny logs.
    :return: new logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(Constants.LEVELS[level])
    formatter = logging.Formatter(Constants.LOG_FORMATS[log_format])
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger


def directory(string: str) -> str:
    """
    Check if the given path is a directory
    :param string: path name
    :return: the path if it is a directory else raise an error
    """
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def list_dags(dags_directory: str) -> List[str]:
    """
    List all the DAGs present in the given location
    :param dags_directory: the directory containing the DAGs
    :return: list of DAG names
    """
    dags = []
    for dag_name in os.listdir(dags_directory):
        abs_dir = os.path.join(dags_directory, dag_name)
        if os.path.isdir(abs_dir) and (dag_name not in Constants.DAG_DIRECTORY_EXCLUDE):
            dags.append(dag_name)
    return dags


def check_file_exists(file_path: str) -> bool:
    """
    Check if the given file exists on the file system
    :param file_path: path to the file
    :return: True if the file exists, else False
    """
    return os.path.exists(file_path)


def get_yaml_contents(file_path: str) -> Union[Dict[Hashable, Any], List, None]:
    """
    Get the contents of the YAML file
    :param file_path: path to the YAML file
    :return: Dictionary containing the items in the YAML file
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def combine_variables(dags_directory: str, dag_list: List[str], environment: str) -> Dict[str, Any]:
    """
    Combine the variables associated with the all dags
    :param dags_directory: Path to the directory containing the DAGs
    :param dag_list: List of DAG names found
    :param environment: The deployment environment name
    :return: Nested Dictionary with all the variables keyed by the DAG name
    """
    combined = {}
    for dag_name in dag_list:
        dag_dir = os.path.join(dags_directory, dag_name)
        variables_file = os.path.join(dag_dir, Constants.ENVIRONMENT_DIR, f"{environment}.yml")
        log.debug(f"Checking for variables file: {variables_file}")
        if check_file_exists(variables_file):
            variables = get_yaml_contents(variables_file)
            combined[dag_name] = variables
        else:
            log.warning(f"Found dag: {dag_name}, but no variables found!")
    return combined


def dump_variables(variables: Dict[str, Any], variables_file_name: str = "variables.json") -> None:
    """
    Dump the variables dictionary to the given path
    :param variables: The combined variables dictionary
    :param variables_file_name: The file name to write the variables json to
    :return:
    """
    current_working_directory = os.getcwd()
    output_file = os.path.join(current_working_directory, variables_file_name)

    log.info(f"Exported variables to file: {output_file}")
    with open(output_file, "w") as f:
        f.write(json.dumps(variables))


def get_mwaa_cli_token(mwaa_environment_name: str) -> Dict[str, Any]:
    """
    Get Token from AWS to interact with MWAA
    :param mwaa_environment_name: name of the MWAA environment
    :return: Token value
    """
    client = boto3.client('mwaa')

    mwaa_cli_token = client.create_cli_token(
        Name=mwaa_environment_name
    )
    return mwaa_cli_token


def execute_mwaa_cli_command(mwaa_cli_token: Dict[str, Any], mwaa_cli_command: str):
    """
    Execute the given MWAA CLI command
    :param mwaa_cli_token: Token for AWS MWAA
    :param mwaa_cli_command: Command to run
    :return:
    """
    mwaa_auth_token = 'Bearer ' + mwaa_cli_token['CliToken']
    mwaa_webserver_hostname = 'https://{0}/aws_mwaa/cli'.format(mwaa_cli_token['WebServerHostname'])

    mwaa_response = requests.post(
        mwaa_webserver_hostname,
        headers={
            'Authorization': mwaa_auth_token,
            'Content-Type': 'text/plain'
        },
        data=mwaa_cli_command
    )
    mwaa_status_code = mwaa_response.status_code
    mwaa_std_err_message = b64decode(mwaa_response.json()['stderr']).decode('utf8')
    mwaa_std_out_message = b64decode(mwaa_response.json()['stdout']).decode('utf8')

    if (mwaa_status_code != requests.codes.ok) or (mwaa_std_err_message != ""):
        log.debug(f"Stdout: {mwaa_std_out_message}")
        log.debug(f"Stderr: {mwaa_std_err_message}")
        log.debug(f"Could not execute command successfully, exiting: {mwaa_cli_command}")
        exit(1)
    else:
        log.debug(f"Command executed successfully: {mwaa_cli_command}")
        log.debug(f"Stdout: {mwaa_std_out_message}")


def run():
    file_directory = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(description="Gather airflow variables for the DAGs")
    parser.add_argument("-d", "--dags-directory", type=directory, help="path to directory containing the DAGs",
                        default=os.path.join(file_directory, "../dags"))
    parser.add_argument("-e", "--environment", type=str, help="the environment name for variables",
                        choices=["stg", "prd"], default="stg")
    parser.add_argument("-r", "--dry-run", help="Prepare deployment artifacts without deploying", action="store_true")
    parser.add_argument("-v", "--verbose", help="Use verbose logging", action="store_true")

    subparsers = parser.add_subparsers(dest="subcommand", help="subcommand help")
    gather_variables_subparser = subparsers.add_parser("gather-variables",
                                                       help="gather airflow variables into variables.json file")

    trigger_dag_subparser = subparsers.add_parser("trigger-dag", help="trigger given airflow dags")
    trigger_dag_subparser.add_argument("-n", "--dag-name", type=str, help="airflow DAG name",
                                       default="import_variables_hourly")

    args = parser.parse_args()

    dags_directory = args.dags_directory
    environment = args.environment
    mwaa_environment = Constants.MWAA_ENVIRONMENTS[environment]
    subcommand = args.subcommand

    global log
    if args.verbose:
        log = get_logger(__name__, "debug", "detailed")
    else:
        log = get_logger(__name__)

    log.info(f"Using DAGs directory: {dags_directory}")
    log.info(f"Using Environment name: {environment}")
    log.info(f"Using MWAA Environment: {mwaa_environment}")

    if subcommand is None:
        log.info("Nothing to do, exiting")
        exit(0)

    if subcommand == "gather-variables":
        dags_list = list_dags(dags_directory)
        log.info(f"The DAGs found are: {dags_list}")

        combined_variables = combine_variables(dags_directory, dags_list, environment)
        dump_variables(combined_variables)

    if subcommand == "trigger-dag":
        dag_name = args.dag_name
        mwaa_cli_command = f'trigger_dag {dag_name}'
        cli_token = get_mwaa_cli_token(mwaa_environment)
        execute_mwaa_cli_command(cli_token, mwaa_cli_command)
        log.info(f"Successfully triggered DAG: {dag_name}")

    log.info("FIN.")
