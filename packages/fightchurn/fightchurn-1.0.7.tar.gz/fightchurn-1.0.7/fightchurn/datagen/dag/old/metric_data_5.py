from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

dag_args = {
    'owner': 'carl.gold',
    'depends_on_past': False,
    'start_date': datetime(2020, 5, 31),
    'end_date': datetime(2020, 6, 1),
    'email': ['carl.steven.gold@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 0,
    'retry_delay': timedelta(minutes=3)}

dag = DAG(
    dag_id='metric_data_test_5',
    start_date=datetime(2020, 5, 31),
    end_date=datetime(2020, 6, 1),
    default_args=dag_args,
    schedule_interval='0 9 * * *')

t1 = BigQueryCheckOperator(task_id='check_event_data_exists',
                           sql="""
                            select count(*) > 0
                            from `fight-churn-with-gcp.churn_1.event`
                            where DATE(event_time) = '2020-05-31'
                        """,
                           use_legacy_sql=False)

t2 = BigQueryOperator(
    task_id='calculate_metric',
    use_legacy_sql=False,
    create_disposition='CREATE_IF_NEEDED',
    write_disposition='WRITE_TRUNCATE',
    allow_large_results=True,
    bigquery_conn_id='bigquery_default',
    time_partitioning={
        "type": 'DAY'
        },
    sql='''
    #standardSQL
        select date('2020-05-31') as date, account_id,  'n_like' as metric, count(*) as value
        from `fight-churn-with-gcp.churn_1.event` e 
        inner join `fight-churn-with-gcp.churn_1.event_type` t on t.event_type_id=e.event_type_id
        where t.event_type_name='like'
          e.event_time <= '2020-05-31'
          and DATE_DIFF('2020-05-31', e.event_time , DAY) < 28
        group by account_id
    ''',
    destination_dataset_table='fight-churn-with-gcp.churn_1.metric_test',
    dag=dag)

t1 >> t2