from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup

import custom_functions



default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1)
}



with DAG(dag_id="fraud_detection", default_args=default_args, schedule_interval=timedelta(seconds=120.0), catchup=False) as dag:
    start_dag = DummyOperator(task_id="start_dag")

    with TaskGroup(group_id="API_ETL") as api_ETL:
        extract_api_data = BashOperator(task_id="extract_api_data", bash_command='''
                                    cd ../../opt/airflow/data/json
                                    curl -o api_reply0.json https://sdacelo-real-time-fraud-detection.hf.space/current-transactions
                                    curl -o api_reply1.json https://sdacelo-real-time-fraud-detection.hf.space/current-transactions
                                    curl -o api_reply2.json https://sdacelo-real-time-fraud-detection.hf.space/current-transactions
                                    pwd
                                    ls
                                    ''')
                                
        transform_api_data = PythonOperator(
            task_id="transform_api_data",
            python_callable=custom_functions.process_api_data
        )

        load_api_data = PythonOperator(
            task_id="load_api_data",
            python_callable=custom_functions.write_api_data
        )

        [extract_api_data >> transform_api_data >> load_api_data]
    

    with TaskGroup(group_id="predict") as api_predict:
        import_neondata = PythonOperator(
            task_id="import_neondata",
            python_callable=custom_functions.pull_neon_data
        )

        transform_neondata = PythonOperator(
            task_id="transform_neondata",
            python_callable=custom_functions.transform_neondata
        )

        consume_neondata = PythonOperator(
            task_id="consume_neondata",
            python_callable=custom_functions.consume_neondata
        )

        check_predict = PythonOperator(
            task_id="check_predict",
            python_callable=custom_functions.flag_checker
        )

        [import_neondata >> transform_neondata >> consume_neondata >> check_predict]
    
    end_dag = DummyOperator(task_id="end_dag")

    start_dag >> api_ETL >> api_predict >> end_dag



with DAG(dag_id="daily_report", default_args=default_args, schedule_interval="@daily", catchup=False) as dag2:
    start_dag = DummyOperator(task_id="start_dag")

    with TaskGroup(group_id="report") as generate_report:
        produce_report = PythonOperator(
            task_id="produce_report",
            python_callable=custom_functions.produce_report
        )

        send_report = PythonOperator(
            task_id="send_report",
            python_callable=custom_functions.send_report
        )

        [produce_report >> send_report]

    end_dag = DummyOperator(task_id="end_dag")

    start_dag >> generate_report >> end_dag