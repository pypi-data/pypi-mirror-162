from dataclasses import dataclass
import requests
from .api_payload import APIPayload
from .api_credentials import APICredentials
from requests.exceptions import ConnectionError, Timeout, ConnectTimeout


@dataclass(order=False)
class APIPayment:
    """
    transfermovil payment class
    
    Attributes:
        test(bool): Transfermovil enviroment
        ssl_verify(bool): Verify ssl certificate.
        
    """

    test: bool
    ssl_verify: bool

    def charge(self, url: str, credential: APICredentials,
               payload: APIPayload) -> dict:
        """ 
        The function to create payment. 
        
        Parameters:
            url: url to make request
            credential(APICredentials): request credential
            payload(APIPayload): request payload
  
        Returns:
            response(dict): Request response
              
        """

        if not isinstance(self.ssl_verify, bool):
            raise Exception("Incorrect ssl_verified")
        if not isinstance(credential, APICredentials):
            raise Exception("Incorrect credentials")
        if not isinstance(payload, APIPayload):
            raise Exception("Incorrect payload")

        response = requests.post(url,
                                 headers=credential.getheaders(),
                                 json=payload.getPayload(),
                                 verify=self.ssl_verify)
        try:
            if response.status_code != 200:
                return {'success': False, 'error': response.reason,
                        'error_detail': None}
            else:
                json = response.json()
                if not json['PayOrderResult']['Success']:
                    return {'success': False,
                            'error': json['PayOrderResult']['Resultmsg']}
                return json

        except ConnectionError as error:
            return {'success': False, 'error': 'Network Error',
                    'error_detail': error}
        except Timeout as error:
            return {'success': False, 'error': 'Network Conection Timeout',
                    'error_detail': error}
