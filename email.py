from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from google.cloud import bigquery
import smtplib


default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 8),
        'email': ['airflow@airflow.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
      }

dag = DAG('email_dag', default_args=default_args)

sql = """
SELECT * FROM `patents-public-data.patents.publications` limit 20;"""

print_hello = BashOperator(task_id = "print_hello", 
bash_command = "echo Hello Sudharsan!", 
dag = dag)

def bigquery_email_list():
    print("Need to work on it")

def get_email_dict(**kwargs):
    email_dict = dict()
    x = [['task_1', 'sudharshanvas@gmail.com'], ['task_2', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com','sudharshanvas@gmail.com'],
    ['task_3', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com']]
    for i in x:
        email_dict[str(i[0])] = i[1:]
    return email_dict

def send_email(**kwargs):
    ti = kwargs['ti']
    password = "<app_password>"
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('sudharshangcp@gmail.com',password)
    email_dict = ti.xcom_pull(task_ids = "format_email")
    for i in email_dict.items():
        key = i[0]
        message = f"Hi Hope you are doing well \n"\
        f"This is a test email from {key}"
        vals = i[1]
        for mail in vals:
            s.sendmail('sudharshangcp@gmail.com',mail,message)



format_email = PythonOperator(task_id ="format_email",
python_callable = get_email_dict, 
provide_context = True, dag = dag)

send_email = PythonOperator(task_id ="send_email",
python_callable = send_email, 
provide_context = True, dag = dag)


        
print_hello >> format_email >> send_email