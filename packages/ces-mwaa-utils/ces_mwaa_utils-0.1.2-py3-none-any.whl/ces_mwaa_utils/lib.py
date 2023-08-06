from datetime import datetime, timedelta
from typing import Dict, Any

from airflow.models import Variable
from airflow.hooks.base_hook import BaseHook
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator


def get_default_args() -> Dict[str, Any]:
    """
    Get default arguments for Airflow DAGs, These are common values across DAGs.
    :return: Default arguments dictionary
    """
    return {
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
        "catchup": False,
    }


def get_variable_json(dag_name: str) -> Any:
    """
    Get the Airflow variable for the given DAG name with JSON deserialization
    :param dag_name: Name of the Airflow DAG
    :return: Airflow DAG variable dictionary
    """
    return Variable.get(dag_name, deserialize_json=True)


def get_common_variable_json(variable_name: str = "common") -> Any:
    """
    Get the airflow common variables to be used across DAGs
    :return: Airflow common variable dictionary
    """
    return Variable.get(variable_name, deserialize_json=True)


def get_start_date(dag_name: str) -> datetime:
    """
    Get the start date for the given DAG
    :param dag_name: Name of the Airflow DAG
    :return: Start date datetime object
    """
    start_date_str = get_variable_json(dag_name)["start_date"]
    return datetime.strptime(start_date_str, "%Y-%m-%d")


def get_resources_path(dag_name: str, resource_name: str) -> str:
    """
    Generate the AWS filesystem path for the given resource
    :param dag_name: Name of the DAG the resource belongs to
    :param resource_name: Name of the resource
    :return: AWS MWAA fileystem path
    """
    return "/usr/local/airflow/dags/{}/resources/{}".format(dag_name, resource_name)


def get_file_contents(file_path: str) -> str:
    """
    Read the contents of the given file path
    :param file_path: Path to the file
    :return: Contents of the file
    """
    with open(file_path, "r") as file:
        contents = file.read()
        return contents


def get_resource_contents(dag_name: str, resource_name: str) -> str:
    """
    Read the contents of the given resource by finding the filesystem path
    :param dag_name: Name of the DAG the resource belongs to
    :param resource_name: Name of the resource
    :return: Contents of the resource
    """
    file_path = get_resources_path(dag_name, resource_name)
    return get_file_contents(file_path)


def get_common_resource_contents(resource_name: str) -> str:
    """
    Get the contents of the given "common" resource. Common resources don't belong
    to a particular file and is shared/common across all the DAGs
    :param resource_name: Name of the resource
    :return: Contents of the resource
    """
    file_path = "/usr/local/airflow/dags/common/{}".format(resource_name)
    return get_file_contents(file_path)


def push_slack_notification(context):
    """
    Push Slack notification based on the Airflow context. Used for notifying
    users of failures to Airflow tasks.
    :param context: Airflow Context
    :return: Execute task and return status
    """
    slack_webhook_token = BaseHook.get_connection("slack").password
    slack_msg_blockkit = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":failed: Task Failed",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "plain_text",
                    "text": "DAG: {}".format(context.get("task_instance").dag_id)
                },
                {
                    "type": "plain_text",
                    "text": "Task: {}".format(context.get("task_instance").task_id)
                },
                {
                    "type": "plain_text",
                    "text": "Operator: {}".format(context.get("task_instance").operator)
                },
                {
                    "type": "plain_text",
                    "text": "Execution Time: {}".format(context.get("task_instance").execution_date)
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "View task logs on Airflow"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Click Me",
                    "emoji": True
                },
                "value": "click_me",
                "url": "{}".format(context.get("task_instance").log_url),
                "action_id": "button-action"
            }
        }
    ]
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        blocks=slack_msg_blockkit,
        username='airflow')
    return failed_alert.execute(context=context)
