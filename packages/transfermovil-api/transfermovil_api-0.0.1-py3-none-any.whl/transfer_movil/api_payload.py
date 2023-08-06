from dataclasses import dataclass
import validators


@dataclass(order=False)
class APIPayload:
    """
    transfermovil request payload class
    
    Attributes:
        amount(float): order total amount
        phone(str): user mobile phone number
        currency(str): order currency
        description(str): order description
        order_id(str): order id description
        source(str): ecommerce source
        webhook(str): ecommerce response url
        valid_time(int): order valid time
    """

    amount: float
    currency: str
    order_id: str
    source: str
    webhook: str
    valid_time: int = 0
    phone: str = ''
    description: str = 'description'

    def getPayload(self) -> dict:
        """ 
        The function to get request payload. 
  
        Returns:
            request(dict): Payload object
              
        """
        if not isinstance(self.amount, float) or self.amount <= 0:
            raise Exception("Incorrect amount")

        elif not isinstance(self.currency, str) or len(self.currency) == 0:
            raise Exception("Incorrect currency")

        elif not isinstance(self.order_id, str) or len(self.order_id) <= 3:
            raise Exception("Incorrect Order ID")

        elif not isinstance(self.source, str) or len(self.source) == 0:
            raise Exception("Incorrect Source")

        elif not validators.url(self.webhook):
            raise Exception("Incorrect Webhook")

        elif not isinstance(self.valid_time, int):
            raise Exception("Incorrect Valid Time")

        elif not isinstance(self.phone, str):
            raise Exception("Incorrect Phone")

        elif not isinstance(self.description, str):
            raise Exception("Incorrect description")

        request = {
            'request': {
                'Amount': self.amount,
                'Phone': self.phone,
                'Currency': self.currency,
                'Description': self.description,
                'ExternalId': self.order_id,
                'Source': int(self.source),
                'UrlResponse': self.webhook,
                'ValidTime': self.valid_time
            }
        }
        return request
