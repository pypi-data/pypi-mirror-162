'''This module defines personal asset data access components.'''

class IPersonalAssetDataAccess:
    '''Component to perform functions related to personal / owned assets.'''

    def get_supported_assets(self) -> list:
        '''Get all supported asset names and symbols.'''

        raise NotImplementedError()

    def get_personal_transactions(self) -> list:
        '''Get all personal transactions made on an EasyEquities account.'''

        raise NotImplementedError()
