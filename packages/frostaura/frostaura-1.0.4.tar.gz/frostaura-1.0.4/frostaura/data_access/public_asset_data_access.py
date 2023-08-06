'''This module defines Yahoo Finance data access components.'''
import yfinance as yf
import pandas as pd

class IPublicAssetDataAccess:
    '''Component to perform functions related to public assets.'''

    def get_symbol_history(self, symbol: str) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        raise NotImplementedError()


class YahooFinanceDataAccess(IPublicAssetDataAccess):
    '''Yahoo Finance-related functionality.'''

    def get_symbol_history(self, symbol: str) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='max')

        return hist
