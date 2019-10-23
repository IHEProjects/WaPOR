# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:25:33 2019

@author: ntr002
"""
import os
from datetime import datetime
import requests

import numpy as np

import download as WaPOR
try:
    from .download import GIS_functions as gis
except ImportError:
    from download import GIS_functions as gis


def main(Dir, Startdate='2009-01-01', Enddate='2018-12-31',
         latlim=[-40.05, 40.05], lonlim=[-30.5, 65.05], level=1,
         version=2, Waitbar=1):
    """
    This function downloads yearly WAPOR AETI data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -40.05 and 40.05)
    lonlim -- [xmin, xmax] (values must be between -30.05 and 65.05)
    """
    print('\nDownload yearly WaPOR Land Cover Class data for the period %s till %s' % (
        Startdate, Enddate))

    # Download data
    # WaPOR.API.version = version
    # catalog = WaPOR.API.getCatalog(version, level, True)

    bbox = [lonlim[0], latlim[0], lonlim[1], latlim[1]]

    if level == 1:
        cube_code = 'L1_LCC_A'
    elif level == 2:
        cube_code = 'L2_LCC_A'
    else:
        print('This module only support level 1 and level 2 data. For higher level, use WaPORAPI module')

    try:
        cube_info = WaPOR.API.getCubeInfo(
            cube_code, version=version, level=level)
        multiplier = cube_info['measure']['multiplier']
    except:
        print('ERROR: Cannot get cube info. Check if WaPOR version has cube %s' % (
            cube_code))
        return None

    time_range = '{0},{1}'.format(Startdate, Enddate)

    try:
        df_avail = WaPOR.API.getAvailData(
            cube_code, time_range=time_range, version=version, level=level)
    except:
        print('ERROR: cannot get list of available data')
        return None

    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(df_avail)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(
    #         amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

    Dir = os.path.join(Dir, cube_code)
    if not os.path.exists(Dir):
        os.makedirs(Dir)

    for index, row in df_avail.iterrows():
        download_url = WaPOR.API.getCropRasterURL(bbox,
                                                  cube_code,
                                                  row['time_code'],
                                                  row['raster_id'],
                                                  WaPOR.API.token['Access'])

        Date = datetime.strptime(row['YEAR'], '%Y')

        filename = 'LCC_WAPOR.v2.0_level%s_annually_%s.tif' % (
            level, Date.strftime('%Y'))
        outfilename = os.path.join(Dir, filename)

        download_file = os.path.join(Dir, '{0}.tif'.format(row['raster_id']))

        # Download raster file
        resp = requests.get(download_url)
        open(download_file, 'wb').write(resp.content)

        driver, NDV, xsize, ysize, GeoT, Projection = gis.GetGeoInfo(
            download_file)

        # Array = gis.OpenAsArray(download_file, nan_values=True)
        Array = gis.OpenAsArray(download_file, nan_values=False)
        CorrectedArray = Array * multiplier

        gis.CreateGeoTiff(outfilename, CorrectedArray,
                          driver, NDV, xsize, ysize, GeoT, Projection)
        os.remove(download_file)

        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount,
        #                                 prefix='Progress:',
        #                                 suffix='Complete',
        #                                 length=50)


if __name__ == "__main__":
    dir_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../', '../', 'tests', 'data'
    )
    main(Dir=dir_path)
