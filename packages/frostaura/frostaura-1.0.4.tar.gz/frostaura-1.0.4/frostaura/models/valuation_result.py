'''This module defines valuation model components.'''

class ValuationResult:
    '''A model with all the post-valuation data for an asset.'''

    def __init__(self,
                 symbol: str,
                 company_name: str,
                 current_price: float,
                 valuation_price: float,
                 annual_dividend_percentage: float,
                 purchased_price: float = None):
        self.symbol = symbol
        self.company_name = company_name
        self.current_price = current_price
        self.valuation_price = valuation_price
        self.absolute_current_v_valuation_delta = 1 - (min(valuation_price, current_price) / max(valuation_price, current_price))
        self.is_overvalued = valuation_price < current_price
        self.annual_dividend_percentage = annual_dividend_percentage
        self.purchased_price = purchased_price
