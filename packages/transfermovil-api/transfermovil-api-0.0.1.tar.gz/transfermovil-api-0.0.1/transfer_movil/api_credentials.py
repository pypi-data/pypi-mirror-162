from dataclasses import dataclass
import pendulum
import hashlib
import base64


@dataclass(order=False)
class APICredentials:
    """
    transfermovil credentials class
    
    Attributes:   
        username(str): ecommerce username
        source(str): ecommerce id
        seed(str): ecommerce seed

    """

    username: str
    source: str
    seed: str

    @staticmethod
    def __encodepass__(text: str = None) -> str:
        """ 
        The function to encode header password. 
  
        Parameters: 
            text (str): header info to encode 
            
            
        Returns:
            encode64_string (str): Return encoded text
              
        """

        if not isinstance(text, str) or len(text) == 0:
            raise Exception("Encode text cannot be empty")

        hash_string = hashlib.sha512(text.encode()).digest()
        encode64 = base64.b64encode(hash_string)
        encode64_string = str(encode64)
        return encode64_string[2:-1]

    def getheaders(self) -> dict:
        """ 
        The function to get transfermovil header.
        Returns:
            headers (dict): Return request headers.
        """

        if not isinstance(self.username, str) or len(self.username) == 0:
            raise Exception("Incorrect Username")

        elif not isinstance(self.source, str) or len(self.source) == 0:
            raise Exception("Incorrect Source")

        elif not isinstance(self.seed, str) or len(self.seed) == 0:
            raise Exception("Incorrect Seed")

        current_date = pendulum.now()
        headers = {"Content-Type": "application/json",
                   "username": self.username,
                   "source": self.source,
                   "password": self.__encodepass__(
                       f"{self.username}"
                       f"{current_date.day}"
                       f"{current_date.month}"
                       f"{current_date.year}"
                       f"{self.seed}"
                       f"{self.source}"
                   )}
        return headers
