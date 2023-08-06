from jiange.log import LogAgent
from jiange.file import dump_json


class AgentBase(object):

    def __init__(self, *args, **kwargs):
        self.skill_name = None
        self.log = LogAgent()

    def dispatch(self, *args, **kwargs):
        raise NotImplementedError

    def response(self, *args, **kwargs):
        """

        e.g.
        response = {
            'code': 200,
            'message': 'success',
            'data': {
                'output': output,
                'skill_name': self.skill_name
            }
        }
        """
        raise NotImplementedError

    def log_request_response(self, request, response):
        body = {
            'request': request,
            'response': response,
            'skill_name': self.skill_name
        }
        body = dump_json(body, indent=False)
        self.log.info(body)

    def log_info(self, body):
        if isinstance(body, dict):
            body = dump_json(body, indent=False)
        self.log.info(body)
