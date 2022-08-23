import json
import boto3
import os
import time


# Converting Redshift Data API output to JSON
# Expected:
# {
#   "status": "ok",
#   "description": "load active"
# }
def post_process(meta, records):
    columns = [k["name"] for k in meta]
    rows = []
    for r in records:
        tmp = []
        for c in r:
            tmp.append(c[list(c.keys())[0]])
        rows.append(tmp)
    print(columns)
    
    return_value = {columns[0]: rows[0][0], columns[1]: rows[0][1]}
    
    return return_value

def query(sql, v_cluster_identifier, v_secret_arn, v_database_name):
    
    rsd = boto3.client('redshift-data')
    
    resp = rsd.execute_statement(
        Database=v_database_name,
        ClusterIdentifier=v_cluster_identifier,
        SecretArn=v_secret_arn,
        Sql=sql
    )
    qid = resp["Id"]
    print("query ID:", qid)
    desc = None
    
    while True:
        desc = rsd.describe_statement(Id=qid)
        if desc["Status"] == "FINISHED":
            break
            print(desc["ResultRows"])
            
    if desc and desc["ResultRows"]  > 0:
        result = rsd.get_statement_result(Id=qid)
        rows, meta = result["Records"], result["ColumnMetadata"]
        return post_process(meta, rows)


def lambda_handler(event, context):
    
    
    
    load_type = event['load_type']
    load_frequency = event['load_frequency']
    
    v_secret_arn = os.environ.get('secret_arn')
    v_cluster_identifier = os.environ.get('cluster_identifier')
    v_database_name = os.environ.get('database_name')
    v_schema_name = os.environ.get('rs_schema')
    
    sql_statement = "select case when active_flag = 'Y' then 'ok' else 'abort' end as status, case when active_flag = 'Y' then 'load active' else 'load deactivated' end as description from %s.etlfw_load_tp_master where load_tp = '%s' and load_frequency = '%s'" % (v_schema_name, load_type, load_frequency)
    
    pf=query(sql_statement, v_cluster_identifier, v_secret_arn, v_database_name)
    print(pf)

    
    return pf

