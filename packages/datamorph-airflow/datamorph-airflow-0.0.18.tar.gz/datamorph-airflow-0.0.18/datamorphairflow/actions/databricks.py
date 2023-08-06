from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator


class DMDatabricksRunNowJobOperator(DatabricksRunNowOperator):
    """
    Extension of databricks run now operator with custom status push to xcom
    """

    def __init__(
            self, *args, **kwargs
    ):
        super().__init__(do_xcom_push=True, *args, **kwargs)
        # self.databricks_conn_id = databricks_conn_id

    def execute(self, context):
        super(DMDatabricksRunNowJobOperator, self).execute(context)
        #databricks_hook = DatabricksHook(databricks_conn_id=self.databricks_conn_id)
        run_id = context["task_instance"].xcom_pull(self.task_id, key="run_id")
        self.log.info(run_id)
        self.log.info(self.run_id)
        #result = databricks_hook.get_run_state_result(self.run_id)
        #self.log.info("Result:")
        #self.log.info(result)
        #context['ti'].xcom_push(key='status', value=result)
        #return result