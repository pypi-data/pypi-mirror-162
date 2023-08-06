import requests
import base64
from loguru import logger
import sys


def get_headers(auth):
    '''
		get headers for your auth
	'''
    headers = {
        'accept': 'application/json',
        'Authorization': f'{auth}',
    }

    return headers


def get_workflow_url(url, name, group=None, subgroup=None):
    '''
		creating url for wf. Using group and subgroup
	'''
    subgroup = subgroup if group else None

    workflow_url = f"{url}/api/workflow/" + f"{group}" if group else f"{url}/api/workflow"
    workflow_url = f"{workflow_url}/" + f"{subgroup}/{name}" if subgroup else f'{workflow_url}/{name}'

    return workflow_url


class EsbConnect:
    '''
		Class for work with esb
	'''

    def __init__(self, user, password, esb_prod=False):
        '''
			create instance for user
		'''

        self.user = user
        self.password = password

        self.url = 'https://esb.rarus-cloud.ru' if esb_prod else 'http//esb.test.rarus-cloud.ru'

    def get_token(self):
        '''
			get keycloak token for instanses user
		'''
        basic_auth = base64.b64encode(f'{self.user}:{self.password}'.encode("UTF-8"))

        auth = f'Basic {basic_auth.decode("utf-8")}'

        headers = get_headers(auth)

        logger.info("Please wait. Token is generaring")

        response = requests.get(url=self.url + '/auth/tokens', headers=headers)

        self.token = response.json()['token']

    def get_task_result(self):
        '''
			Get result by your task id. This function have loop while task processing
		'''

        auth = f'Bearer {self.token}'
        headers = get_headers(auth=auth)

        task_is_processing = True

        while task_is_processing:
            logger.info('Task progressing...')

            response = requests.get(url=self.url + f'/api/task/{self.task_id}', headers=headers)

            task_is_processing = False if response.json()['progress'] == 100 else True

        self.task_result = response.json()['task_result']

        logger.info(f'Task ended. Result is - {self.task_result}')

        self.result = response.json()['data']

    def execute_workflow(self, request_data, workflow_name=None, workflow_group=None, workflow_subgroup=None):
        """
			execute your workflow and wait result
		"""
        try:

            workflow_url = get_workflow_url(self.url, workflow_name, workflow_group, workflow_subgroup)

        except TypeError:

            logger.error('Sorry, but you miss agrument "name"')
            sys.exit(1)
        self.get_token()

        auth = f'Bearer {self.token}'
        headers = get_headers(auth=auth)

        logger.info('Loading workflow')
        response = requests.post(workflow_url, headers=headers, json=request_data)
        try:
            self.task_id = response.json()['callbacks']['room']
        except KeyError:
            logger.error('Sorry, your request is wrong.')
            sys.exit(1)

        logger.info(f'Task is OK. Task id - {self.task_id}')

        self.get_task_result()

