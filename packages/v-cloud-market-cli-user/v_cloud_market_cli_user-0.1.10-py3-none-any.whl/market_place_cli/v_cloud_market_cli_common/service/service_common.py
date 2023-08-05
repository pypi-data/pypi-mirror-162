from v_cloud_market_cli_common.utils.service_error import (
    HttpNotFoundException,
    HttpBadRequestException
)

class ServiceCommon:

    def __init__(self):
        pass

    @staticmethod
    def validate_response(resp):
        if not isinstance(resp, dict) and not isinstance(resp, list):
            raise HttpNotFoundException
        elif 'error' in resp:
            if 'code' in resp['error'] and 'message' in resp['error']:
                raise Exception(f"Net Error: {resp['error']['message']}")
            else:
                raise Exception(f"Net Error: {resp}")
