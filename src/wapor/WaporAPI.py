# -*- coding: utf-8 -*-
"""
Authors: Bich Tran
         IHE Delft 2019
Contact: b.tran@un-ihe.org

`FAO WaPOR GIS Manager APPI <https://io.apps.fao.org/gismgr/api/v1/swagger-ui.html>`_
"""
import requests
import time
import datetime
import json
import pandas as pd

TIME_SLEEP_SECOND = 2


class __WaPOR_API_class(object):
    """WaPOR API Class

    API Docs
    - `sign_in <https://io.apps.fao.org/gismgr/api/v1/iam/sign-in/>`_
    - `refresh <https://io.apps.fao.org/gismgr/api/v1/iam/token>`_
    - `catalog <https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/>`_
    - `download <https://io.apps.fao.org/gismgr/api/v1/download/>`_
    - `query <https://io.apps.fao.org/gismgr/api/v1/query/>`_
    - `jobs <https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/WAPOR/jobs/`_

    Parameters
    ----------
    APIToken: str
        Input WaPOR API token.
    print_job: bool
        Print job details, default True.
    """

    def __init__(self, APIToken='', print_job=True):
        """
        """
        if APIToken == '':
            raise ValueError('APIToken must be provided!')

        self.print_job = print_job
        self.version = 1
        self.workspaces = {
            1: 'WAPOR',
            2: 'WAPOR_2'
        }

        # self.AccessToken = ''
        # self.RefreshToken = ''
        # self.time = {
        #     'start': datetime.datetime.now().timestamp(),
        #     'now': datetime.datetime.now().timestamp(),
        #     'expire': 0
        # }

        self.token = {
            'API': '',
            'Access': '',
            'Refresh': '',
            'time': {
                'start': datetime.datetime.now().timestamp(),
                'now': datetime.datetime.now().timestamp(),
                'expire': 0
            },
        }

        self.path = {
            'catalog': 'https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/',
            'sign_in': 'https://io.apps.fao.org/gismgr/api/v1/iam/sign-in/',
            'refresh': 'https://io.apps.fao.org/gismgr/api/v1/iam/token',
            'download': 'https://io.apps.fao.org/gismgr/api/v1/download/',
            'query': 'https://io.apps.fao.org/gismgr/api/v1/query/',
            'jobs': 'https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/WAPOR/jobs/'
        }

        # Dynamic assigned in the functions
        self.wkspaces = None
        
        self.catalog = None

        self.locationsTable = None
        self.list_countries = None
        self.list_basins = None

        # Initiate Token
        self.getInitToken(APIToken)

    def getInitToken(self, APIToken):
        '''Initiate AccessToken and RefreshToken
        '''
        print('WaPOR: Loading sign-in...')

        try:
            Token = self._query_accessToken(APIToken)
        except BaseException:
            print(
                'ERROR: The data with specified level version is not available in this version')
        else:
            self.token = {
                'API': APIToken,
                'Access': Token['accessToken'],
                'Refresh': Token['refreshToken'],
                'time': {
                    'expire': Token['expiresIn'],
                    'start': datetime.datetime.now().timestamp(),
                    'now': datetime.datetime.now().timestamp()
                },
            }

    def getCheckToken(self):
        '''Check AccessToken expires, and refresh token
        '''
        print('WaPOR: Checking token...')

        APIToken = self.token['API']
        RefToken = self.token['Refresh']
        dt_start = self.token['time']['start']
        dt_expire = self.token['time']['expire']

        dt_now = datetime.datetime.now().timestamp()
        if dt_now - dt_start > dt_expire:
            try:
                Token = self._query_refreshToken(RefToken)
            except BaseException:
                raise('ERROR: The data with specified level version is not available in this version')
            else:
                self.token = {
                    'API': APIToken,
                    'Access': Token['accessToken'],
                    'Refresh': Token['refreshToken'],
                    'time': {
                        'expire': Token['expiresIn'],
                        'start': dt_now,
                        'now': dt_now
                    },
                }
            finally:
                print('Access Token (new) is:', self.token['Access'])

    def getWorkspaces(self):
        '''Get workspace
        '''
        print('WaPOR: Loading workspace...')

        try:
            df = self._query_workspaces()
        except BaseException:
            print(
                'ERROR: The data with specified level version is not available in this version')
        self.wkspaces = df
        return self.wkspaces

    def _query_workspaces(self):
        print('WaPOR:   _query_workspaces')

        base_url = '{0}?overview=false&paged=false&sort=code'
        request_url = base_url.format(
            self.path['catalog'])

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getCatalog(self, level=None, cubeInfo=True):
        '''Get catalog from workspace
        '''
        print('WaPOR: Loading catalog...')

        try:
            df = self._query_catalog(level)
        except BaseException:
            print(
                'ERROR: The data with specified level version is not available in this version')
        if cubeInfo:
            cubes_measure = []
            cubes_dimension = []
            for cube_code in df['code'].values:
                cubes_measure.append(self._query_cubeMeasures(cube_code,
                                                              version=self.version))
                cubes_dimension.append(self._query_cubeDimensions(cube_code,
                                                                  version=self.version))
            df['measure'] = cubes_measure
            df['dimension'] = cubes_dimension
        self.catalog = df
        return self.catalog

    def _query_catalog(self, level=None):
        print('WaPOR:   _query_catalog')

        if level is None:
            self.version = 2
            base_url = '{0}{1}/cubes?overview=false&paged=false'
            request_url = base_url.format(
                self.path['catalog'],
                self.workspaces[self.version])
        else:
            self.version = level
            base_url = '{0}{1}/cubes?overview=false&paged=false&tags=L{2}'
            request_url = base_url.format(
                self.path['catalog'],
                self.workspaces[self.version],
                level)

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()

            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    df = pd.DataFrame.from_dict(resp, orient='columns')
                    return df
                    # return df.sort_values(['code'], ascending=[True])
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

#    def _query_cubeInfo(self,cube_code):
#        request_url = r'{0}{1}/cubes/{2}?overview=false'.format(self.path['catalog'],
#        self.workspaces[self.version],cube_code)
#        resp = requests.get(request_url)
#        try:
#            meta_data_items = resp.json()['response']
#            cube_info=meta_data_items #['additionalInfo']
#        except:
#            cube_info=None
#        return cube_info

    def getCubeInfo(self, cube_code):
        '''Get cube info
        '''
        print('WaPOR: Loading "{c_code}" info...'.format(c_code=cube_code))

        try:
            catalog = self.catalog
            if 'measure' not in catalog.columns:
                catalog = self.getCatalog(cubeInfo=True)
        except BaseException:
            catalog = self.getCatalog(cubeInfo=True)

        try:
            cube_info = catalog.loc[catalog['code'] == cube_code].to_dict('records')[0]
            return cube_info
        except BaseException:
            print('ERROR: Data for specified cube code and version is not available')

    def _query_cubeMeasures(self, cube_code, version=1):
        print('WaPOR:   _query_cubeMeasures')

        base_url = '{0}{1}/cubes/{2}/measures?overview=false&paged=false'
        request_url = base_url.format(
            self.path['catalog'],
            self.workspaces[self.version],
            cube_code)

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()

            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    return resp[0]
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def _query_cubeDimensions(self, cube_code, version = 1):
        print('WaPOR:   _query_cubeDimensions')

        base_url = '{0}{1}/cubes/{2}/dimensions?overview=false&paged=false'
        request_url=base_url.format(
            self.path['catalog'],
            self.workspaces[self.version],
            cube_code)

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def _query_accessToken(self, APIToken):
        print('WaPOR:   _query_accessToken')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['sign_in'])

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.post(
                request_url,
                headers = {
                    'X-GISMGR-API-KEY': APIToken})
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def _query_refreshToken(self, RefreshToken):
        print('WaPOR:   _query_refreshToken')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['refresh'])

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.post(
                request_url,
                params = {
                    'grandType': 'refresh_token',
                    'refreshToken': RefreshToken})
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getAvailData(self, cube_code, time_range = '2009-01-01,2018-12-31',
                     location = [], season = [], stage = []):
        '''Get Available Data

        cube_code: str
            ex. 'L2_CTY_PHE_S'
        time_range: str
            ex. '2009-01-01,2018-12-31'
        location: list of strings
            default: empty list, return all available locations
            ex. ['ETH']
        season: list of strings
            default: empty list, return all available seasons
            ex. ['S1']
        stage: list of strings
            default: empty list, return all available stages
            ex. ['EOS','SOS']
        '''
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            cube_info = self.getCubeInfo(cube_code)
            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']
        except BaseException:
            print('ERROR: Cannot get cube info')

        print('WaPOR: Loading "{c_code}" data...'.format(c_code=cube_code))

        dims_ls=[]
        columns_codes=['MEASURES']
        rows_codes=[]
        try:
            for dims in cube_dimensions:
                if dims['type'] == 'TIME':  # get time dims
                    time_dims_code=dims['code']
                    df_time=self._query_dimensionsMembers(cube_code, time_dims_code)

                    time_dims={
                        "code": time_dims_code,
                        "range": '[{0})'.format(time_range)
                    }
                    dims_ls.append(time_dims)
                    rows_codes.append(time_dims_code)
                if dims['type'] == 'WHAT':
                    dims_code = dims['code']
                    df_dims = self._query_dimensionsMembers(cube_code, dims_code)

                    members_ls = [row['code'] for i, row in df_dims.iterrows()]
                    if (dims_code == 'COUNTRY' or dims_code == 'BASIN'):
                        if location:
                            members_ls = location
                    if (dims_code == 'SEASON'):
                        if season:
                            members_ls = season
                    if (dims_code == 'STAGE'):
                        if stage:
                            members_ls = stage

                    what_dims = {
                        "code": dims['code'],
                        "values": members_ls
                    }
                    dims_ls.append(what_dims)
                    rows_codes.append(dims['code'])

            df = self._query_availData(cube_code, cube_measure_code,
                                       dims_ls, columns_codes, rows_codes)
        except BaseException:
            print('ERROR:Cannot get list of available data')
            return None
        
        # sorted df
        keys = rows_codes + ['raster_id', 'bbox', 'time_code']
        df_dict = {i: [] for i in keys}
        for irow, row in df.iterrows():
            for i in range(len(row) - 1):
                if row[i]['type'] == 'ROW_HEADER':
                    key_info = row[i]['value']

                    df_dict[keys[i]].append(key_info)
                    if keys[i] == time_dims_code:
                        time_info = df_time.loc[df_time['caption'] == key_info].to_dict(
                            orient='records')
                        df_dict['time_code'].append(time_info[0]['code'])
                if row[i]['type'] == 'DATA_CELL':
                    raster_info = row[i]['metadata']['raster']

                    df_dict['raster_id'].append(raster_info['id'])
                    df_dict['bbox'].append(raster_info['bbox'])
        df_sorted = pd.DataFrame.from_dict(df_dict)
        return df_sorted

    def _query_availData(self, cube_code, measure_code,
                         dims_ls, columns_codes, rows_codes):
        print('WaPOR:   _query_availData')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        query_load = {
            "type": "MDAQuery_Table",
            "params": {
                "properties": {
                    "metadata": True,
                    "paged": False,
                },
                "cube": {
                    "workspaceCode": self.workspaces[self.version],
                    "code": cube_code,
                    "language": "en"
                },
                "dimensions": dims_ls,
                "measures": [measure_code],
                "projection": {
                    "columns": columns_codes,
                    "rows": rows_codes
                }
            }
        }

        # requests
        try:
            resq = requests.post(
                request_url,
                json=query_load)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    try:
                        df = pd.DataFrame(resp['items'])
                        # df = pd.DataFrame.from_dict(resp, orient='columns')
                        return df
                    except BaseException:
                        print('ERROR: Cannot get list of available data')
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def _query_dimensionsMembers(self, cube_code, dims_code):
        print('WaPOR:   _query_dimensionsMembers')

        base_url = '{0}{1}/cubes/{2}/dimensions/{3}/members?overview=false&paged=false'
        request_url = base_url.format(
            self.path['catalog'],
            self.workspaces[self.version],
            cube_code,
            dims_code)

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    try:
                        df = pd.DataFrame.from_dict(resp, orient='columns')
                        return df
                    except BaseException:
                        print('ERROR: Cannot get dimensions Members')
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getLocations(self, level=None):
        '''Get Locations

        level: int
            2 or 3
        '''
        print('WaPOR: Loading locations...')

        try:
            df_loc = self.locationsTable
        except BaseException:
            df_loc = self._query_locations()
            df_loc = self.locationsTable

        if level is not None:
            df_loc = df_loc.loc[df_loc["l{0}".format(level)] == True]
        return df_loc

    def _query_locations(self):
        print('WaPOR:   _query_locations')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        request_json = {
            "type": "TableQuery_GetList_1",
            "params": {
                "table": {
                    "workspaceCode": self.workspaces[self.version],
                    "code": "LOCATION"
                },
                "properties": {
                    "paged": False
                },
                "sort": [
                    {
                        "columnName": "name"
                    }
                ]
            }
        }

        # requests
        try:
            resq = requests.post(
                request_url,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    df_loc = pd.DataFrame.from_dict(resp, orient='columns')

                    self.locationsTable = df_loc
                    df_CTY = df_loc.loc[(df_loc["l2"] == True) &
                                        (df_loc["type"] == 'COUNTRY')]
                    df_BAS = df_loc.loc[(df_loc["l2"] == True) &
                                        (df_loc["type"] == 'BASIN')]
                    self.list_countries = [rows['code']
                                        for index, rows in df_CTY.iterrows()]
                    self.list_basins = [rows['code']
                                        for index, rows in df_BAS.iterrows()]
                    return df_loc
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getRasterUrl(self, cube_code, rasterId, APIToken):
        '''Get Raster Url
        '''
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        print('WaPOR: Loading "{c_code}" url...'.format(c_code=cube_code))

        download_url = self._query_rasterUrl(cube_code, rasterId, AccessToken)
        return download_url

    def _query_rasterUrl(self, cube_code, rasterId, AccessToken):
        print('WaPOR:   _query_rasterUrl')

        base_url = '{0}{1}'
        request_url = base_url.format(
            self.path['download'],
            self.workspaces[self.version])

        if self.print_job:
            print(request_url)

        request_headers = {
            'Authorization': "Bearer " + AccessToken}
        request_params = {
            'language': 'en',
            'requestType': 'mapset_raster',
            'cubeCode': cube_code,
            'rasterId': rasterId}

        # requests
        try:
            resq = requests.get(
                request_url, 
                headers=request_headers,
                params=request_params)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']

                if resq_json['message'] == 'OK':
                    expiry_date = datetime.datetime.now() \
                        + datetime.timedelta(seconds=int(resp['expiresIn']))

                    output = {
                        'url': resp['downloadUrl'],
                        'expiry_datetime': expiry_date}
                    return output
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def _query_jobOutput(self, job_url):
        print('WaPOR:   _query_jobOutput')

        request_url = job_url

        ijob = 0
        contiue = True
        if self.print_job:
            print(request_url)
        
        while contiue:
            # requests
            try:
                resq = requests.get(
                    request_url)
                resq.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print("Http Error:", err)
            except requests.exceptions.ConnectionError as err:
                print("Error Connecting:", err)
            except requests.exceptions.Timeout as err:
                print("Timeout Error:", err)
            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)
                # sys.exit(1)
            else:
                resq_json = resq.json()
                try:
                    resp = resq_json['response']

                    if resq_json['message'] == 'OK':
                        jobType = resp['type']

                        if self.print_job:
                            print('  {i:d} {s}'.format(i=ijob, s=resp['status']))
                
                        if resp['status'] == 'COMPLETED':
                            contiue = False
                            if jobType == 'CROP RASTER':
                                output = resp['output']['downloadUrl']
                            elif jobType == 'AREA STATS':
                                results = resp['output']
                                output = pd.DataFrame(results['items'], columns=results['header'])
                            else:
                                print('ERROR: Invalid jobType')
                            return output
                        if resp['status'] == 'COMPLETED WITH ERRORS':
                            contiue = False
                            print(resp['log'])
                        else:
                            # 'WAITING' or 'RUNNING'
                            time.sleep(TIME_SLEEP_SECOND)
                    else:
                        print(resq_json['message'])
                except BaseException:
                    print('Error: Cannot get {url}'.format(url=request_url))

            ijob += 1

    def getCropRasterURL(self, bbox, cube_code,
                         time_code, rasterId, APIToken):
        '''Get Crop Raster Url

        Do need Authorization

        bbox: str
            latitude and longitude
            [xmin,ymin,xmax,ymax]
        '''
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            cube_info = self.getCubeInfo(cube_code)
            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']

            for cube_dimension in cube_dimensions:
                if cube_dimension['type'] == 'TIME':
                    cube_dimension_code = cube_dimension['code']
        except BaseException:
            print('ERROR: Cannot get cube info')

        print('WaPOR: Loading "{c_code}" url...'.format(c_code=cube_code))

        # Create Polygon
        xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
        Polygon = [
            [xmin, ymin],
            [xmin, ymax],
            [xmax, ymax],
            [xmax, ymin],
            [xmin, ymin]
        ]

        # Query payload
        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        request_headers = {
            'Authorization': 'Bearer {0}'.format(AccessToken)
        }
        request_json = {
            "type": "CropRaster",
            "params": {
                "properties": {
                    "outputFileName": "{0}.tif".format(rasterId),
                    "cutline": True,
                    "tiled": True,
                    "compressed": True,
                    "overviews": True
                },
                "cube": {
                    "code": cube_code,
                    "workspaceCode": self.workspaces[self.version],
                    "language": "en"
                },
                "dimensions": [
                    {
                        "code": cube_dimension_code,
                        "values": [
                            time_code
                        ]
                    }
                ],
                "measures": [
                    cube_measure_code
                ],
                "shape": {
                    "type": "Polygon",
                    "properties": {
                        "name": "epsg:4326"  # latlon projection
                    },
                    "coordinates": [
                        Polygon
                    ]
                }
            }
        }

        # requests
        try:
            resq = requests.post(
                request_url,
                headers=request_headers,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        job_url = resp['links'][0]['href']

                        if self.print_job:
                            print('WaPOR: Downloading "{c_code}" "{t}"...'.format(
                                c_code=cube_code, t=resp['type']))

                        output = self._query_jobOutput(job_url)
                        return output
                    except BaseException:
                        print('Error: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getAreaTimeseries(self, shapefile_fh, cube_code, APIToken,
                          time_range="2009-01-01,2018-12-31"):
        '''Get Area Timeseries

        Do need Authorization

        shapefile_fh: str
                    "E:/Area.shp"
        time_range: str
                    "YYYY-MM-DD,YYYY-MM-DD"
        '''
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            cube_info = self.getCubeInfo(cube_code)
            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']

            for cube_dimension in cube_dimensions:
                if cube_dimension['type'] == 'TIME':
                    cube_dimension_code = cube_dimension['code']
        except BaseException:
            print('ERROR: Cannot get cube info')

        print('WaPOR: Loading "{c_code}" area timeseries...'.format(c_code=cube_code))

        # get shapefile info
        import ogr
        dts = ogr.Open(shapefile_fh)
        layer = dts.GetLayer()
        epsg_code = layer.GetSpatialRef().GetAuthorityCode(None)
        shape = layer.GetFeature(0).ExportToJson(as_object=True)['geometry']
        shape["properties"] = {"name": "EPSG:{0}".format(epsg_code)}

        # query load
        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        request_headers = {
            'Authorization': 'Bearer {0}'.format(AccessToken)
        }
        request_json = {
            "type": "AreaStatsTimeSeries",
            "params": {
                "cube": {
                    "code": cube_code,
                    "workspaceCode": self.workspaces[self.version],
                    "language": "en"
                },
                "dimensions": [
                    {
                        "code": cube_dimension_code,
                        "range": "[{0})".format(time_range)
                    }
                ],
                "measures": [
                    cube_measure_code
                ],
                "shape": shape
            }
        }

        # requests
        try:
            resq = requests.post(
                request_url,
                headers=request_headers,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        job_url = resp['links'][0]['href']

                        if self.print_job:
                            print('WaPOR: Downloading "{c_code}" "{t}"...'.format(
                                c_code=cube_code, t=resp['type']))

                        output = self._query_jobOutput(job_url)
                        return output
                    except BaseException:
                        print('Error: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))

    def getPixelTimeseries(self, pixelCoordinates, cube_code,
                           time_range="2009-01-01,2018-12-31"):
        '''Get Pixel Timeseries

        Don't need Authorization

        pixelCoordinates: list
            [37.95883206252312, 7.89534]
        '''
        # get cube info
        cube_info = self.getCubeInfo(cube_code)
        cube_measure_code = cube_info['measure']['code']
        for dims in cube_info['dimension']:
            if dims['type'] == 'TIME':
                cube_dimension_code = dims['code']

        print('WaPOR: Loading "{c_code}" point timeseries...'.format(c_code=cube_code))

        # query load
        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        # request_headers = {
        #     'Authorization': 'Bearer {0}'.format(AccessToken)
        # }
        request_json = {
            "type": "PixelTimeSeries",
            "params": {
                "cube": {
                    "code": cube_code,
                    "workspaceCode": self.workspaces[self.version],
                    "language": "en"
                },
                "dimensions": [
                    {
                        "code": cube_dimension_code,
                        "range": "[{0})".format(time_range)
                    }
                ],
                "measures": [
                    cube_measure_code
                ],
                "point": {
                    "crs": "EPSG:4326",  # latlon projection
                    "x": pixelCoordinates[0],
                    "y": pixelCoordinates[1]
                }
            }
        }

        # requests
        try:
            resq = requests.post(
                request_url,
                # headers=request_headers,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            print("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            # sys.exit(1)
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        df = pd.DataFrame(resp['items'], columns=resp['header'])
                        return df
                    except BaseException:
                        print('Error: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('Error: Cannot get {url}'.format(url=request_url))
