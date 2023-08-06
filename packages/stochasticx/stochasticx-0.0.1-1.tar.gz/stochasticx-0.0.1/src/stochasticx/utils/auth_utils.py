import os
import json
import requests
from pathlib import Path
from stochasticx.constants.urls import LOGIN_URL, TOKEN_AUTH_PATH


class LoginUtils:
    @staticmethod
    def login_request(username, password):
        """Private method to do the login request

        Args:
            username (str): username
            password (str): password

        Returns:
            str: token
        """
        login_info = {"email": username, "password": password}

        response = requests.post(LOGIN_URL, data=login_info)
        response.raise_for_status()

        response_data = response.json()
        token = response_data["tokens"]["access"]["token"]
        
        # Save token in ENV var
        os.environ["STOCHASTIC_TOKEN"] = token
        
        # Save token in a file
        token_path = Path(TOKEN_AUTH_PATH).resolve()
        
        if not token_path.exists():
            token_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(str(token_path), 'w', encoding='utf-8') as f:
            json.dump({
                "token": token
            }, f, ensure_ascii=False, indent=4)
        
        return token

class AuthUtils:
    
    @staticmethod
    def get_auth_headers():
        """Get authentication headers from the webapp

        Raises:
            ValueError: if token not found in the following ENV variable STOCHASTIC_TOKEN

        Returns:
            dict: auth headers
        """
        token = os.getenv("STOCHASTIC_TOKEN")
        
        if token is None:
            f = open(TOKEN_AUTH_PATH)
            data = json.load(f)
            token = data['token']

        
        if token is None:
            raise ValueError("Do login before running any request")
        else:
            return {
                'Authorization': 'Bearer ' + token
            }