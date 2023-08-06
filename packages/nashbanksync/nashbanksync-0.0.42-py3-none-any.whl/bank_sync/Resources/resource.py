from bank_sync.Resources.operations import Operations
from bank_sync.APIs.api_format import API
import json
from bank_sync.APIs.utils.generate_code import get_code


class Resource(API,Operations):

    _bank_id = 0

    _operation = 0

    _user_id = None

    _response = {}

    # The standardized request
    _request = {}

    _callback_data = None

    _read_url = ""

    _api = None

    _resource_id = -1

    _action='read'

    @property
    def READ(self):
        return 0

    def set_action(self, action):
        self._action = action
        return self

    def set_operation(self, operation):
        self._operation = operation
        return self

    def set_bank_id(self, bank_id):
        self._bank_id = bank_id
        return self

    def set_user_id(self, user_id):
        self._user_id = user_id
        return self

    def set_urls(self, urls):
        self.set_read_url(urls.get("read", ""))
        return self

    def payload(self):
        return {}

    def serialize(self):
        return self

    def response(self):
        return self._response

    def request(self):
        return self._request

    def set_response(self, response={}):
        self._response = response
        return self

    def set_request(self, request={}):
        self._request = request
        return self

    def set_read_url(self, read_url):
        self._read_url = read_url
        return self

    def get_read_url(self):
        return self._read_url

    def get_bank_id(self):
        return self._bank_id

    def get_user_id(self):
        return self._user_id

    def generate_code(self, length=6):
        return get_code(length)

    def get_operation(self):
        return self._operation

    def get_action(self):
        return self._action
    
    # This is the data that can be sent back to a callback, it can be overriden 
    # Each resource has the ability to decide what data can be sent back to a callback
    # This is the default standard of a sync callback data

    # You can use this method to simutalte a sync callback for endpoints that return data synchronously
    def sync_callback(self,response={}):
        # TODO implement a default method for sending async data
        pass
    
    def get_callback_data(self):
        return self._callback_data

    def read(self, payload=None, params=''):
        # Check if the bank exists
        if self.get_bank_id() in self.BANKS_CONF.keys():
            # set BANKS to be the default operation when no operation is passed
            # get a billler's API details
            bank = self.BANKS_CONF.get(self.get_bank_id(), self.BANKS)

            endpoint = bank.get(self.get_action(), {}).get('endpoint', '')

            operation, method = bank.get(self.get_action(), {}).get(
                'operations', {}).get(self.get_operation(), self.BANKS)

            # Check if any query params where passed, while creating the end point
            if bool(params):
                endpoint = f'{endpoint}/{operation}?{params}'
            else:
                endpoint = f'{endpoint}/{operation}'

            super().set_full_url(full_url=f"{bank.get('url','')}/{endpoint}")

            # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
            self._response = self._exec(payload, method)

        else:
            self._response = {'error':'Bank ID Does not Exist'}
        return self

    # This is the method that will be called execute an A.P.I. request.
    # Since most of the A.P.I. calls methods are similar, they are to be placed inside this method to avoid code duplication.
    #
    # It will only accept parameters unique to each A.P.I. request.
    def _exec(self, payload=None, method='POST', files=None):

        # NCBA send data back to our callback as XML converted to bytes
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        if files is None:
            payload = json.dumps(payload)
        else:
            payload = payload

        # Call the A.P.I. url by passing the variables to the super class method responsible for making requests to A.P.I. endpoints
        # The super class method returns a response that is returned by this method
        return super().api_request(payload=payload, method=method, files=files)