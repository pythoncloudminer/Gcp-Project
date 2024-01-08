from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from google.cloud import bigquery
import smtplib
from email.message import EmailMessage


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
    ti = kwargs['ti']
    email_dict = dict()
    x = [['task_1', 'sudharshanvas@gmail.com'], ['task_2', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com','sudharshanvas@gmail.com'],
    ['task_3', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com', 'sudharshanvas@gmail.com']]
    for i in x:
        email_dict[str(i[0])] = i[1:]
    ti.xcom_push("email", email_dict)
    return email_dict

def send_email(**kwargs):
    email = EmailMessage()
    email["From"] = "sudharshangcp@gmail.com"
    #email["To"] = recipient
    email["Subject"] = "Certificate Expiry Notification"
    #email.set_content(message, subtype="html")

    ti = kwargs['ti']
    password = "upzkqbwxnmwfcptw "
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('sudharshangcp@gmail.com',password)
    email_dict = ti.xcom_pull(task_ids = "format_email")
    for i in email_dict.items():
        key = i[0]
        message = f"""<h1> Your Certificate is about to Expire in seven days! </h1>
        <p>Hi Hope you are doing <b>well</b><p> \n
        "This is a test email from {key} to notify the expiry of your certificate"""
        vals = i[1]
        for mail in vals:
            email.set_content(message, subtype="html")
            email["To"] = mail
            s.sendmail('sudharshangcp@gmail.com',mail,email.as_string())
            del email["To"]



format_email = PythonOperator(task_id ="format_email",
python_callable = get_email_dict, 
provide_context = True, dag = dag)

send_email = PythonOperator(task_id ="send_email",
python_callable = send_email, 
provide_context = True, dag = dag)


        
print_hello >> format_email >> send_email
