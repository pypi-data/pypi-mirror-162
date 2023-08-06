'''This module defines Yahoo Finance data access components.'''
import yfinance as yf
import pandas as pd
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess

class YahooFinanceDataAccess(IPublicAssetDataAccess):
    '''Yahoo Finance public asset-related functionality.'''

    def get_symbol_history(self, symbol: str) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='max')

        return hist
