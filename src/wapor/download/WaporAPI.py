# -*- coding: utf-8 -*-
"""
Authors: Bich Tran
         IHE Delft 2019
Contact: b.tran@un-ihe.org

`FAO WaPOR GIS Manager API <https://io.apps.fao.org/gismgr/api/v1/swagger-ui.html>`_
"""
import requests
import time
import datetime
# import json
import pandas as pd

TIME_EXPIRES_BEFORE_SECOND = 120  # From API expires time is 3600-120sec
# TIME_EXPIRES_BEFORE_SECOND = 600  # From API expires time is 3600-600sec
TIME_SLEEP_SECOND = 2


class WaPOR_API_class(object):
    """WaPOR API Class

    API Docs

    - `sign_in <https://io.apps.fao.org/gismgr/api/v1/iam/sign-in/>`_
    - `refresh <https://io.apps.fao.org/gismgr/api/v1/iam/token>`_
    - `catalog <https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/>`_
    - `download <https://io.apps.fao.org/gismgr/api/v1/download/>`_
    - `query <https://io.apps.fao.org/gismgr/api/v1/query/>`_
    - `jobs <https://io.apps.fao.org/gismgr/api/v1/catalog/workspaces/WAPOR/jobs/>`_

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
            raise ValueError('WaPOR API ERROR: APIToken must be provided!')

        self.print_job = print_job

        self.workspaces = {
            1: 'WAPOR',
            2: 'WAPOR_2'
        }
        self.version = 2
        self.level = None

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
            'catalog': 'https://io.apps.fao.org/gismgr/api/v1/'
                       'catalog/workspaces/',
            'sign_in': 'https://io.apps.fao.org/gismgr/api/v1/'
                       'iam/sign-in/',
            'refresh': 'https://io.apps.fao.org/gismgr/api/v1/'
                       'iam/token',
            'download': 'https://io.apps.fao.org/gismgr/api/v1/'
                        'download/',
            'query': 'https://io.apps.fao.org/gismgr/api/v1/'
                     'query/',
            'jobs': 'https://io.apps.fao.org/gismgr/api/v1/'
                    'catalog/workspaces/WAPOR/jobs/'
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
        """Initiate AccessToken and RefreshToken

        Parameters
        ----------
        APIToken: str
            Input WaPOR API token.
        """
        print('WaPOR API: Loading sign-in...')

        Token = self._query_accessToken(APIToken)
        if Token is None:
            raise Exception(
                'WaPOR API ERROR: The data with specified level version'
                ' is not available in this version')
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

    def _query_accessToken(self, APIToken):
        """Query AccessToken and RefreshToken

        Parameters
        ----------
        APIToken: str
            Input WaPOR API token.
        """
        print('WaPOR API:   _query_accessToken')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['sign_in'])

        if self.print_job:
            print(request_url)

        request_headers = {
            'X-GISMGR-API-KEY': APIToken}

        # requests
        try:
            resq = requests.post(
                request_url,
                headers=request_headers)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getCheckToken(self):
        """Check AccessToken expires, and refresh token
        """
        print('WaPOR API: Checking token...')

        # APIToken = self.token['API']
        RefToken = self.token['Refresh']
        dt_start = self.token['time']['start']
        dt_expire = self.token['time']['expire']

        dt_now = datetime.datetime.now().timestamp()
        if dt_now - dt_start > dt_expire - TIME_EXPIRES_BEFORE_SECOND:
            Token = self._query_refreshToken(RefToken)

            if Token is None:
                raise Exception(
                    'WaPOR API ERROR: The data with specified level version'
                    ' is not available in this version')
            else:
                self.token['Access'] = Token['accessToken']
                self.token['Refresh'] = Token['refreshToken']
                self.token['time']['expire'] = Token['expiresIn']
                self.token['time']['start'] = dt_now
                self.token['time']['now'] = dt_now

    def _query_refreshToken(self, RefreshToken):
        """Query AccessToken expires, and refresh token
        """
        print('WaPOR API:   _query_refreshToken')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['refresh'])

        if self.print_job:
            print(request_url)

        request_json = {
            'grandType': 'refresh_token',
            'refreshToken': RefreshToken}

        # requests
        try:
            resq = requests.post(
                request_url,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getWorkspaces(self):
        """Get workspace
        """
        print('WaPOR API: Loading workspace...')

        df = self._query_workspaces()
        if df is None:
            raise Exception(
                'WaPOR API ERROR: The data with specified level version'
                ' is not available in this version')
        else:
            self.wkspaces = df
            return self.wkspaces

    def _query_workspaces(self):
        """Query workspace
        """
        print('WaPOR API:   _query_workspaces')

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getCatalog(self, version=None, level=None, cubeInfo=True):
        """Get catalog from workspace

        Parameters
        ----------
        version: int, optional
            WaPOR workspace version, default 2.
        level: int, optional
            Data resolution level, default None.
        cubeInfo: bool, optional
            Get cube information, default True.

        Returns
        -------
        catalog: :obj:`pandas.DataFrame`
            Catalog table.
        """
        print('WaPOR API: Loading catalog WaPOR_{v}.L{l}...'.format(v=version, l=level))

        isFound = False

        # if isinstance(version, int) and isinstance(level, int):
        #     print('| int')
        #     if 0 < version < 3 and 0 < level < 4:
        #         print('|  range')
        if version == self.version and level == self.level:
            # print('|   equal')
            if self.catalog is not None:
                # print('|    not None')
                isFound = True

        if isFound:
            df = self.catalog

            print('WaPOR API: Loading catalog WaPOR_{v}.L{l} found.'.format(
                v=version, l=level))
        else:
            df = self._query_catalog(version, level)

            print('WaPOR API: Loading catalog WaPOR_{v}.L{l} loaded.'.format(
                v=version, l=level))

        if cubeInfo:
            cubes_measure = []
            cubes_dimension = []
            for cube_code in df['code'].values:
                cubes_measure.append(self._query_cubeMeasures(cube_code))
                cubes_dimension.append(self._query_cubeDimensions(cube_code))
            df['measure'] = cubes_measure
            df['dimension'] = cubes_dimension

        self.catalog = df
        return self.catalog

    def _query_catalog(self, version=None, level=None):
        """Query catalog from workspace
        """
        print('WaPOR API:   _query_catalog')

        if isinstance(version, int):
            if 0 < version < 3:
                self.version = version
            else:
                raise ValueError(
                    'WaPOR API ERROR: _query_catalog: Version "{v}"'
                    ' is not correct!'.format(v=version))

        if isinstance(level, int):
            if 0 < level < 4:
                self.level = level
            else:
                raise ValueError(
                    'WaPOR API ERROR: _query_catalog: level "{l}"'
                    ' is not correct!'.format(l=level))
        elif level is None:
            self.version = version
        else:
            raise ValueError(
                'WaPOR API ERROR: _query_catalog: level "{l}"'
                ' is not correct!'.format(l=level))

        if self.level is None:
            base_url = '{0}{1}/cubes?overview=false&paged=false'
            request_url = base_url.format(
                self.path['catalog'],
                self.workspaces[self.version])
        else:
            base_url = '{0}{1}/cubes?overview=false&paged=false&tags=L{2}'
            request_url = base_url.format(
                self.path['catalog'],
                self.workspaces[self.version],
                self.level)

        if self.print_job:
            print(request_url)

        # requests
        try:
            resq = requests.get(
                request_url)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()

            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    df = pd.DataFrame.from_dict(resp, orient='columns')
                    return df
                    # return df.sort_values(['code'], ascending=[True])
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    # def _query_cubeInfo(self,cube_code):
    #     request_url = r'{0}{1}/cubes/{2}?overview=false'.format(self.path['catalog'],
    #     self.workspaces[self.version],cube_code)
    #     resp = requests.get(request_url)
    #     try:
    #         meta_data_items = resp.json()['response']
    #         cube_info=meta_data_items #['additionalInfo']
    #     except:
    #         cube_info=None
    #     return cube_info

    def getCubeInfo(self, cube_code, version=None, level=None):
        """Get cube info

        Parameters
        ----------
        cube_code: str
            Cube code.
        version: int, optional
            WaPOR workspace version, default 2.
        level: int, optional
            Data resolution level, default None.

        Returns
        -------
        cube_info: dict
            Cube information.
        """
        print('WaPOR API: Loading "{c_code}" CubeInfo...'.format(
            c_code=cube_code))

        isFound = False

        if isinstance(version, int) and isinstance(level, int):
            if 0 < version < 3 and 0 < level < 4:
                isFound = True

        if not isFound:
            version, level = 2, 3
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if not isFound:
            version, level = 2, 2
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if not isFound:
            version, level = 2, 1
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if not isFound:
            version, level = 1, 3
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if not isFound:
            version, level = 1, 2
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if not isFound:
            version, level = 1, 1
            catalog = self.getCatalog(version, level, cubeInfo=False)
            if cube_code in catalog['code'].tolist():
                isFound = True

        if isFound:
            print('WaPOR API: "{c_code}" is found in WaPOR_{v}.L{l}'.format(
                c_code=cube_code, v=version, l=level))

            catalog = self.getCatalog(version, level, cubeInfo=True)
            cube_info = catalog.loc[catalog['code'] == cube_code].to_dict('records')[0]
            return cube_info
        else:
            raise ValueError(
                'WaPOR API ERROR: "{c_code}" is not available in WaPOR'.format(
                    c_code=cube_code))

    def _query_cubeMeasures(self, cube_code):
        """Query cube measures
        """
        # print('WaPOR API:   _query_cubeMeasures')

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()

            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    return resp[0]
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def _query_cubeDimensions(self, cube_code):
        """Query cube dimensions
        """
        # print('WaPOR API:   _query_cubeDimensions')

        base_url = '{0}{1}/cubes/{2}/dimensions?overview=false&paged=false'
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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    return resp
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(url=request_url))

    def getAvailData(self, cube_code, time_range='2009-01-01,2018-12-31',
                     location=[], season=[], stage=[],
                     version=None, level=None):
        """Get Available Data

        Parameters
        ----------
        cube_code: str
            ex. 'L2_CTY_PHE_S'.
        time_range: str, optional
            ex. '2009-01-01,2018-12-31'.
        location: list, str, optional
            default: empty list, return all available locations, ex. ['ETH'].
        season: list, str, optional
            default: empty list, return all available seasons, ex. ['S1'].
        stage: list, str, optional
            default: empty list, return all available stages, ex. ['EOS','SOS'].
        version: int, optional
            WaPOR workspace version, default 2.
        level: int, optional
            Data resolution level, default None.

        Returns
        -------
        data: :obj:`pandas.DataFrame`
            Available Data table.
        """
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            cube_info = self.getCubeInfo(cube_code, version=version, level=level)
            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']
        except BaseException:
            print('WaPOR API ERROR: Cannot get cube info')

        print('WaPOR API: Loading "{c_code}" data...'.format(c_code=cube_code))

        dims_ls = []
        columns_codes = ['MEASURES']
        rows_codes = []
        try:
            for dims in cube_dimensions:
                if dims['type'] == 'TIME':  # get time dims
                    time_dims_code = dims['code']
                    df_time = self._query_dimensionsMembers(cube_code, time_dims_code)

                    time_dims = {
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
            print('WaPOR API ERROR:Cannot get list of available data')
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
        """Query Available Data
        """
        print('WaPOR API:   _query_availData')

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        df = pd.DataFrame(resp['items'])
                        # df = pd.DataFrame.from_dict(resp, orient='columns')
                        return df
                    except BaseException:
                        print('WaPOR API ERROR: Cannot get list of available data')
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def _query_dimensionsMembers(self, cube_code, dims_code):
        """Query dimensions members
        """
        print('WaPOR API:   _query_dimensionsMembers')

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        df = pd.DataFrame.from_dict(resp, orient='columns')
                        return df
                    except BaseException:
                        print('WaPOR API ERROR: Cannot get dimensions Members')
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getLocations(self, version=None, level=None):
        """Get Locations

        Parameters
        ----------
        version: int, optional
            WaPOR workspace version, default 2.
        level: int, optional
            Data resolution level, 2 or 3, default None.

        Returns
        -------
        locations: :obj:`pandas.DataFrame`
            Locations table.
        """
        print(
            'WaPOR API: Loading locations WaPOR_{v}.L{l}...'.format(v=version, l=level))

        self.version = 2
        self.level = None
        if isinstance(version, int):
            if 0 < version < 3:
                self.version = version
        if isinstance(level, int):
            if 0 < level < 4:
                self.level = level

        if self.locationsTable is None:
            df_loc = self._query_locations(version, level)
            df_loc = self.locationsTable
        else:
            df_loc = self.locationsTable

        if level is not None:
            self.level = level
            df_loc = df_loc.loc[df_loc["l{0}".format(self.level)] == True]
        return df_loc

    def _query_locations(self, version=None, level=None):
        """Query Locations
        """
        print('WaPOR API:   _query_locations')

        base_url = '{0}'
        request_url = base_url.format(
            self.path['query'])

        if self.print_job:
            print(request_url)

        # requests
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

        try:
            resq = requests.post(
                request_url,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

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
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getRasterUrl(self, cube_code, rasterId, APIToken=""):
        """Get Raster Url

        Parameters
        ----------
        cube_code: str
            Cube code.
        rasterId: str
            Raster ID, from Available Data table "raster_id", ex. "L1_PCP_0901M".

        Returns
        -------
        download: dict
            Download url and expiry_datetime.
        """
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        print('WaPOR API: Loading "{c_code}" url from WaPOR{v}.L{l}...'.format(
            c_code=cube_code, v=self.version, l=self.level))

        download_url = self._query_rasterUrl(cube_code, rasterId, AccessToken)
        return download_url

    def _query_rasterUrl(self, cube_code, rasterId, AccessToken):
        """Query Raster Url
        """
        print('WaPOR API:   _query_rasterUrl')

        base_url = '{0}{1}'
        request_url = base_url.format(
            self.path['download'],
            self.workspaces[self.version])

        if self.print_job:
            print(request_url)

        request_headers = {
            'Authorization': "Bearer " + AccessToken}
        request_json = {
            'language': 'en',
            'requestType': 'mapset_raster',
            'cubeCode': cube_code,
            'rasterId': rasterId}

        # requests
        try:
            resq = requests.get(
                request_url,
                headers=request_headers,
                json=request_json)
            resq.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

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
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getCropRasterURL(self, bbox, cube_code,
                         time_code, rasterId, APIToken=""):
        """Get Crop Raster Url

        Do need Authorization

        Parameters
        ----------
        bbox: list
            [xmin,ymin,xmax,ymax], latitude and longitude.
        cube_code: str
            Cube code.
        time_code: str
            Time code, from Available Data table "raster_id",
            ex. "[2009-01-01,2009-02-01)".
        rasterId: str
            Raster ID, from Available Data table "raster_id",
            ex. "L1_PCP_0901M".
        APIToken: str
            WaPOR API Token.

        Returns
        -------
        download: str
            Download url.
        """
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            # cube_info = self.getCubeInfo(cube_code)
            catalog = self.getCatalog(self.version, self.level, cubeInfo=True)
            cube_info = catalog.loc[catalog['code'] == cube_code].to_dict('records')[
                0]

            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']

            for cube_dimension in cube_dimensions:
                if cube_dimension['type'] == 'TIME':
                    cube_dimension_code = cube_dimension['code']
        except BaseException:
            print('WaPOR API ERROR: Cannot get cube info')

        print('WaPOR API: Loading "{c_code}" url from WaPOR{v}.L{l}...'.format(
            c_code=cube_code, v=self.version, l=self.level))

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        job_url = resp['links'][0]['href']

                        if self.print_job:
                            print('WaPOR API: Downloading "{c_code}" "{t}"...'.format(
                                c_code=cube_code, t=resp['type']))

                        output = self._query_jobOutput(job_url)
                        return output
                    except BaseException:
                        print('WaPOR API ERROR: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(
                    url=request_url))

    def getAreaTimeseries(self, shapefile_fh, cube_code,
                          time_range="2009-01-01,2018-12-31", APIToken=""):
        """Get Area Timeseries

        Do need Authorization

        Parameters
        ----------
        shapefile_fh: str
            ex. "E:/Area.shp".
        cube_code: str
            Cube code.
        time_range: str, optional
            "YYYY-MM-DD,YYYY-MM-DD".
        APIToken: str
            WaPOR API Token.

        Returns
        -------
        timeseries: :obj:`pandas.DataFrame`
            Area timeseries table.
        """
        # Check AccessToken expires
        self.getCheckToken()
        AccessToken = self.token['Access']

        # Get measure_code and dimension_code
        try:
            # cube_info = self.getCubeInfo(cube_code)
            catalog = self.getCatalog(self.version, self.level, cubeInfo=True)
            cube_info = catalog.loc[catalog['code'] == cube_code].to_dict('records')[
                0]

            # get measures
            cube_measure_code = cube_info['measure']['code']
            # get dimension
            cube_dimensions = cube_info['dimension']

            for cube_dimension in cube_dimensions:
                if cube_dimension['type'] == 'TIME':
                    cube_dimension_code = cube_dimension['code']
        except BaseException:
            print('WaPOR API ERROR: Cannot get cube info')

        print(
            'WaPOR API: Loading "{c_code}" area timeseries...'.format(c_code=cube_code))

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
        else:
            resq_json = resq.json()
            try:
                resp = resq_json['response']
                # print(resp)

                if resq_json['message'] == 'OK':
                    try:
                        job_url = resp['links'][0]['href']

                        if self.print_job:
                            print('WaPOR API: Downloading "{c_code}" "{t}"...'.format(
                                c_code=cube_code, t=resp['type']))

                        output = self._query_jobOutput(job_url)
                        return output
                    except BaseException:
                        print('WaPOR API ERROR: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(url=request_url))

    def _query_jobOutput(self, job_url):
        """Query Job output, url(str) or table(pd.DataFrame)
        """
        print('WaPOR API:   _query_jobOutput')

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
                raise Exception("WaPOR API Http Error: {e}".format(e=err))
            except requests.exceptions.ConnectionError as err:
                raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
            except requests.exceptions.Timeout as err:
                raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
            except requests.exceptions.RequestException as err:
                raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
            else:
                resq_json = resq.json()
                try:
                    resp = resq_json['response']
                    # print(resp)

                    if resq_json['message'] == 'OK':
                        jobType = resp['type']

                        if self.print_job:
                            print('WaPOR API:  {i:d} {s}'.format(i=ijob,
                                                                 s=resp['status']))

                        if resp['status'] == 'COMPLETED':
                            contiue = False
                            if jobType == 'CROP RASTER':
                                output = resp['output']['downloadUrl']
                            elif jobType == 'AREA STATS':
                                results = resp['output']
                                output = pd.DataFrame(
                                    results['items'], columns=results['header'])
                            else:
                                print('WaPOR API ERROR: Invalid jobType')
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
                    print('WaPOR API ERROR: Cannot get {url}'.format(url=request_url))

            ijob += 1

    def getPixelTimeseries(self, pixelCoordinates, cube_code,
                           time_range="2009-01-01,2018-12-31"):
        """Get Pixel Timeseries

        Do not need Authorization

        Parameters
        ----------
        pixelCoordinates: list
            ex. [37.95883206252312, 7.89534].
        cube_code: str
            Cube code.
        time_range: str, optional
            "YYYY-MM-DD,YYYY-MM-DD".

        Returns
        -------
        timeseries: :obj:`pandas.DataFrame`
            Point timeseries table.
        """
        # get cube info
        # cube_info = self.getCubeInfo(cube_code)
        catalog = self.getCatalog(self.version, self.level, cubeInfo=True)
        cube_info = catalog.loc[catalog['code'] == cube_code].to_dict('records')[
            0]

        # get measures
        cube_measure_code = cube_info['measure']['code']
        for dims in cube_info['dimension']:
            if dims['type'] == 'TIME':
                cube_dimension_code = dims['code']

        print('WaPOR API: Loading "{c_code}" point timeseries...'.format(
            c_code=cube_code))

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
            raise Exception("WaPOR API Http Error: {e}".format(e=err))
        except requests.exceptions.ConnectionError as err:
            raise Exception("WaPOR API Error Connecting: {e}".format(e=err))
        except requests.exceptions.Timeout as err:
            raise Exception("WaPOR API Timeout Error: {e}".format(e=err))
        except requests.exceptions.RequestException as err:
            raise Exception("WaPOR API OOps: Something Else {e}".format(e=err))
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
                        print('WaPOR API ERROR: Server response is empty')
                        return None
                else:
                    print(resq_json['message'])
            except BaseException:
                print('WaPOR API ERROR: Cannot get {url}'.format(url=request_url))
