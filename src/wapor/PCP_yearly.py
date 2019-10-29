# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:25:33 2019

@author: ntr002
"""
import os
from datetime import datetime
import psutil
import requests

import numpy as np

import download as WaPOR

try:
    from .download import GIS_functions as gis
except ImportError:
    from download import GIS_functions as gis


def main(Dir, Startdate='2009-01-01', Enddate='2018-12-31',
         latlim=[-40.05, 40.05], lonlim=[-30.5, 65.05],
         version=2, level=1, Waitbar=1):
    """
    This function downloads dekadal WaPOR Precipitation data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -40.05 and 40.05)
    lonlim -- [xmin, xmax] (values must be between -30.05 and 65.05)
    """
    print('WaPOR PCP: Download dekadal WaPOR Precipitation data'
          ' for the period %s till %s' % (Startdate, Enddate))
    checkMemory('Start')

    # Download data
    # WaPOR.API.version = version
    # catalog = WaPOR.API.getCatalog()

    bbox = [lonlim[0], latlim[0], lonlim[1], latlim[1]]

    if level == 1:
        cube_code = 'L1_PCP_A'
    else:
        raise Exception('WaPOR PCP ERROR: This module'
                        ' only support level 1 data.'
                        ' For higher level, use WaPORAPI module')

    try:
        cube_info = WaPOR.API.getCubeInfo(
            cube_code, version=version, level=level)
        multiplier = cube_info['measure']['multiplier']
    except BaseException:
        raise Exception('WaPOR PCP ERROR: Cannot get cube info.'
                        ' Check if WaPOR version has cube %s' % (cube_code))
    finally:
        cube_info = None

    time_range = '{0},{1}'.format(Startdate, Enddate)

    df_avail = WaPOR.API.getAvailData(
        cube_code, time_range=time_range, version=version, level=level)
    # try:
    # except:
    #     print('ERROR: cannot get list of available data')
    #     return None

    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(df_avail)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
    #                                 suffix='Complete', length=50)

    Dir = os.path.join(Dir, cube_code)
    if not os.path.exists(Dir):
        os.makedirs(Dir)

    for index, row in df_avail.iterrows():
        print('WaPOR PCP: ----- {} -----'.format(index))
        checkMemory('{} AvailData loop start'.format(index))

        # Download raster file name
        download_file = os.path.join(Dir, '{0}.tif'.format(row['raster_id']))
        print('WaPOR PCP: Downloaded file :', download_file)

        # Local raster file name
        filename = 'PCP_WAPOR.v%s_level%s_mm-annually-1_%s.tif' % (
            version, level,
            datetime.strptime(row['YEAR'], '%Y').strftime('%Y'))
        outfilename = os.path.join(Dir, filename)
        print('WaPOR PCP: Local      file :', outfilename)

        # Downloading raster file
        checkMemory('{} Downloading start'.format(index))
        resp = requests.get(WaPOR.API.getCropRasterURL(bbox,
                                                       cube_code,
                                                       row['time_code'],
                                                       row['raster_id'],
                                                       WaPOR.API.token['Access']))
        with open(download_file, 'wb') as fp:
            fp.write(resp.content)
        resp = None
        checkMemory('{} Downloading end'.format(index))


        # GDAL download_file * multiplier => outfilename
        driver, NDV, xsize, ysize, GeoT, Projection = gis.GetGeoInfo(
            download_file)

        Array = gis.OpenAsArray(download_file, nan_values=True)
        print('WaPOR PCP: Array         : {t}'.format(
            t=Array.dtype.name))

        checkMemory('{} Multiply start'.format(index))
        NDV = np.float32(NDV)
        multiplier = np.float32(multiplier)
        print('WaPOR PCP: NDV           : {v} {t}'.format(
            v=NDV, t=NDV.dtype.name))
        print('WaPOR PCP: multiplier    : {v} {t}'.format(
            v=multiplier, t=multiplier.dtype.name))

        NDV = NDV * multiplier
        Array = Array * multiplier
        print('WaPOR PCP: NDV           : {v} {t}'.format(
            v=NDV, t=NDV.dtype.name))
        print('WaPOR PCP: Array         : {t}'.format(
            t=Array.dtype.name))
        checkMemory('{} Multiply end'.format(index))

        gis.CreateGeoTiff(outfilename, Array,
                          driver, NDV, xsize, ysize, GeoT, Projection)

        Array = None
        checkMemory('{} AvailData loop end'.format(index))

        # Remove downloaded raster file
        try:
            os.remove(download_file)
        except OSError as err:
            # if failed, report it back to the user
            print("WaPOR PCP ERROR: %s - %s." % (err.filename, err.strerror))

        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount,
        #                                 prefix='Progress:',
        #                                 suffix='Complete',
        #                                 length=50)
    checkMemory('End')


def checkMemory(txt=''):
    mem = psutil.virtual_memory()
    print('WaPOR PCP: > Memory available      : {t} {v:.2f} MB'.format(
        t=txt, v=mem.available / 1024 / 1024))


if __name__ == "__main__":
    dir_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../', '../', 'tests', 'data', 'Download'
    )
    main(Dir=dir_path, Startdate='2009-01-01', Enddate='2018-12-31',
         #  latlim=[-40.05, 40.05], lonlim=[-30.5, 65.05],
         latlim=[-40.05, 40.05], lonlim=[-30.5, 0.0],
         version=2, level=1)
