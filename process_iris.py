from datetime import datetime
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
import os
from datetime import timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from dbt_operator import DbtOperator
from python_scripts.train_model import process_iris_data
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator

ANALYTICS_DB = os.getenv('ANALYTICS_DB', 'analytics')
PROJECT_DIR = os.getenv('AIRFLOW_HOME') + "/dags/dbt/homework"
PROFILE = 'homework'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

env_vars = {
    'ANALYTICS_DB': ANALYTICS_DB,
    'DBT_PROFILE': PROFILE
}

dbt_vars = {
    'is_test': False,
    'data_date': '{{ ds }}',
}


with DAG(
        dag_id="process_iris",
        start_date=datetime(2025, 4, 22),
        # end_date=datetime(2025, 4, 24),
        schedule_interval="0 1 22-24 4 *",
        catchup=True,
) as dag:

    initial = DbtOperator(
        task_id='initial',
        dag=dag,
        command='seed',
        profile=PROFILE,
        project_dir=PROJECT_DIR,
        env_vars=env_vars,
        vars=dbt_vars
    )

    stg = DbtOperator(
        task_id='stg',
        dag=dag,
        command='run',
        profile=PROFILE,
        project_dir=PROJECT_DIR,
        models=['staging'],
        env_vars=env_vars,
        vars=dbt_vars,
    )

    mart = DbtOperator(
        task_id='mart',
        dag=dag,
        command='run',
        profile=PROFILE,
        project_dir=PROJECT_DIR,
        models=['mart'],
        env_vars=env_vars,
        vars=dbt_vars,
    )

    iris_data = PythonOperator(
        task_id='iris_data',
        dag=dag,
        python_callable=process_iris_data,
        provide_context=True,
    )

    send_email = EmailOperator(
        task_id='send_success_email',
        to='beavlina@meta.ua',
        subject='Iris pipeline completed',
        html_content='Пайплайн успешно выполнен!',
    )

    done = EmptyOperator(task_id="done")

    initial >> stg >> mart >> iris_data >> send_email >> done


