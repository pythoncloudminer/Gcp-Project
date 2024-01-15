Apache Airflow DAG Documentation: Certificate Expiry Notification
This Apache Airflow DAG is designed, and implemented to automate the process of monitoring certificates' expiry within the latestCerts dataset, and to send notification to leaders when the certificates are about to expire in a week. The Airflow pipeline involves creating a temporary table by filtering the latestCerts data based on the certificate expiry and joing it with escalation data to access the email IDs of the leaders, and then the tasks are scheduled to send email notifications everyday to respective leaders based on certificate expiration and escalation.

DAG STRUCTURE
1.	FilterTask:
o	Task Type: BigQuery Operator
o	Description: Filters data from the latestCerts dataset based on certificates about to expire within a week, joins the result with the escalation table and creates a temporary table for further processing.
2.	ProcessDagTask:
o	Task Type: Python Operator
o	Description: Uses the "process_dag" Python function to read data from the temporary table created in the FilterTask. Processes the data to generate a dictionary containing certificate and email information.
3.	EmailTask:
o	Task Type: Email Operator
o	Description: Sends email notifications to respective leaders based on certificate expiration and escalation. The email content is dynamically generated using the processed data.
Task Dependencies:
•	FilterTask is set as the first task in the DAG.
•	ProcessDagTask depends on the successful completion of FilterTask.
•	EmailTask depends on the successful completion of ProcessDagTask.






Task Implementation:
1.	FilterTask Implementation:
o	BigQuery - SQL query filters data from the latestCerts dataset based on certificates about to expire within a week.
o	Joins the results with escalation table.
o	Creates a temporary table for subsequent processing.
2.	ProcessDagTask Implementation:
o	Python function (process_dag) reads data from the temporary table created in FilterTask.
o	Processes the data to create a dictionary with certificate and email information.
3.	EmailTask Implementation:
o	Uses an Email Operator to send notifications.
o	Dynamically generates the email content based on the processed data.

Execution:
1.	The DAG runs on a daily schedule (schedule_interval='@daily').
2.	The FilterTask executes first, filtering data and creating a temporary table.
3.	ProcessDagTask executes, processing data and generating the required dictionary.
4.	Finally, EmailTask executes, sending notifications to respective leaders based on certificate expiration and escalation.


