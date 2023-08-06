import requests
import json
import os
import datetime


class ORest(object):
    """
    Class for sending request over REST API, and handling the sent and received data in efficient manner.
    
    Parameters:
        url : (required) URL of deribit Rest API
        client_id : (optional: None) Credentials from Deribit
        client_secret : (optional: None) Credentials from Deribit
    Returns:
        DeribitREST Object
    """
        
    def __init__(self, url, client_id = None, client_secret=None):
        self.url = url
        self.result = None
        
        if (client_id is not None) and (client_secret is not None):
            self.__authorize_me(client_id,client_secret)
    
    
    # Executed if there is no __access_token (Never Authorized), or __token_expiry_time is less than current time (we need to refresh token)
    def __authorize_me(self,client_id=None,client_secret=None):
        """
        Private Method. 
        Called during object creation to get access_token and refresh_token for accessing private streams in Deribit.
        Called using refresh_token from subsequent calls whenever the access_token is expired.
        Parameters:
            client_id : (optional: None)
            client_secret : (optional: None)
        Returns:
            None
        """
        
        if ('__access_token' not in self.__dict__) or (datetime.datetime.now()>= self.__dict__.get("__token_expiry_time", datetime.datetime.now())):
            if (client_id is None) or (client_secret is None):
                authorization = self.auth(grant_type = "refresh_token", refresh_token = self.__refresh_token ).extract(['access_token', 'refresh_token','expires_in'])
            else:
                authorization = self.auth(grant_type = "client_credentials", client_id = client_id,client_secret = client_secret).extract(['access_token', 'refresh_token','expires_in'])

            self.__access_token = authorization['access_token']
            self.__refresh_token = authorization['refresh_token']
            self.__token_expiry_time = datetime.timedelta(seconds=int(authorization['expires_in'])) + datetime.datetime.now()

    # ensures to execute get request with whatever method you call
    def __getattr__(self, method):
        """
        Handler to use catch unavailable functions and map them to Deribit API Methods. If called method starts with 'private_', the REST Api call will be made with authentication headers.
        All the extra parameters will be packed as key-value pair and passed to Rest API.
        Parameters:
            method : (auto: Name of the Function called)
            **kwargs : (optional: {}) Will be passed as a parameter dictionary to REST Request
        Returns:
            Wrapped 'get' method which evenually returns DeribitREST Object
        """
        
        def wrapper(*args, **kwargs):
            parameters = {k:v for k,v in kwargs.items()}
            if method.startswith('private_'):
                self.__authorize_me()
                return self.get(method = '_'.join(method.split('_')[1:]), parameters=parameters, scope='private')            
            return self.get(method, parameters)
        return wrapper
    
    # executes get request and saves it in result
    def get(self, method, parameters = {}, scope = 'public'):
        """
        Handler to use catch unavailable functions and map them to Deribit API Methods. If called method starts with 'private_', the REST Api call will be made with authentication headers. 
        Parameters:
            method : (required) Method to be called on Deribit API
            parameters : (optional: {}) Parameters to be passes with REST request
            scope : (optional: public) Whether method is 'public' or 'private' 
        Returns:
            Adds API response data to 'result' property and then returns DeribitREST Object
        """
        headers={'Content-Type':'application/json','Authorization': f'Bearer {self.__access_token if scope == "private" else None}'}
        self.result = requests.get(url = os.path.join(self.url,scope,method), params = parameters,headers = headers).json()
        if 'error' in self.result: raise Exception("Error from REST API",self.result)
        return self
    
    # returns raw saved result 
    def raw(self):
        """
        Returns data stored in 'result' property 
        Parameters:
            None
        Returns:
            API response result from last get call
        """
        return self.result
    
    # extract information from saved result
    def extract(self, keys=None):
        """
        Extracts specific information from stored result that was obtained in last API call
        Parameters:
            keys : (optional: None) Single key as 'str' or list of keys
        Returns:
            Extracted Result (Str, Dict, List of Dict) based on passed key parameter
        """
        extract_keys = lambda dictionary: {k:v for k,v in dictionary.items() if k in keys} if isinstance(keys, list) else dictionary[keys]
        if not keys: 
            return self.result['result']
        if isinstance(self.result['result'], list):
            return list(map(extract_keys , self.result['result']))
        if isinstance(self.result['result'], dict):
            return extract_keys(self.result['result'])
        return self.result
