# -*- coding: utf-8 -*-
"""
Description:
This script collects WaPOR data from the WaPOR API.
The data is available between 2009-01-01 till present.

Example:
from watools.Collect import WaPOR
WaPOR.PCP_monthly(Dir='C:/Temp/', Startdate='2009-02-24', Enddate='2009-03-09',
                     latlim=[50,54], lonlim=[3,7])
WaPOR.AETI_monthly(Dir='C:/Temp/', Startdate='2009-02-24', Enddate='2009-03-09',
                     latlim=[50,54], lonlim=[3,7])
"""
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'WaporIHE'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

from .download import API as API

from .AET_dekadal import main as AET_dekadal
from .AET_monthly import main as AET_monthly
from .AET_yearly import main as AET_yearly

from .I_yearly import main as I_yearly

from .LCC_yearly import main as LCC_yearly

from .NPP_dekadal import main as NPP_dekadal

from .PCP_daily import main as PCP_daily
from .PCP_monthly import main as PCP_monthly
from .PCP_yearly import main as PCP_yearly

from .RET_monthly import main as RET_monthly
from .RET_yearly import main as RET_yearly

__all__ = [
    'API',
    'AET_dekadal', 'AET_monthly', 'AET_yearly',
    'I_yearly',
    'LCC_yearly',
    'NPP_dekadal',
    'PCP_daily', 'PCP_monthly', 'PCP_yearly',
    'RET_monthly', 'RET_yearly',
]
