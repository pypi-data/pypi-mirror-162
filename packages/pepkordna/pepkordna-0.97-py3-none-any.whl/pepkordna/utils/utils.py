from airflow.hooks.base_hook import BaseHook
from inspect import cleandoc
import requests
import logging
import sendgrid
from sendgrid.helpers.mail import *
import traceback
from airflow.models import Variable
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, SupportsAbs, Union, Type

class Status():
    """
    All status types standardized.

    Examples
    -------- 
    Status.SUCCESS
    """ 
   
    # Green
    SUCCESS = 'Success'
    COMPLETED = 'Completed'
    DONE = 'Done'
    # Red    
    FAILED = 'Failed' 
    ERROR = 'Error'
    # Yellow
    WARNING = 'Warning'  
    # Blue 
    NOTIFICATION = 'Notification'

    _STATUS_LIST = set()       

    @classmethod
    def status_list(cls):
        if not cls._STATUS_LIST:
            cls._STATUS_LIST = {
                getattr(cls, attr)
                for attr in dir(cls)
                if not attr.startswith("_") and not callable(getattr(cls, attr))
            }
        return cls._STATUS_LIST   

class Alerting:
    """
    Generic package that contains all standardized alerting.
    """

    @classmethod
    def log_to_gitlab(cls,
        git_project_id: str,
        git_project_area: str,
        git_issue_type: str,
        git_request_label: str,
        git_issue_description: str,
        git_issue_title: str,
        git_api_token: str = None,
        airflow_git_api_key_conn_id: str = None
        ) -> None:

        """
        Log issues to gitlab using gitlab API: https://docs.gitlab.com/ee/api/issues.html

        :param git_project_id: 
            Git project id.

        :param git_project_area: 
            Git project area - e.g: issues

        :param git_issue_type:
            Git type of issue - eg: incident

        :param git_request_label:
            Git request label - eg: Backlog (Sprint backlog)

        :param git_issue_title: 
            Title for the ticket logged.

        :param git_api_token:
            API token. Not advised to hardcode. If not passed in, param airflow_git_api_key_conn_id will be referenced.

        :param airflow_git_api_key_conn_id:
            Airflow connection id. Store api key as http connection in password field.
        
        Examples
        --------  
        Alerting().log_to_gitlab(
                    git_api_token='123',
                    git_project_id='123',
                    git_project_area='issues',
                    git_issue_type='issue',
                    git_request_label='Backlog',
                    git_issue_description='Process failed with exception xyz',
                    git_issue_title='Process that loads files failed')
        """

        if git_issue_description != None:
            git_issue_description = cleandoc(git_issue_description)

        if git_api_token is None and airflow_git_api_key_conn_id is None:
            raise ValueError('Require value for git_api_token or airflow_git_api_key_conn_id.')

        if airflow_git_api_key_conn_id != None:
            connection = BaseHook.get_connection(airflow_git_api_key_conn_id)
            git_api_token = connection.password

        headers = {
            "Authorization": 'Bearer '+git_api_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "title": git_issue_title,
            "issue_type": git_issue_type,
            "description": git_issue_description,
            "labels": git_request_label
        }

        end_point_url = 'https://gitlab.com/api/v4/projects/{git_project_id}/{git_project_area}'.format(
            git_project_id=git_project_id,
            git_project_area=git_project_area)

        try:
            req = requests.post(end_point_url,json=payload,headers=headers)
            req_text = req.text
            req_response_ok = req.ok
            
            if not req_response_ok:
                raise Exception(req_text)

            logging.info("Gitlab issue logged successfully.")
        except Exception:
            tb = traceback.format_exc()
            logging.info("Failed to log to gitlab --> Error: "+str(tb))

    @classmethod
    def send_gchat(cls,
        process_status: str,
        project_name: str,      
        extra_event_info: str,
        process_name: str,   
        data_engineers: List[Dict[str, str]] = [],      
        webhook_url: str = None,
        airflow_webhook_conn_id: str = None,
        log_url: str = None) -> None:

        """
        Send message to google chatroom.

        :param process_status: 
            Status of process. See class Status for all possible statuses. e.g: Status.FAILED
            Colour of `Status` field on Google chatroom card will change according to status passed in.

        :param project_name: 
            Name of GCP project where process is running in.

        :param extra_event_info:
            Details of alert.

        :param process_name:
            The name of the process. e.g: Dag Name

        :param data_engineers: 
            List of data engineers. 
                data_engineers.user_name: Name used on card to indicate who owns the process.
                data_engineers.user_id: Used to @user_id in chat. This value can only be retreived from the HTML DOM on the Google chat page.
                                        If not needed, leave value for key user_id blank -> "user_id:""                                   

        :param webhook_url:
            Webhook URL to google chatroom. If not passed in, airflow_webhook_conn_id will be referenced.

        :param airflow_webhook_conn_id:
            Airflow connection id to webhook.

        :param log_url:
            A URL to a process log. e.g: Airflow log URL.
        
        Examples
        --------  
        Alerting().send_gchat(
                    process_status=Status.FAILED,
                    project_name='google-cloud-project-name',      
                    extra_event_info='Process failed with exception xyz',
                    process_name='File Loader',
                    data_engineers=[{"user_name": "Name Surname","user_id": "1234567890"}],    
                    webhook_url='https://chat.googleapis.com/',
                    log_url='wwww.airflow_log_url_here.com')                   
        """

        if process_status not in Status.status_list():
            raise ValueError('Status value of ({status}) not valid. See class Status'.format(status=process_status))           

        if extra_event_info != None:
            extra_event_info = cleandoc(extra_event_info)

        if webhook_url is None and airflow_webhook_conn_id is None:
            raise ValueError('Require value for webhook_url or airflow_webhook_conn_id.')        

        if airflow_webhook_conn_id:
            connection = BaseHook.get_connection(airflow_webhook_conn_id)
            webhook_url = connection.password

        if process_status.lower() in ('success','completed','done'):
            # Green
            colour = '#339900'
        elif process_status.lower() in ('warning'):
            # Yellow
            colour = '#ffcc00'
        elif process_status.lower() in ('failed','error'):
            # Red
            colour = '#cc3300'
        elif process_status.lower() in ('notification'):
            # Blue
            colour = '#4977E1'
        else:
            # Black
            colour = '#000000'

        card_engineers_ids = ''
        engineers_all_names = ''

        if len(data_engineers) > 0:
            card_engineers_ids = ',"text": "{engineers_ids}"'
            engineers_all_at = ''
            for engineer in data_engineers:
                engineer_user_id = engineer['user_id']
                if len(engineer_user_id) > 0:
                    engineers = '<users/{engineer}> '.format(engineer=engineer_user_id)
                    engineers_all_at += engineers 

            card_engineers_ids = card_engineers_ids.format(engineers_ids=engineers_all_at)

            for engineer in data_engineers:
                engineer_username = engineer['user_name']
                if len(engineer_username) > 0:
                    engineers = '{engineer_name},'.format(engineer_name=engineer_username)
                    engineers_all_names += engineers

            engineers_all_names = engineers_all_names.rstrip(',')
        else:
            engineers_all_names = 'N/A'            

        body = """
        {{
        "cards": [
            {{
            "header": {{
                "title": "Process Name",
                "subtitle": "{process_name}"
            }},
            "sections": [
                {{
                "widgets": [             
                    {{
                        "keyValue": {{
                        "icon": "BOOKMARK",
                        "topLabel": "Status",
                        "content": "<font color='{colour}'>{process_status}</font>"      
                        }}
                    }}
                ]
                }},
                {{
                "widgets": [
                    {{
                        "keyValue": {{
                        "icon": "BOOKMARK",                    
                        "topLabel": "Log URL",
                        "contentMultiline": "true",                            
                        "content": "{log_url}",
                        "onClick": {{
                            "openLink": {{
                                "url": "{log_url}"
                            }}
                        }}                             
                    }}
                }}
                ]
                }},
                {{
                "widgets": [
                    {{
                        "keyValue": {{
                        "icon": "BOOKMARK",                    
                        "topLabel": "Project Name",
                        "content": "{project_name}"
                        }}
                    }}
                ]
                }},
                {{
                "widgets": [
                    {{
                        "keyValue": {{
                        "icon": "BOOKMARK",                    
                        "topLabel": "Data Engineers",
                        "content": "{engineers_all_names}"
                        }}
                    }}
                ]
                }},                
                {{                        
                "widgets": [
                    {{
                        "keyValue": {{
                        "icon": "BOOKMARK",                    
                        "topLabel": "Event Information",
                        "contentMultiline": "true",
                        "content": "{extra_event_info}"
                        }}
                    }}
                ]
                }},        
                {{
                "widgets": [
                    {{
                        "buttons": [                 
                            {{
                            "textButton": {{
                                "text": "OPEN PROJECT",
                                "onClick": {{
                                "openLink": {{
                                    "url": "https://console.cloud.google.com/bigquery?project={project_name}"
                                }}
                                }}
                            }}
                            }}
                        ]
                    }}
                ]
                }}
            ]
            }}
        ]
        {card_engineers_ids}
        }}
        """.format(
            process_name=process_name,
            log_url=log_url,
            extra_event_info=extra_event_info,
            process_status=process_status,
            project_name=project_name,
            engineers_all_names=engineers_all_names,
            card_engineers_ids=card_engineers_ids,
            colour=colour
            )

        try:
            req = requests.post(url=webhook_url,data=body)    
            req_text = req.text
            req_response_ok = req.ok
            
            if not req_response_ok:
                raise Exception(req_text)

            logging.info("Gchat sent successfully.")
        except Exception:
            tb = traceback.format_exc()
            logging.info("failed to send gchat notification --> Error: "+str(tb))

    @classmethod
    def send_sendgrid_email(cls,
        email_body: str,
        email_to_list: List[str],
        email_subject: str,
        from_email: str = 'DE_NOTIFICATION_FROM_EMAIL_ADDRESS',        
        email_cc_list: List[str] = [],
        content_type: str = 'plain' or 'html',
        sendgrid_api_key: str = None,
        airflow_sendgrid_api_key_conn_id: str = None
        ) -> None:

        """
        Send email using sendgrid API

        :param email_body: 
            Email body.

        :param email_to_list: 
            List of email addresses to email.

        :param email_subject:
            Email subject.

        :param from_email:
            The from email address. Can also pass variable name for Airflow. Default already assigned for data engineering team.

        :param email_subject:
            Email subject.

        :param email_cc_list:
            List of email addresses to CC.

        :param content_type:
            Email body content type. plain or html.

        :param sendgrid_api_key:
            Sendgrid API key. Not advised to hardcode. If not passed in, param airflow_sendgrid_api_key_conn_id will be referenced.      

        :param airflow_sendgrid_api_key_conn_id:
            Airflow connection id. Store api key as http connection in password field.
        
        Examples
        --------  
        Alerting().send_sendgrid_email(
                    sendgrid_api_key='api_key',
                    email_body='test',
                    email_to_list=['user@email.com'],
                    email_cc_list=['user@email.com'],
                    email_subject='Test')                    
        """        

        email_body = cleandoc(email_body)

        if sendgrid_api_key is None and airflow_sendgrid_api_key_conn_id is None:
            raise ValueError('Require value for sendgrid_api_key or airflow_sendgrid_api_key_conn_id.')  

        if airflow_sendgrid_api_key_conn_id:
            connection = BaseHook.get_connection(airflow_sendgrid_api_key_conn_id)
            sendgrid_api_key = connection.password     

        # Check if from_email is an airflow variable
        if '@' not in from_email:
            from_email_var = Variable.get(from_email)
            if from_email_var == None:
                raise Exception('Airflow variable ({from_email}) not found.'.format(from_email=from_email))
            else:
                from_email = from_email_var

        if not type(email_to_list) is list:
            raise TypeError('email_to_list not of type list.') 
        if not type(email_cc_list) is list:
            raise TypeError('email_cc_list not of type list.')             

        sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
        from_email_inst = Email(from_email)
        p = Personalization()

        for email in email_to_list:
            p.add_to(To(email))

        for email in email_cc_list:
            p.add_to(To(email))

        content = Content("text/"+content_type, email_body)
        mail = Mail(from_email=from_email_inst,subject=email_subject,plain_text_content=content)
        mail.add_personalization(p)    

        try:
            req = sg.client.mail.send.post(request_body=mail.get())    
            req_status_code = req.status_code
            req_body = req.body        
            
            if req_status_code not in (200,201,202):
                raise Exception(req_body)

            logging.info("Email sent successfully.")
        except Exception:
            tb = traceback.format_exc()
            logging.info("failed to send email notification --> Error: "+str(tb)) 

class AirflowCallbacks:
    """
    Default callbacks for airflow.

    :param airflow_context (obj): 
        Context object from airflow
    """

    def __init__(self, airflow_context):  
        self.airflow_context = airflow_context 
        self.alerting = Alerting()

    def get_git_ticket_description(self) -> str:

        exception = self.airflow_context.get('exception')
        task_id = self.airflow_context.get('task_instance').task_id
        dag_id = self.airflow_context.get('task_instance').dag_id
        exec_date = self.airflow_context.get('execution_date')
        log_url = self.airflow_context.get('task_instance').log_url

        description = cleandoc("""
        Dag ID: {dag_id}<br>
        Task ID: {task_id}<br>
        Execution Date: {exec_date}<br>
        URL: [Composer Log URL]({log_url})<br>

        Exception:<br>
        {exception}
        """).format(
            dag_id=dag_id,
            task_id=task_id,
            exec_date=exec_date,
            log_url=log_url,
            exception=exception
        )   

        return description   

    def default_on_success_callback(self,
            email_to_list: List[str],        
            email_cc_list: List[str],
            data_engineers: List[Dict[str, str]] = [],   
            airflow_gchat_webhook_conn_id: str = None,
            airflow_sendgrid_api_key_conn_id: str = None,
            send_gchat=False,      
            send_email=False) -> None:
        """
        Default on_success callback for Airflow operators.

        :param reference class Alerting.send_sendgrid_email:
        :param reference class Alerting.send_gchat:        

        :param send_gchat:
            If True, send message via google chat.

        :param send_email:            
            If True, send email.
        """            

        if send_email:

            if email_to_list is None:
                raise ValueError('Param email_to_list cannot be value of None when send_email is being used.')            

            # Sendgrid API key
            connection = BaseHook.get_connection(airflow_sendgrid_api_key_conn_id)
            sendgrid_api_key = connection.password
            
            email_body = """
            Execution Date: {execution_date}
            Log URL: {log_url}
            """.format(
                log_url=self.airflow_context.get('task_instance').log_url,
                execution_date=self.airflow_context.get('execution_date')
            )
            title = 'DAG Success: DAG_ID: {dag_id}. TASK_ID: {task_id}'.format(
                dag_id=self.airflow_context.get('task_instance').dag_id,
                task_id=self.airflow_context.get('task_instance').task_id
                )
            try:
                self.alerting.send_sendgrid_email(
                    sendgrid_api_key=sendgrid_api_key,
                    email_body=email_body,
                    email_to_list=email_to_list,
                    email_cc_list=email_cc_list,
                    email_subject=title)
            except Exception:
                tb = traceback.format_exc()
                logging.info("failed to send email notification --> Error: "+str(tb)) 

        if send_gchat:

            if airflow_gchat_webhook_conn_id is None:
                raise ValueError('Param airflow_gchat_webhook_conn_id cannot be value of None when send_gchat is being used.')               

            # GChat Webhook
            connection = BaseHook.get_connection(airflow_gchat_webhook_conn_id)
            gchat_room_webhook = connection.password
                        
            try:            
                self.alerting.send_gchat(
                        process_status=Status.SUCCESS,
                        project_name='dna-data-prod',   
                        data_engineers=data_engineers,   
                        extra_event_info=None,
                        process_name=self.airflow_context.get('task_instance').dag_id,   
                        webhook_url=gchat_room_webhook,
                        log_url=self.airflow_context.get('task_instance').log_url)
            except Exception:
                tb = traceback.format_exc()
                logging.info("failed to send gchat notification --> Error: "+str(tb)) 

    def default_on_failure_callback(self,
            email_to_list: List[str] = None,        
            email_cc_list: List[str] = None,          
            git_project_id: str = None,
            data_engineers: List[Dict[str, str]] = [],            
            airflow_gchat_webhook_conn_id: str = None,
            airflow_git_api_key_conn_id: str = None,
            airflow_sendgrid_api_key_conn_id: str = None,
            git_request_label: str = 'Backlog',
            send_gchat = False,
            send_gitlab = False,           
            send_email = False) -> None:
        """
        Default on_failure callback for Airflow operators.

        :param reference class Alerting.send_sendgrid_email:
        :param reference class Alerting.send_gchat:  
        :param reference class Alerting.log_to_gitlab:          

        :param send_gchat:
            If True, send message via google chat.

        :param send_gitlab:            
            If True, log ticket to gitlab.

        :param send_email:            
            If True, send email.            
        """             

        if send_email:

            if email_to_list is None:
                raise ValueError('Param email_to_list cannot be value of None when send_email is being used.')

            if airflow_sendgrid_api_key_conn_id is None:
                raise ValueError('Param airflow_sendgrid_api_key_conn_id cannot be value of None when send_email is being used.')

            # Sendgrid API key
            connection = BaseHook.get_connection(airflow_sendgrid_api_key_conn_id)
            sendgrid_api_key = connection.password

            email_body = """
            Execution Date: {execution_date}
            Log URL: {log_url}
            Exception: {exception}
            """.format(
                exception=self.airflow_context.get('exception'),
                log_url=self.airflow_context.get('task_instance').log_url,
                execution_date=self.airflow_context.get('execution_date')
            )
            title = 'DAG Failure: DAG_ID: {dag_id}. TASK_ID: {task_id}'.format(
                dag_id=self.airflow_context.get('task_instance').dag_id,
                task_id=self.airflow_context.get('task_instance').task_id
                )
            try:
                self.alerting.send_sendgrid_email(
                    sendgrid_api_key=sendgrid_api_key,
                    email_body=email_body,
                    email_to_list=email_to_list,        
                    email_cc_list=email_cc_list,            
                    email_subject=title)
            except Exception:
                tb = traceback.format_exc()
                logging.info("failed to send email notification --> Error: "+str(tb)) 

        if send_gchat:

            if airflow_gchat_webhook_conn_id is None:
                raise ValueError('Param airflow_gchat_webhook_conn_id cannot be value of None when send_gchat is being used.')            

            # GChat Webhook
            connection = BaseHook.get_connection(airflow_gchat_webhook_conn_id)
            gchat_room_webhook = connection.password

            try: 
                self.alerting.send_gchat(
                        process_status=Status.FAILED,
                        project_name='dna-data-prod',      
                        data_engineers=data_engineers,
                        extra_event_info=self.airflow_context.get('exception'),
                        process_name=self.airflow_context.get('task_instance').dag_id,   
                        webhook_url=gchat_room_webhook,
                        log_url=self.airflow_context.get('task_instance').log_url)
            except Exception:
                tb = traceback.format_exc()
                logging.info("failed to send gchat notification --> Error: "+str(tb))  

        if send_gitlab:

            if git_project_id is None:
                raise ValueError('Param git_project_id cannot be value of None when send_gitlab is being used.')  

            if airflow_git_api_key_conn_id is None:
                raise ValueError('Param airflow_git_api_key_conn_id cannot be value of None when send_gitlab is being used.')                              

            # Gitlab API Key
            connection = BaseHook.get_connection(airflow_git_api_key_conn_id)
            gitlab_api_key = connection.password

            try:            
                git_ticket_description = self.get_git_ticket_description()
                self.alerting.log_to_gitlab(
                        git_api_token=gitlab_api_key,
                        git_project_id=git_project_id,
                        git_project_area='issues',
                        git_issue_type='issue',
                        git_request_label=git_request_label,
                        git_issue_description=git_ticket_description,
                        git_issue_title=title
                )
            except Exception:
                tb = traceback.format_exc()
                logging.info("Failed to log to gitlab --> Error: "+str(tb))
