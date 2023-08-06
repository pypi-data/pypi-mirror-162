'''This module defines Easy Equities data access components.'''
from datetime import datetime
import json

class IPersonalAssetDataAccess:
    '''Component to perform functions related to personal / owned assets.'''

    def get_supported_assets(self) -> list:
        '''Get all supported asset names and symbols.'''

        raise NotImplementedError()

    def get_personal_transactions(self) -> list:
        '''Get all personal transactions made on an EasyEquities account.'''

        raise NotImplementedError()

class EasyEquitiesPersonalAssetDataAccess(IPersonalAssetDataAccess):
    '''EasyEquities-related functionality.'''

    def get_supported_assets(self) -> list:
        '''Get all supported asset names and symbols.'''

        with open('./../../data/easy_equities_us_stocks.json', 'r') as file:
            return json.load(file)

    def get_personal_transactions(self) -> list:
        '''Get all personal transactions made on an EasyEquities account.'''

        return {
            'TSLA': {
                'name': 'Tesla Inc.',
                'symbol': 'TSLA',
                'transactions': [
                    { 'value': 0.0688, 'date': datetime(2022, 7, 28, 0, 0) }
                ]
            },
            'AAPL': {
                'name': 'Apple Inc.',
                'symbol': 'AAPL',
                'transactions': [
                    { 'value': 0.4317, 'date': datetime(2022, 6, 28, 0, 0) }
                ]
            },
            'DDD': {
                'name': '3D Systems Corporation',
                'symbol': 'DDD',
                'transactions': [
                    { 'value': 8.8925, 'date': datetime(2022, 8, 5, 0, 0) }
                ]
            },
            'SBSW': {
                'name': 'Sibanye Stillwater Ltd',
                'symbol': 'SBSW',
                'transactions': [
                    { 'value': 1.1265, 'date': datetime(2022, 8, 5, 0, 0) }
                ]
            },
        }
