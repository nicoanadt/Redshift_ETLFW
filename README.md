# Redshift_ETLFW
ETL framework for Amazon Redshift using its Federated Query feature

## Deployment Steps
Please follow the below steps to deploy the framework

### 1. Deploy DDLs Redshift Control Tables
Login to your Redshift database and Execute https://github.com/nicoanadt/Redshift_ETLFW/blob/main/redshift/control_tables.sql.
Replace $$schema with the appropriate schema.
Read the instructions in the scripts to replace the insert statements.

* Make sure you have an entry for each source table that you want to be extracted in the $$schema.etlfw_load_details table. This is a one time activity

### 2. Deploy DDLs Redshift Log Tables
* DDL:- Login to your Redshift database and Execute https://github.com/nicoanadt/Redshift_ETLFW/blob/main/redshift/log_tables.sql. Replace $$schema with the schema of appropriate schema. Read the instructions in the scripts to replace the insert statements.
* Make sure you have an entry for each source table and the last modified timestamp from the source table in the $$schema.etlfw_load_businessdate table. This is a one time activity. Going forward the jobs will keep updated the table with the latest modified timestamp.
* Stored Procedure:- Login to your Redshift database and Execute https://github.com/nicoanadt/Redshift_ETLFW/blob/main/redshift/sp_sync_merge.sql. Replace $$schema with the appropriate schema.

### 3. Store PG and Redshift secrets in Secret Manager.

### 4. Deploy Lambda functions
Deploy the 2 lambda functions.

1. etlfw_rs_check_load_active_status - https://github.com/nicoanadt/Redshift_ETLFW/tree/main/lambda/etlfw_rs_check_load_active_status. Use the .py file in lambda function. Please ensure the following configurations are added.

* Runtime settings -> Runtine - Python 3.8, Handler - lambda_function.lambda_handler, 
* Associate an IAM role that access to the secrets (steps 3) in Secret Manager and access to Redshift Data API
* Under configurations set the following environment variable
            Key | Value
  ------------- | -------------
     rs_schema  | schema where step 1 DDLs were deployed
   secret_arn  | Secret Manager ARN for Redshift DB
   cluster_identifer | Cluster identifer name of the Redshift cluster
   database_name | Database name of the Redshift cluster

2. etlfw_rs_fetch_active_tables - https://github.com/nicoanadt/Redshift_ETLFW/blob/main/lambda/etlfw_rs_fetch_active_tables/lambda_function.py. Use the .py file in lambda function. Please ensure the following configurations are added.

* Runtime settings -> Runtine - Python 3.8, Handler - lambda_function.lambda_handler, 
* Associate an IAM role that access to the secrets (steps 3) and access to Redshift Data API.
* Under configurations set the following environment variable
            Key | Value
  ------------- | -------------
     rs_schema  | schema where step 1 DDLs were deployed
   secret_arn  | Secret Manager ARN for Redshift DB
   cluster_identifer | Cluster identifer name of the Redshift cluster
   database_name | Database name of the Redshift cluster


### 4. Deploy Step functions and cloudwatch events to trigger the Step function
1. Create an IAM role for Step Function. Associate the inline policy https://github.com/nicoanadt/Redshift_ETLFW/blob/main/step_functions/step_function_lambda_redshift-IAMPolicy.json. Replace the account no and aws region with appropriate values.

2. Create a step function with the definition https://github.com/nicoanadt/Redshift_ETLFW/blob/main/step_functions/etlfw_stepfunction.json. Associate the IAM role you created in the previous step.

3. Go to Cloudwatch events and Create a rule, with the following configurations.
* Click on Schedule - Fixed rate of <put appropriate intervals> minutes.
* For Target choose Step function state machines - Choose the step function you just deployed.
* For Configure input, choose Constant (JSON text) and insert the json text 
```
{ "load_type": "incremental",   "load_frequency": "short_batch" }
```
* Choose create a new role for this specific resource.
* If you want to create a pipeline for full load pipeline create a new cloudwatch event rule with appropriate input JSON text.

            
  
## Done, you are good to go
  
    

