'''This module defines HTTP resources data access component.'''
import requests
from bs4 import BeautifulSoup
from frostaura.data_access.resources_data_access import IResourcesDataAccess

class HtmlResourcesDataAccess(IResourcesDataAccess):
    '''Component to perform HTML resource related actions.'''

    def get_resource(self, path: str) -> bytes:
        '''Get a queryable HTML page via a URL (path).'''

        response: requests.Response = requests.get(url=path, headers={
            'User-Agent': 'PostmanRuntime/7.29.0'
        })
        response_text: str = response.text

        return BeautifulSoup(response_text, 'html.parser')
