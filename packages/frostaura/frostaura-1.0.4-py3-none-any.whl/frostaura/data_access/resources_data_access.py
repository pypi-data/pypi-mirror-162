'''This module defines resources data access components.'''
from importlib import resources

class IResourcesDataAccess:
    '''Component to perform resource related actions.'''

    def get_resource(self, path: str, package_name) -> bytes:
        '''Get a resource as a byte stream.'''

        raise NotImplementedError()

class EmbeddedResourcesDataAccess(IResourcesDataAccess):
    '''Component to perform embedded resource related actions.'''

    def get_resource(self, path: str, package_name: str='frostaura') -> bytes:
        '''Get a resource as a byte stream that was embedded in a given package.'''

        with resources.open_binary(package_name, path) as resource:
            return resource.read()
