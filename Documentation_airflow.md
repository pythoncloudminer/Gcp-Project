# Apache Airflow DAG Documentation: Certificate Expiry Notification
This Apache Airflow DAG is designed, and implemented to automate the process of monitoring certificates' expiry within the latestCerts dataset, and to send notification to leaders when the certificates are about to expire in a week. The Airflow pipeline involves creating a temporary table by filtering the latestCerts data based on the certificate expiry and joing it with escalation data to access the email IDs of the leaders, and then the tasks are scheduled to send email notifications everyday to respective leaders based on certificate expiration and escalation.

# DAG STRUCTURE
1.	FilterTask:

- Task Type: BigQuery Operator
- Description: Filters data from the latestCerts dataset based on certificates about to expire within a week, joins the result with the escalation table and creates a temporary table for further processing.
2.ProcessDagTask:
- Task Type: Python Operator
- Description: Uses the "process_dag" Python function to read data from the temporary table created in the FilterTask. Processes the data to generate a dictionary containing certificate and email information.
3.EmailTask:
- Task Type: Email Operator
- Description: Sends email notifications to respective leaders based on certificate expiration and escalation. The email content is dynamically generated using the processed data.
Task Dependencies:
•	FilterTask is set as the first task in the DAG.
•	ProcessDagTask depends on the successful completion of FilterTask.
•	EmailTask depends on the successful completion of ProcessDagTask.

# Task Implementation:
1.	FilterTask Implementation:
- BigQuery - SQL query filters data from the latestCerts dataset based on certificates about to expire within a week.
- Joins the results with escalation table.
- Creates a temporary table for subsequent processing.
2.	ProcessDagTask Implementation:
- Python function (process_dag) reads data from the temporary table created in FilterTask.
- Processes the data to create a dictionary with certificate and email information.
3.	EmailTask Implementation:
- Uses an Email Operator to send notifications.
- Dynamically generates the email content based on the processed data.

# Execution:
- The DAG runs on a daily schedule (schedule_interval='@daily').
- The FilterTask executes first, filtering data and creating a temporary table.
- ProcessDagTask executes, processing data and generating the required dictionary.
- Finally, EmailTask executes, sending notifications to respective leaders based on certificate expiration and escalation.


