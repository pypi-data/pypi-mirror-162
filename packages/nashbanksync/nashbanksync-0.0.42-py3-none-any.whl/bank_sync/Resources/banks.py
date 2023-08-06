from bank_sync.Resources.resource import Resource
from bank_sync.Resources.accounts import Accounts
from bank_sync.Resources.payments import Payments


class Bank(Resource):

    _resources = {
        "Accounts": Accounts(),
        "Payments": Payments(),
    }

    # use the nash object to confirm if the user accessing the banks is logged in
    _nash = None

    urls = {}

    def __init__(self, nash, bank_id=None):
        self._nash = nash
        super().__init__("BankAPI", self._nash.get_headers(), self._nash.get_params())
        super().set_bank_id(bank_id)

    def resource(self, resource_name):
        resource = self._resources[resource_name].set_bank_id(super().get_bank_id()).set_headers(self._nash.get_headers())

        return resource

    def get_resources(self):
        return list(self._resources.keys())

    def callback(self, bank_name=None, payload=None, method='POST', endpoint='/callback'):

        if bank_name is not None:
            endpoint = f'{endpoint}/{bank_name}'

        return super().read(payload, method, endpoint)

    def sample_payload(self, bank_id=None, payload=None, method='GET', endpoint='/sample_payload'):

        if bank_id is not None:
            endpoint = f'{endpoint}/{bank_id}'

        return super().read(payload, method, endpoint)
    
    # This is a 'global' function
    # Used to get operations supported by Nash
    def bank_operations(self):
        return self.exec_global_function(operation=super().OPERATIONS)
    
    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types(self):
        return self.bank_types_by_id()
    
    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types_by_id(self,bank_id=None):
        return self.exec_global_function(operation=super().BANKS_BY_ID, bank_id=bank_id)
    
    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types_by_code(self,bank_code=None):
        return self.exec_global_function(operation=super().BANKS_BY_CODE, bank_id=bank_code)

    # This is a 'global' function
    # Used to get sample_payloads for a resource's end point
    def sample_payload(self, bank_id=None, payload=None):
        return self.exec_global_function(operation=super().SAMPLE_DATA, bank_id=bank_id, payload=payload)

    # This is a 'global' function
    # Used to get sample_payloads for a resource's end point
    def countries(self, payload=None):
        return self.exec_global_function(operation=super().COUNTRIES, payload=payload)

    # This method is responsible for returning the bank id that's to execute the 'global' functions
    def exec_global_function(self, operation = 0, bank_id=None, payload=None):
        data = {}
        # Set the operation to be performed 
        super().set_operation(operation)

        # If a bank id is supplied 
        if bank_id is not None:
            # If a user did not set a bank id
            if super().get_bank_id() < 1:
                # If a user did not set a bank id, set the bank_id to the Global Biller ID 0
                super().set_bank_id(super().GLOBAL)
                # Executing the method below after setting the Global Biller ID will ensure
                # that we are calling/get access to the SAMPLE_DATA operation found
                # linked to the Global ID. Pass the bank id whose sample data the user wants
                data = super().read(payload,params=f'bank_id={bank_id}')

            # If a user set a bank id
            elif super().get_bank_id() > 0:
                # Since operations are linked to a bank id, we want to get access to the Global Biller ID,
                # so as to get access to the SAMPLE_DATA operation, execute the call, then set bank id to
                # the user's bank ID

                # Get the user's bank id and save it temporarily (temp)
                temp = super().get_bank_id()
                # Set the bank id to the Global Biller ID
                super().set_bank_id(super().GLOBAL)

                # Execite the SAMPLE_DATA operation
                # Pass the bank id whose sample data the user wants
                data = super().read(payload,params=f'bank_id={bank_id}')

                # reset the bank_id to the bank id set by the user before (temp)
                super().set_bank_id(temp)

        # If a bank id is not supplied 
        else:
            # If a user did not set a bank id
            if super().get_bank_id() < 1:
                # If a user did not set a bank id, set the bank_id to the Global Biller ID 0
                super().set_bank_id(super().GLOBAL)         
                # Executing the method below after setting the Global Biller ID will ensure
                # that we are calling/get access to the SAMPLE_DATA operation found
                # linked to the Global ID. Pass the bank id whose sample data the user wants   
                data = super().read(payload,params=f'bank_id={bank_id}')

            # If a user did set a bank id
            elif super().get_bank_id() > 0:
                # Since operations are linked to a bank id, we want to get access to the Global Biller ID,
                # so as to get access to the SAMPLE_DATA operation, execute the call, then set bank id to
                # the user's bank ID

                # Get the user's bank id and save it temporarily (temp)
                temp = super().get_bank_id()
                # Set the bank id to the Global Biller ID
                super().set_bank_id(super().GLOBAL)

                # Execite the SAMPLE_DATA operation
                # Pass the bank id whose sample data the user wants
                data = super().read(payload,params=f'bank_id={bank_id}')
                # Set bank id to back the user's orginal bank id
                super().set_bank_id(temp)
        
        # The 'if else' complexities above are done to ensure that the users can call this method
        # anywhere in their code, if they wish to get a sample data

        return data

    