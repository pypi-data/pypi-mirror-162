'''This module defines embedded resources data access component.'''
from importlib import resources
from typing import BinaryIO
from logging import debug, info
from frostaura.data_access.resources_data_access import IResourcesDataAccess

class EmbeddedResourcesDataAccess(IResourcesDataAccess):
    '''Component to perform embedded resource related actions.'''

    def __init__(self, config: dict):
        self.config = config

    def get_resource(self, path: str) -> BinaryIO:
        '''Get a resource as a byte stream that was embedded in a given package.'''

        info(f'Fetching embedded resource "{path}".')

        if not 'package_name' in self.config:
            debug('No value found for "package_name" in config. Setting default "frostaura".')
            self.config['package_name'] = 'frostaura'

        return resources.open_binary(self.config['package_name'], path)
