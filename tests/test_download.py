# -*- coding: utf-8 -*-

import os
# import pytest
import wapor as WaPOR

__author__ = "Quan Pan"
__copyright__ = "Quan Pan"
__license__ = "apache"


def test_download():
    print(os.getcwd())

    dir_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data', 'Download'
    )

    latlim = [7.89, 12.4]
    lonlim = [37.95, 43.35]

    # start and end date to download the data
    Startdate = '2009-01-01'
    Enddate = '2009-02-01'

    arg = {'APIToken': 'ae34c8743c4dc4b3c32d26501fcef18b0cc47464'
                       'baaa87cceb1b10d5ee1096ba03ab36196d29fe07',
           'Dir': dir_path,
           'Startdate': Startdate, 'Enddate': Enddate,
           'latlim': latlim, 'lonlim': lonlim,
           'version': 2, 'level': 1}

    print('\n===== WaPOR.AET =====')
    WaPOR.AET_dekadal(**arg)
    WaPOR.AET_monthly(**arg)
    WaPOR.AET_yearly(**arg)

    print('\n===== WaPOR.I =====')
    WaPOR.I_yearly(**arg)

    print('\n===== WaPOR.LCC =====')
    WaPOR.LCC_yearly(**arg)

    print('\n===== WaPOR.NPP =====')
    WaPOR.NPP_dekadal(**arg)

    print('\n===== WaPOR.PCP =====')
    WaPOR.PCP_daily(**arg)
    WaPOR.PCP_monthly(**arg)
    WaPOR.PCP_yearly(**arg)

    print('\n===== WaPOR.RET =====')
    WaPOR.RET_monthly(**arg)
    WaPOR.RET_yearly(**arg)

    assert True
    # with pytest.raises(AssertionError):
    #     fib(-10)
