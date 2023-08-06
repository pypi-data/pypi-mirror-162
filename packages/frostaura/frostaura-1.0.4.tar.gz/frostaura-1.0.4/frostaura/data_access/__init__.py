'''A convenience importing mechanism for all data access components.'''

from .html_data_access import IHtmlDataAccess, HtmlDataAccess
from .personal_asset_data_access import (IPersonalAssetDataAccess,
                                         EasyEquitiesPersonalAssetDataAccess)
from .public_asset_data_access import IPublicAssetDataAccess, YahooFinanceDataAccess
from .resources_data_access import IResourcesDataAccess, EmbeddedResourcesDataAccess
