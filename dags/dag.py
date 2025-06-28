from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'dag',
    default_args=default_args,
    description='data pipeline run once a month',
    schedule_interval='0 0 1 * *',  # At 00:00 on day-of-month 1
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 6, 1),
    catchup=True,
) as dag:

    # MODEL TRAINING
    model_training_start = DummyOperator(task_id="model_training_start")
    
    model_train = BashOperator(
        task_id='model_train',
        bash_command=(
            'cd /opt/airflow/scripts && '
            'python3 model_train.py '
            '--snapshotdate "{{ ds }}"'
        ),
    )
    
    # model_2_training = DummyOperator(task_id="model_2_training")

    model_training_completed = DummyOperator(task_id="model_training_completed")
    
    # Define task dependencies to run scripts sequentially
    # feature_store_completed >> model_training_start
    # label_store_completed >> model_training_start
    model_training_start >> model_train >> model_training_completed


    # MODEL INFERENCE -> MODEL MONITORING
    
    # --- model inference ---
    model_inference_start = DummyOperator(task_id="model_inference_start")

    model_1_inference = BashOperator(
        task_id='model_1_inference',
        bash_command=(
            'cd /opt/airflow/scripts && '
            'python3 model_inference.py '
            '--snapshotdate "{{ ds }}" '
            '--modelname "credit_model_2024_06_01.pkl"'
        ),
    )


    # model_2_inference = DummyOperator(task_id="model_2_inference")

    model_inference_completed = DummyOperator(task_id="model_inference_completed")


    model_monitor_start = DummyOperator(task_id="model_monitor_start")

    model_1_monitor = BashOperator(
        task_id='model_1_monitor',
        bash_command=(
            'cd /opt/airflow/scripts && '
            'python3 model_monitor.py '
            '--snapshotdate "{{ ds }}" '
            '--modelname "credit_model_2024_06_01.pkl"'
        ),
    )
    
    # model_2_monitor = DummyOperator(task_id="model_2_monitor")

    model_monitor_completed = DummyOperator(task_id="model_monitor_completed")
    

    model_training_completed >> model_inference_start >> model_1_inference >> model_inference_completed >> model_monitor_start >> model_1_monitor >> model_monitor_completed