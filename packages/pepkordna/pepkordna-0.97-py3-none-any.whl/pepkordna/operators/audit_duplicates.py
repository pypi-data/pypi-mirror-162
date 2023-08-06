from pepkordna.operators.audit_base_operator import AuditBaseOperator
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, SupportsAbs, Union, Type

class AuditDuplicates(AuditBaseOperator):
    """
    Check for duplicates on source table and log query results to smart alerts table.

    :param results_table_project_id: 
        Project name where audit results will get logged to. Expect table in dataset named dataops.

    :param bigquery_conn_id: 
        Airflow Bigquery connection id.

    :param source_table:
        Source table to be audited.

    :param cols:
        list of columns that will make up the unique key to be audited.

    :param partition_col: 
        Column name table is partioned on.

    :param partition_col_value_start:
        Start value for audit range. If no value is passed, today date will be used.

    :param partition_col_value_end:
        End value for audit range. If no value is passed, (today date)-3 months will be used.

    Examples
    -------- 
    test_aud_dups = AuditDuplicates(
        task_id='test_aud_dups',
        results_table_project_id='gcp_project_id',
        bigquery_conn_id='default_conn_id',
        source_table='gcp_project_id.dataset_id.table_name',
        cols=['user_id','snapshot_date'],
        partition_col='snapshot_date',
        partition_col_value_start='2022-01-31',
        partition_col_value_end='2022-05-31'
    )      
    """

    partition_clause = """
        {partition_col} between '{partition_col_value_start}'
        and
        '{partition_col_value_end}'
    """

    aud_sql = """
    select '{cols}' unique_key, count(*) rec_cnt
    from `{source_table}`
    where {partition_clause}
    group by {cols}
    having count(*) > 1
    """

    def __init__(self,
            results_table_project_id: str,
            bigquery_conn_id: str,
            source_table: str,
            cols: List[str],
            partition_col: str,
            partition_col_value_start: str = None,
            partition_col_value_end: str = None,            
            delegate_to=None,
            *args,
            **kwargs):
        
        # Default 3 months ago
        if partition_col_value_start == None:
            partition_col_value_start = date.today() - relativedelta(months=+3)

        if partition_col_value_end == None:
            partition_col_value_end =  date.today()   

        if partition_col == '' or partition_col == None:
            partition_clause_fmt = '1 = 1'
        else:
            partition_clause_fmt = self.partition_clause.format(
                partition_col=partition_col,
                partition_col_value_start=partition_col_value_start,
                partition_col_value_end=partition_col_value_end
            )                   
            
        self.aud_sql_fmt = self.aud_sql.format(
            source_table=source_table,
            cols=','.join(cols),
            partition_col=partition_col,
            partition_clause=partition_clause_fmt
        )         

        super().__init__(
            results_table_project_id=results_table_project_id,
            bigquery_conn_id=bigquery_conn_id,     
            delegate_to=delegate_to,            
            aud_sql=self.aud_sql_fmt,
            *args,
            **kwargs)
