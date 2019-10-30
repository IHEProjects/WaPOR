# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 14:16:35 2019

@author: Bert Coerver
"""
import os
import psutil
import numpy as np

import gdal
import osr


def GetGeoInfo(fh, subdataset=0):
    """
    Substract metadata from a geotiff, HDF4 or netCDF file.

    Parameters
    ----------
    fh : str
        Filehandle to file to be scrutinized.
    subdataset : int, optional
        Layer to be used in case of HDF4 or netCDF format, default is 0.

    Returns
    -------
    driver : str
        Driver of the fh.
    NDV : float
        No-data-value of the fh.
    xsize : int
        Amount of pixels in x direction.
    ysize : int
        Amount of pixels in y direction.
    GeoT : list
        List with geotransform values.
    Projection : str
        Projection of fh.
    """
    print('WaPOR GIS: Getting Geo Information...')
    checkMemory('GetGeoInfo Start')

    SourceDS = gdal.Open(fh, gdal.GA_ReadOnly)

    Type = SourceDS.GetDriver().ShortName
    if Type == 'HDF4' or Type == 'netCDF':
        SourceDS = gdal.Open(SourceDS.GetSubDatasets()[subdataset][0])
    driver = gdal.GetDriverByName(Type)

    meta = SourceDS.GetMetadata()

    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize

    GeoT = SourceDS.GetGeoTransform()

    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())

    subNDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    subMeta = SourceDS.GetRasterBand(1).GetMetadata()

    print('WaPOR GIS:   Metadata              : {v}, {t}'.format(
        v=meta, t=type(meta)))
    print('WaPOR GIS:   xsize                 : {v}, {t}'.format(
        v=xsize, t=type(xsize)))
    print('WaPOR GIS:   ysize                 : {v}, {t}'.format(
        v=ysize, t=type(ysize)))
    print('WaPOR GIS:   GeoT                  : {v}, {t}'.format(
        v=GeoT, t=type(GeoT)))
    print('WaPOR GIS:   Projection            : {v}, {t}'.format(
        v=Projection.GetAttrValue('AUTHORITY', 1), t=type(Projection)))

    print('WaPOR GIS:   sub NoDataValue       : {v}, {t}'.format(
        v=subNDV, t=type(subNDV)))
    print('WaPOR GIS:   sub Metadata          : {v}, {t}'.format(
        v=subMeta, t=type(subMeta)))

    SourceDS = None
    checkMemory('GetGeoInfo End')
    return driver, subNDV, xsize, ysize, GeoT, Projection


def OpenAsArray(fh, bandnumber=1, dtype='float32', nan_values=False):
    """
    Open a map as an numpy array.

    Parameters
    ----------
    fh: str
        Filehandle to map to open.
    bandnumber : int, optional
        Band or layer to open as array, default is 1.
    dtype : str, optional
        Datatype of output array, default is 'float32'.
    nan_values : boolean, optional
        Convert he no-data-values into np.nan values, note that dtype needs to
        be a float if True. Default is False.

    Returns
    -------
    Array: :obj:`numpy.ndarray`
        Array with the pixel values.
    """
    print('WaPOR GIS: Opening file...')
    checkMemory('OpenAsArray Start')

    # datatypes = {
    #     "uint8": np.uint8, "int8": np.int8,
    #     "uint16": np.uint16, "int16": np.int16, "Int16": np.int16,
    #     "uint32": np.uint32, "int32": np.int32, "Int32": np.int32,
    #     "float32": np.float32, "float64": np.float64,
    #     "Float32": np.float32, "Float64": np.float64,
    #     "complex64": np.complex64, "complex128": np.complex128,
    #     "Complex64": np.complex64, "Complex128": np.complex128, }

    DataSet = gdal.Open(fh, gdal.GA_ReadOnly)
    checkMemory('OpenAsArray Opened')

    Type = DataSet.GetDriver().ShortName
    if Type == 'HDF4':
        Subdataset = gdal.Open(DataSet.GetSubDatasets()[bandnumber][0])
        NDV = int(Subdataset.GetMetadata()['_FillValue'])
    else:
        Subdataset = DataSet.GetRasterBand(bandnumber)
        NDV = Subdataset.GetNoDataValue()

    print('WaPOR GIS:   Band DataType         : {v}'.format(
        v=Subdataset.DataType))
    print('WaPOR GIS:   Band DataTypeName     : {v}'.format(
        v=gdal.GetDataTypeName(Subdataset.DataType)))
    print('WaPOR GIS:   NoDataValue           : {v}, {t}'.format(
        v=NDV, t=type(NDV)))

    # Array = Subdataset.ReadAsArray().astype(datatypes[dtype])
    Array = Subdataset.ReadAsArray()
    print('WaPOR GIS:   Band Array dtype      : {v} {sp} {sz}'.format(
        v=Array.dtype.name, sp=Array.shape, sz=Array.size))
    checkMemory('OpenAsArray Loaded')

    # if nan_values:
    #     Array[Array == NDV] = np.nan

    DataSet = None
    checkMemory('OpenAsArray End')
    return Array


def CreateGeoTiff(fh, Array, driver, NDV, xsize, ysize, GeoT,
                  Projection, explicit=True, compress=None):
    """
    Creates a geotiff from a numpy array.

    Parameters
    ----------
    fh : str
        Filehandle for output.
    Array: ndarray
        Array to convert to geotiff.
    driver : str
        Driver of the fh.
    NDV : float
        No-data-value of the fh.
    xsize : int
        Amount of pixels in x direction.
    ysize : int
        Amount of pixels in y direction.
    GeoT : list
        List with geotransform values.
    Projection : str
        Projection of fh.
    """
    print('WaPOR GIS: Creating tiff file...')
    checkMemory('CreateGeoTiff Start')

    print('WaPOR GIS:   Array DataTypeName    : {t}'.format(
        t=Array.dtype.name))
    print('WaPOR GIS:   No Data Value         : {v} {t}'.format(
        v=NDV, t=NDV.dtype.name))

    datatypes = {
        "uint8": 1, "int8": 1,
        "uint16": 2, "int16": 3, "Int16": 3,
        "uint32": 4, "int32": 5, "Int32": 5,
        "float32": 6, "float64": 7,
        "Float32": 6, "Float64": 7,
        "complex64": 10, "complex128": 11,
        "Complex64": 10, "Complex128": 11, }

    if compress is not None:
        DataSet = driver.Create(
            fh, xsize, ysize, 1,
            datatypes[Array.dtype.name],
            [
                'COMPRESS={0}'.format(compress),
            ])
    else:
        # 'COMPRESS=LZW',
        # 'BIGTIFF=YES',
        DataSet = driver.Create(
            fh, xsize, ysize, 1,
            datatypes[Array.dtype.name],
            [
                'BLOCKXSIZE=256',
                'BLOCKYSIZE=256'
            ])

    # if NDV is None:
    #     NDV = -9999
    #
    # if explicit:
    #     Array[np.isnan(Array)] = NDV

    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())

    DataSet.GetRasterBand(1).SetNoDataValue(float(NDV))
    DataSet.GetRasterBand(1).WriteArray(Array)

    DataSet = None

    # if "nt" not in Array.dtype.name:
    #     Array[Array == NDV] = np.nan

    checkMemory('CreateGeoTiff End')


def MatchProjResNDV(source_file, target_fhs, output_dir,
                    resample='near', dtype='float32', scale=None, ndv_to_zero=False):
    """
    Matches the projection, resolution and no-data-value of a list of target-files
    with a source-file and saves the new maps in output_dir.

    Parameters
    ----------
    source_file : str
        The file to match the projection, resolution and ndv with.
    target_fhs : list
        The files to be reprojected.
    output_dir : str
        Folder to store the output.
    resample : str, optional
        Resampling method to use, default is 'near' (nearest neighbour).
    dtype : str, optional
        Datatype of output, default is 'float32'.
    scale : int, optional
        Multiple all maps with this value, default is None.

    Returns
    -------
    output_files: :obj:`numpy.ndarray`
        Filehandles of the created files.
    """
    print('WaPOR GIS: Matching projection...')

    output_files = np.array([])

    dst_info = gdal.Info(gdal.Open(source_file), format='json')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for target_file in target_fhs:
        folder, fn = os.path.split(target_file)
        output_file = os.path.join(output_dir, fn)

        src_info = gdal.Info(gdal.Open(target_file), format='json')
        gdal.Warp(output_file, target_file, format='GTiff',
                  srcSRS=src_info['coordinateSystem']['wkt'],
                  dstSRS=dst_info['coordinateSystem']['wkt'],
                  srcNodata=src_info['bands'][0]['noDataValue'],
                  dstNodata=dst_info['bands'][0]['noDataValue'],
                  width=dst_info['size'][0],
                  height=dst_info['size'][1],
                  outputBounds=(dst_info['cornerCoordinates']['lowerLeft'][0],
                                dst_info['cornerCoordinates']['lowerLeft'][1],
                                dst_info['cornerCoordinates']['upperRight'][0],
                                dst_info['cornerCoordinates']['upperRight'][1]),
                  outputBoundsSRS=dst_info['coordinateSystem']['wkt'],
                  resampleAlg=resample)

        output_files = np.append(output_files, output_file)

        if not np.any([scale == 1.0, scale is None, scale == 1]):
            driver, NDV, xsize, ysize, GeoT, Projection = GetGeoInfo(
                output_file)
            DATA = OpenAsArray(output_file, nan_values=True) * scale
            CreateGeoTiff(
                output_file,
                DATA,
                driver,
                NDV,
                xsize,
                ysize,
                GeoT,
                Projection)

        if ndv_to_zero:
            driver, NDV, xsize, ysize, GeoT, Projection = GetGeoInfo(
                output_file)
            DATA = OpenAsArray(output_file, nan_values=False)
            DATA[DATA == NDV] = 0.0
            CreateGeoTiff(
                output_file,
                DATA,
                driver,
                NDV,
                xsize,
                ysize,
                GeoT,
                Projection)
    return output_files


def checkMemory(txt=''):
    mem = psutil.virtual_memory()
    print('WaPOR GIS: > Memory available      : {t} {v:.2f} MB'.format(
        t=txt, v=mem.available / 1024 / 1024))
