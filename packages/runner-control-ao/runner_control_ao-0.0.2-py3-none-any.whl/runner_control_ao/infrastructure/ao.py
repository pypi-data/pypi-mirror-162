import requests, json
from ddd_objects.infrastructure.ao import exception_class_dec
from ddd_objects.infrastructure.repository_impl import error_factory
from ddd_objects.domain.exception import return_codes
from .do import TaskDO, TaskUserRequestDO

class TaskControlAccessOperator:
    def __init__(self, ip: str, port: int, token: str) -> None:
        self.url = f"http://{ip}:{port}"
        self.header = {"api-token":token}

    def _check_error(self, status_code, info):
        if status_code>299:
            if isinstance(info['detail'], str):
                return_code = return_codes['OTHER_CODE']
                error_traceback = info['detail']
            else:
                return_code = info['detail']['return_code']
                error_traceback = info['detail']['error_traceback']
            raise error_factory.make(return_code)(error_traceback)

    @exception_class_dec(max_try=1)
    def check_connection(self, timeout=3):
        response=requests.get(f'{self.url}', headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        if info['message']=='Hello World':
            return True
        else:
            return False

    @exception_class_dec(max_try=1)
    def send_task_user_request(self, task_user_request: TaskUserRequestDO, timeout=3):
        data = json.dumps(task_user_request.to_json())
        response = requests.post(f'{self.url}/task_request', 
            headers=self.header, data=data, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def find_task_by_id(self, id, timeout=3):
        response = requests.get(f'{self.url}/task/id/{id}', 
            headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return TaskDO(**info)

    @exception_class_dec(max_try=1)
    def delete_task_by_id(self, id, timeout=3):
        response = requests.delete(f'{self.url}/task/id/{id}', 
            headers=self.header, timeout=timeout)
        info = json.loads(response.text)
        self._check_error(response.status_code, info)
        return info

    @exception_class_dec(max_try=1)
    def get_log_by_id(self, id):
        result = self.find_task_by_id(id)
        if result.succeed and result.get_value() is not None:
            details = result.get_value().task_details
            if details:
                return details[0].output
            else:
                return None
        else:
            return None

ip = '39.103.156.60'
port = 30014
token = 'c63EnpJdo1'
task_ao = TaskControlAccessOperator(ip, port, token)
