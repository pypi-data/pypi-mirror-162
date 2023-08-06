'''This module defines valuation engine components.'''
from frostaura.data_access.html_data_access import HtmlDataAccess
from frostaura.models.valuation_result import ValuationResult

class IAssetValuationEngine:
    '''Component to perform functions related to asset valuation.'''

    def valuate(self, symbol: str, company_name: str) -> ValuationResult:
        '''Valuate a given asset.'''

        raise NotImplementedError()

class FinvizAssetValuationEngine(IAssetValuationEngine):
    '''Valuation-related functionality using Finviz under-the-hood.'''

    def __init__(self, html_data_access: HtmlDataAccess):
        self.html_data_access = html_data_access

    def __determine_intrinsic_value__(self,
                                      eps_ttm: float, # Total trailing annual earnings per share.
                                      growth_rate: float, # Projected 5 year EPS.
                                      pe_ratio: float, # Price per earnings growth rate. 2x growth_rate if unsure.
                                      min_rate_of_return: float = 0.15, # Rate of return we want to make.
                                      margin_of_safety: float = 0.3 # Margin to padd our valuation with in order to mitigate risk. 20-50% usually.
                              ) -> float:
        assert eps_ttm > 1
        assert growth_rate > 0 and growth_rate < 1
        assert pe_ratio > 1
        assert min_rate_of_return > 0 and min_rate_of_return < 1
        assert margin_of_safety > 0 and margin_of_safety < 1

        target_ten_year_eps: float = eps_ttm

        for year in range(2, 11):
            target_ten_year_eps *= (1 + growth_rate)

        target_ten_year_share_price: float = target_ten_year_eps * pe_ratio
        target_share_price: float = target_ten_year_share_price

        for year in range(2, 11):
            target_share_price /= (1 + growth_rate)

        return target_share_price / (1 + margin_of_safety)

    def valuate(self, symbol: str, company_name: str) -> ValuationResult:
        '''Valuate a given asset.'''

        symbol_summary_url = f'https://finviz.com/quote.ashx?t={symbol}'
        symbol_summary_html = self.html_data_access.get_page(url=symbol_summary_url)

        eps_ttm: float = float(symbol_summary_html.find(text='EPS (ttm)')
                                                            .find_next(class_='snapshot-td2')
                                                            .text)
        eps_five_years: float = float(symbol_summary_html
                                        .find(text='EPS next 5Y')
                                        .find_next(class_='snapshot-td2')
                                        .text
                                        .replace('%', '')) / 100

        pe_ratio: float = float(symbol_summary_html
                                    .find(text='P/E')
                                    .find_next(class_='snapshot-td2')
                                    .text)
        forward_pe_ratio: float = float(symbol_summary_html
                                            .find(text='Forward P/E')
                                            .find_next(class_='snapshot-td2')
                                            .text)
        avg_pe_ratio: float = (pe_ratio + forward_pe_ratio) / 2
        current_price: float = float(symbol_summary_html
                                        .find(text='Price')
                                        .find_next(class_='snapshot-td2')
                                        .text)

        annual_dividend_percentage: float = None
        annual_dividend_percentage_str = (symbol_summary_html
                                            .find(text='Dividend %')
                                            .find_next(class_='snapshot-td2')
                                            .text
                                            .split('%')[0])

        if '-' not in annual_dividend_percentage_str:
            annual_dividend_percentage = float(annual_dividend_percentage_str)

        print(f'EPS: {eps_ttm}, EPS Next 5 Years: {eps_five_years}%')
        print(f'P/E Ratio: {avg_pe_ratio}, Current Price: $ {current_price}')

        intrinsic_value: float = self.__determine_intrinsic_value__(eps_ttm=eps_ttm,
                            growth_rate=eps_five_years,
                            pe_ratio=avg_pe_ratio,
                            margin_of_safety=0.3)

        print(f'Intrinsic Value: $ {intrinsic_value} vs. Current Price: $ {current_price}')

        return ValuationResult(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            valuation_price=intrinsic_value,
            annual_dividend_percentage=annual_dividend_percentage
        )
