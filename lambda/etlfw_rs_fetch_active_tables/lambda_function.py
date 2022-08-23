import json
import boto3
import os
import time

# Converting Redshift Data API output to JSON
def post_process(meta, records):

    columns = [k["name"] for k in meta]
    rows = []
    for r in records:
        tmp = {}
        i = 0
        for c in r:
            tmp[ columns[i] ] = c[ list( c.keys() )[0] ]
            i=i+1
        rows.append(tmp)

    
    return rows

# Query and wait for result using Redshift Data API
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
    
    sql_statement = "select src_tbl, tgt_tbl,load_chkpt_col,load_max_rows,redshift_cluster_id,redshift_user,redshift_database,redshift_log_tbl,redshift_businessdate_tbl, 'call %s.sp_sync_merge_changes(SYSDATE,'''||src_tbl||''','''||tgt_tbl||''','''||load_chkpt_col||''','''||redshift_log_tbl||''','''||redshift_businessdate_tbl||''','||load_max_rows||')' as SQL_inp from %s.etlfw_load_details a inner join %s.etlfw_load_tp_master b on a.load_key=b.load_key cross join %s.etlfw_login_parameters where load_tp = '%s' and load_frequency = '%s';" % (v_schema_name, v_schema_name, v_schema_name, v_schema_name, load_type, load_frequency)
    
    print (sql_statement)
    
    pf=query(sql_statement, v_cluster_identifier, v_secret_arn, v_database_name)
    print(pf)
    
    return pf

