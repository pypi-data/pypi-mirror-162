# pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals, fixme
"""
Basking.io — Python SDK
- Occupancy Class: handles all functionality related to occupancy.
"""

import json
import logging
from datetime import datetime, timedelta

import pandas as pd


class Occupancy:
    """
    Handles all functionality related to occupancy data.
    The occupancy class can be accessed as follows
    ::
        basking.occupancy
    """

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_building_occupancy_stats_daily(
            self,
            building_id,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,  # obsolete, but supported
            end_unix_timestamp=None,  # obsolete, but supported
            pandify=False,
    ):
        """
        Returns daily statistical occupancy data for a building between the given time frames.

        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param building_id:  The building ID
        :type building_id: str.
        :param pandify:  Function returns a DataFrame if this is True.
        :type pandify: bool.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing the end date as seconds since epoch.
        :type end_unix_timestamp: int.

        # todo: check all uses for this function and update.

        :return: DataFrame or Object with statistics about the building on the selected date range
        """

        # checks

        try:
            segment_start_date_timestamp = ''
            segment_end_date_timestamp = ''
            data = []
            page_size_d = 30
            segment_start_date_timestamp = start_obj_tz_unaware
            segment_end_date_timestamp = min(
                segment_start_date_timestamp + timedelta(days=page_size_d),
                end_obj_tz_unaware
            )
            while segment_start_date_timestamp < end_obj_tz_unaware:
                try:
                    start_unaware_timezone, end_unaware_timezone = self.aware_unaware_datetime_converter(
                        building_id=building_id,
                        start_obj_tz_aware=start_obj_tz_aware,
                        end_obj_tz_aware=end_obj_tz_aware,
                        start_obj_tz_unaware=segment_start_date_timestamp,
                        end_obj_tz_unaware=segment_end_date_timestamp,
                        start_unix_timestamp=start_unix_timestamp,
                        end_unix_timestamp=end_unix_timestamp
                    )

                except TypeError:
                    self.log.error('no data')
                    return
                self.log.debug(
                    " > Paginating between timestamps: %s - %s ",
                    segment_start_date_timestamp,
                    segment_end_date_timestamp
                )
                self.log.debug('Started get_building_occupancy_stats_daily with'
                               ' - building_id = %s'
                               ' - start_date_str =%s'
                               ' - end_date_str = %s',
                               building_id, start_unaware_timezone, end_unaware_timezone)
                query, variables = self.basking.graphql_query.get_building_occupancy_stats_daily_graphql_query(
                    str(building_id), str(start_unaware_timezone), str(end_unaware_timezone))
                result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
                data_ = json.loads(result)
                data += data_['data']['location']['occupancy']['daily']

                # prepare for next loop.
                segment_start_date_timestamp = segment_end_date_timestamp + timedelta(days=1)

                segment_end_date_timestamp = min(
                    segment_start_date_timestamp + timedelta(days=page_size_d),
                    end_obj_tz_unaware
                )

            if not isinstance(data, object):
                # has to be an object
                raise AssertionError(f'wrong type for data {type(data)}. required type is object')
            # has_errors = self.basking.basking_handle_api_return_errors(data)

            if pandify:
                df = pd.DataFrame(data)
                if len(df):
                    try:
                        df.set_index('date', inplace=True)
                        df.rename(columns={
                            'avgCount': 'occupancy_daily_avg',
                            'peakCount': 'occupancy_daily_peak',
                            'uniqueCount': 'occupants_daily_unique',
                            'adjustedCapacity': 'adjustedCapacity',
                            'adjustedCapacityPct': 'adjustedCapacityPct'
                        }, inplace=True)
                        df = df[
                            ['occupancy_daily_avg', 'occupancy_daily_peak', 'occupants_daily_unique',
                             'adjustedCapacity', 'adjustedCapacityPct']]
                        df.index = pd.to_datetime(df.index)
                        # the API returns date flagged as UTC wrongly. we need to replace TZ to building TZ
                        building = self.basking.location.get_building(building_id=building_id, pandify=False)
                        tz_str = building['data']['getBuilding']['timeZone']
                        if not tz_str:
                            raise AssertionError(f'length for time zone {len(tz_str)} is not correct.')
                        df.index = df.index.tz_localize(None).tz_localize(tz_str)
                    except TypeError:
                        self.log.error("getting error in dataframe portion")
                else:
                    self.log.debug('no data returned for %s', building_id)
                return df
            return data
        except TypeError:
            self.log.error('no data returned for %s', building_id)

    def get_building_occupancy_hourly(
            self,
            building_id,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
            ap_floor_id=None,
            floor_area_id=None,
            ap_id=0,
            pandify=True
    ):
        """
        This function returns the hourly occupancy data for the specified range aggregated in 3 levels.
        You can choose the aggregation level by specifying the parameters.
            - Building (specify building_id)
            - Floor  (specify building_id + floor_id)
            - Access Point (specify building_id + floor_id + ap_id)

        TODO: prevent passing floor and floor_area at the same time. only 1 is possible, or none.

        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing start date as seconds since epoch
        :type end_unix_timestamp: int.
        :param building_id: The basking building id
        :type building_id: str.
        :param ap_id: The basking access point id
        :type ap_id: Int.
        :param ap_floor_id: The access point floor id
        :type ap_floor_id: Int.
        :param floor_area_id: The floor area ID for the query
        :type floor_area_id: Int.
        :param pandify: makes the call return a panda dataframe
        :type pandify: bool.

        :return: results as DF or array
        """

        building = self.basking.location.get_building(building_id=building_id)
        tz_str = building['data']['getBuilding']['timeZone']
        # pagination
        page_size_d = 30  # 30 days max query length!
        # initial condition
        segment_start_date_timestamp = start_obj_tz_unaware

        segment_end_date_timestamp = min(
            segment_start_date_timestamp + timedelta(days=page_size_d),
            end_obj_tz_unaware
        )

        data = []

        while segment_start_date_timestamp < end_obj_tz_unaware:
            try:
                start_unaware_timezone, end_unaware_timezone = self.aware_unaware_datetime_converter(
                    building_id=building_id,
                    start_obj_tz_aware=start_obj_tz_aware,
                    end_obj_tz_aware=end_obj_tz_aware,
                    start_obj_tz_unaware=segment_start_date_timestamp,
                    end_obj_tz_unaware=segment_end_date_timestamp,
                    start_unix_timestamp=start_unix_timestamp,
                    end_unix_timestamp=end_unix_timestamp
                )

            except TypeError:
                self.log.error('no data')
                return
            self.log.debug(
                " > Paginating between timestamps: %s - %s ",
                start_unaware_timezone,
                end_unaware_timezone
            )

            data_ = self.get_building_occupancy_hourly_pagination(
                start_unaware_timezone,
                end_unaware_timezone,
                building_id,
                ap_floor_id,
                floor_area_id,
                ap_id
            )
            if 'message' in data:
                self.basking.api_timeout_handler(data)
            data += data_['data']['location']['occupancy']['hourly']
            # prepare for next loop.
            segment_start_date_timestamp = segment_end_date_timestamp

            segment_end_date_timestamp = min(
                segment_start_date_timestamp + timedelta(days=page_size_d),
                end_obj_tz_unaware
            )

        self.log.debug('Done with pagination')
        if len(data):
            if pandify:
                df = pd.DataFrame(data)
                df.rename(columns={
                    'hour': 'timestamp',
                    'occupancy': 'occupancy_hourly'
                }, inplace=True)

                df.set_index(
                    pd.to_datetime(
                        df['timestamp']),
                    inplace=True)

                # convert the tz to building tz
                df.index = df.tz_convert(tz_str).index
                df = df[['occupancy_hourly', 'adjustedCapacity', 'adjustedCapacityPct']]
                return df
            return data
        else:
            self.log.info('got no data')
            if pandify:
                return pd.DataFrame()

    def get_building_occupancy_hourly_pagination(
            self,
            start_obj_tz_unaware,
            end_obj_tz_unaware,
            building_id,
            ap_floor_id,
            floor_area_id,
            ap_id
    ):
        """
        Internal method used to paginate long queries of hourly data.

        :param start_obj_tz_unaware: Preferred way of passing the start date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the end date
        :type end_obj_tz_unaware: datetime object.
        :param ap_floor_id: The access point floor id
        :type ap_floor_id: Int.
        :param floor_area_id: The floor area ID for the query
        :type floor_area_id: Int.
        :param ap_id: The basking access point id
        :type ap_id: Int.
        :param building_id:  The building ID
        :type building_id: str.

        :return: results as DF or array about building_occpancy_hourly_pagination
        """

        query, variables = self.basking.graphql_query.get_building_occupancy_hourly_pagination_graphql_query(
            building_id,
            start_obj_tz_unaware,
            end_obj_tz_unaware
        )

        if ap_floor_id:
            variables['floorId'] = ap_floor_id
            if ap_id:
                variables['ap_id'] = ap_id
                # if not specified, then aggregation level will be floor
        elif floor_area_id:
            variables['floorAreaId'] = floor_area_id
            # if not specified, then aggregation level will be Building

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)

        data = json.loads(result)
        if 'message' in data:
            self.basking.api_timeout_handler(data)
        if 'errors' in data:
            self.log.error('Error in query:')
            self.log.error(data['errors'])
        return data

    def get_building_occupancy_hourly_by_floor(
            self,
            building_id,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None
    ):
        """
        get_building_occupancy_hourly_by_floor allows for batch processing floor data.
        It calls internally :obj:`~get_building_occupancy_hourly`  in batch and
        returns a combined df.

        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing start date as seconds since epoch
        :type end_unix_timestamp: int.
        :param building_id: The basking building id
        :type building_id: str.

        :return: pandas DataFrame
        """

        if not building_id:
            self.log.info('got no data in get_building_occupancy_hourly_by_floor')
            return pd.DataFrame()  # creates a new dataframe that's empty

        tmp_array_of_df = []
        # df_floors = self.get_building(building_id, pandify=True)
        self.log.debug(
            'start with get_building building_id=%s',
            building_id
        )
        try:
            meraki_floors = self.basking.location.get_building(
                building_id)['data']['getBuilding']['merakiApFloors']
        except TypeError:
            self.log.info('got no data in get_building_occupancy_hourly_by_floor')
            return pd.DataFrame()  # creates a new dataframe that's empty
        for this_meraki_ap_floor in meraki_floors:
            this_meraki_ap_floor_id = this_meraki_ap_floor['id']
            self.log.debug(
                ">>> starting with ap_floor_id=%s",
                this_meraki_ap_floor_id
            )
            df_ = self.get_building_occupancy_hourly(
                building_id=building_id,
                start_obj_tz_aware=start_obj_tz_aware,
                end_obj_tz_aware=end_obj_tz_aware,
                start_obj_tz_unaware=start_obj_tz_unaware,
                end_obj_tz_unaware=end_obj_tz_unaware,
                start_unix_timestamp=start_unix_timestamp,
                end_unix_timestamp=end_unix_timestamp,
                ap_floor_id=this_meraki_ap_floor_id,
                ap_id=None,
                pandify=True
            )

            if isinstance(df_, pd.DataFrame):
                df_['floor_ap_id'] = this_meraki_ap_floor_id
                df_['floorName'] = this_meraki_ap_floor['floorName']
                tmp_array_of_df.append(df_)
        if len(tmp_array_of_df):
            df = pd.concat(tmp_array_of_df)
            return df
        self.log.info('got no data in get_building_occupancy_hourly_by_floor')
        return pd.DataFrame()

    def get_building_occupancy_hourly_by_floor_area(
            self,
            building_id,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
    ):
        """
        get_building_occupancy_hourly_by_floor_area allows for batch processing floor area data.
        It calls internally :obj:`~get_building_occupancy_hourly`  in batch and
        returns a combined df.


        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing start date as seconds since epoch
        :type end_unix_timestamp: int.
        :param building_id: The basking building id
        :type building_id: str.

        :return: pandas DataFrame
        """
        tmp_array_of_df = []
        basking_floors = self.basking.location.get_building(building_id)['data']['getBuilding']['floors']
        for this_basking_floor in basking_floors:
            this_basking_floor_id = this_basking_floor['id']
            this_basking_floor_name = this_basking_floor['name']
            floor_areas = self.basking.location.get_floor_areas_for_floor(this_basking_floor_id)
            self.log.debug(
                ">>> basking_floor_id=%s has %s floor areas",
                this_basking_floor_id,
                len(floor_areas)
            )
            for this_floor_area in floor_areas:
                this_floor_area_id = this_floor_area['id']
                self.log.debug(
                    ">>> >>> this_floor_area_id=%s",
                    this_floor_area_id
                )
                df_ = self.get_building_occupancy_hourly(
                    building_id=building_id,
                    start_obj_tz_aware=start_obj_tz_aware,
                    end_obj_tz_aware=end_obj_tz_aware,
                    start_obj_tz_unaware=start_obj_tz_unaware,
                    end_obj_tz_unaware=end_obj_tz_unaware,
                    start_unix_timestamp=start_unix_timestamp,
                    end_unix_timestamp=end_unix_timestamp,
                    floor_area_id=this_floor_area_id,
                    ap_id=None,
                    pandify=True
                )
                if isinstance(df_, pd.DataFrame):
                    df_['floor_area_id'] = this_floor_area_id
                    df_['floor_area_name'] = this_floor_area['name']
                    df_['floor_name'] = this_basking_floor_name

                    tmp_array_of_df.append(df_)
        if len(tmp_array_of_df):
            df = pd.concat(tmp_array_of_df)
            return df
        self.log.info('got no data in get_building_occupancy_hourly_by_floor')
        return pd.DataFrame()

    def get_floor_heatmap_kpi(
            self,
            basking_floor_id,
            start_date_seconds_building_tz,
            end_date_seconds_building_tz,
            pandify=False
    ):
        """
        Returns the peak occupancy KPI by areas for a floor id between the specified time period.

        :param start_date_seconds_building_tz: Start Date as seconds since epoch
        :type start_date_seconds_building_tz: int.
        :param end_date_seconds_building_tz: End Date as seconds since epoch.
        :type end_date_seconds_building_tz: int.
        :param basking_floor_id: The basking floor id
        :type basking_floor_id: str.
        :param pandify: makes the call return a panda dataframe
        :type pandify: bool.

        :return: kpis df or array
        """
        self.log.debug(
            """Started get_floor_heatmap_kpi with
                    - basking_floor_id=%s
                    - start_date_seconds_building_tz=%s
                    - end_date_seconds_building_tz=%s
            """,
            basking_floor_id,
            start_date_seconds_building_tz,
            end_date_seconds_building_tz
        )
        query, variables = self.basking.graphql_query.get_floor_heatmap_kpi_graphql_query(
            basking_floor_id,
            start_date_seconds_building_tz,
            end_date_seconds_building_tz
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)
        if 'message' in data:
            self.basking.api_timeout_handler(data)
        try:
            data = data['data']['getFloorHeatmapKPI']
            if len(data):
                if pandify:
                    df = pd.DataFrame(data)
                    return df
                return data
        except TypeError:
            self.log.info('got no data')

    def get_location_duration_of_visits(
            self,
            building_id=None,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
            pandify=True
    ):
        """
        Returns the histogram of the duration of visits between 2 dates at building level.

        Read more about this feature here: https://basking.io/blog/new-features/understand-the-duration-of-visits/

        :param building_id: building_id
        :type building_id: str
        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing the end date as seconds since epoch.
        :type end_unix_timestamp: int.
        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: DataFrame or Array of dictionaries with statistics about the duration of visits
                for the building on the selected date range

         """
        start_obj_str, end_obj_str = self.aware_unaware_datetime_converter(
            building_id=building_id,
            start_obj_tz_aware=start_obj_tz_aware,
            end_obj_tz_aware=end_obj_tz_aware,
            start_obj_tz_unaware=start_obj_tz_unaware,
            end_obj_tz_unaware=end_obj_tz_unaware,
            start_unix_timestamp=start_unix_timestamp,
            end_unix_timestamp=end_unix_timestamp,
        )
        query, variables = self.basking.graphql_query.get_location_duration_of_visits_graphql_query(
            building_id,
            start_obj_str,
            end_obj_str
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)

        data = json.loads(result)
        if 'message' in data:
            self.basking.api_timeout_handler(data)

        try:
            data = data['data']['location']['occupancy']['duration']
        except TypeError:
            self.log.error('no data')
            return data

        if 'message' in data:
            self.basking.api_timeout_handler(data)

        if 'errors' in data:
            self.log.error('Error in query:')
            self.log.error(data['errors'])
            return data

        if len(data) > 0:
            if pandify:
                df = pd.DataFrame(data)
                return df
            return data
        self.log.info('got no data')
        return pd.DataFrame()

    def get_location_frequency_of_visits(
            self,
            building_id=None,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
            pandify=None
    ):

        """
        Returns the histogram of the frequency of visits between 2 dates at building level.
        Read more about this feature here:
        https://basking.io/blog/new-features/understand-the-frequency-of-visits-to-your-office/.

        :param building_id: building_id
        :type building_id: str
        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing the end date as seconds since epoch.
        :type end_unix_timestamp: int.
        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: DataFrame or Array of dictionaries with statistics about the duration of visits
                for the building on the selected date range

         """
        start_obj_str, end_obj_str = self.aware_unaware_datetime_converter(
            building_id=building_id,
            start_obj_tz_aware=start_obj_tz_aware,
            end_obj_tz_aware=end_obj_tz_aware,
            start_obj_tz_unaware=start_obj_tz_unaware,
            end_obj_tz_unaware=end_obj_tz_unaware,
            start_unix_timestamp=start_unix_timestamp,
            end_unix_timestamp=end_unix_timestamp,
        )

        query, variables = self.basking.graphql_query.get_location_frequency_of_visits_graphql_query(
            building_id,
            start_obj_str,
            end_obj_str
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)

        if 'message' in data:
            self.basking.api_timeout_handler(data)

        data = data['data']['location']['occupancy']['daysPerWeek']

        if 'errors' in data:
            self.log.error('Error in query:')
            self.log.error(data['errors'])
            return data

        if len(data) > 0:
            if pandify:
                df = pd.DataFrame(data)
                return df
            return data
        self.log.info('got no data')

    def get_density_for_building(
            self,
            building_id,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
    ):
        """
        Returns the density of the office in RSM at peak between the time period defined.

        :param building_id: The building ID
        :type building_id: str.
        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing end date as seconds since epoch
        :type end_unix_timestamp: int.

        :return: density in RSM

        TODO: convert the density in the user's metric system.
        """
        # 1. get the area
        try:
            building = self.basking.location.get_building(building_id=building_id)

            area_local = building['data']['getBuilding']['area']
            measurement_units = building['data']['getBuilding']['measurementUnits']

            if measurement_units == 'Imperial':
                m2_in_sqf = 10.7639  # 1 sqm equals 10.7 sqf.
                area_metric = area_local / m2_in_sqf
            else:
                area_metric = area_local
            # 2. get the daily peaks occupancy
            if start_unix_timestamp and end_unix_timestamp:
                start_obj_tz_unaware, end_obj_tz_unaware = self.aware_unaware_datetime_converter(
                    building_id=building_id,
                    start_obj_tz_aware=start_obj_tz_aware,
                    end_obj_tz_aware=end_obj_tz_aware,
                    start_obj_tz_unaware=start_obj_tz_unaware,
                    end_obj_tz_unaware=end_obj_tz_unaware,
                    start_unix_timestamp=start_unix_timestamp,
                    end_unix_timestamp=end_unix_timestamp
                )
                start_obj_tz_unaware = datetime.strptime(start_obj_tz_unaware, "%Y-%m-%dT%H:%M:%SZ")
                end_obj_tz_unaware = datetime.strptime(end_obj_tz_unaware, "%Y-%m-%dT%H:%M:%SZ")

            df_building_daily_stats = self.get_building_occupancy_stats_daily(
                building_id=str(building_id),
                start_obj_tz_aware=start_obj_tz_aware,
                end_obj_tz_aware=end_obj_tz_aware,
                start_obj_tz_unaware=start_obj_tz_unaware,
                end_obj_tz_unaware=end_obj_tz_unaware,
                start_unix_timestamp=start_unix_timestamp,
                end_unix_timestamp=end_unix_timestamp,
                pandify=True
            )

            peak_counts = []

            for index, row in df_building_daily_stats.iterrows():
                peak_counts.append(row['occupancy_daily_peak'])
            if len(peak_counts) > 0:
                peak_occupancy = max(peak_counts)
            else:
                peak_occupancy = False
            # 3. calculate the density
            if peak_occupancy:
                density = area_metric / peak_occupancy
            else:
                density = False
            return density
        except (AttributeError, TypeError):
            self.log.error('no data')

    def get_density_for_building_last_days(
            self,
            building_id,
            days=7
    ):
        """
        Returns the density of an office in RSM at peak for the last 7 days from now.

        :param building_id: The building ID
        :type building_id: str.
        :param days: The days in the past to query
        :type days: int.

        :return: density for building_last_day
        """
        building = self.basking.location.get_building(building_id=building_id)
        a = datetime.now()
        end_date_obj = datetime(a.year, a.month, a.day)
        start_date_obj = end_date_obj - timedelta(days=days)
        tz_str = building['data']['getBuilding']['timeZone']
        if tz_str:
            return (
                self.get_density_for_building(
                    building_id=building_id,
                    start_obj_tz_unaware=start_date_obj,
                    end_obj_tz_unaware=end_date_obj
                )
            )
        else:
            self.log.error('Building has no timezone. Aborting. ')

    def aware_unaware_datetime_converter(
            self,
            building_id=None,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
    ):
        """
        Internal helper function for converting aware and unaware
        datetime into the required %Y-%m-%dT%H:%M:%SZ format.

        :param building_id: building_id
        :type building_id: str
        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing the end date as seconds since epoch.
        :type end_unix_timestamp: int.

        :return: timestamp as string, timezone aware using building timezone
        """
        try:
            if isinstance(start_obj_tz_aware, datetime) & isinstance(end_obj_tz_aware, datetime):
                if self.basking.check_if_datetime_obj_tz_aware(
                        start_obj_tz_aware) & self.basking.check_if_datetime_obj_tz_aware(end_obj_tz_aware):
                    self.log.debug('using the date objects: start_obj_tz_aware=%s and '
                                   'end_obj_tz_aware=%s', start_obj_tz_aware, end_obj_tz_aware)
                    start_date_str = start_obj_tz_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
                    end_date_str = end_obj_tz_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
                    return start_date_str, end_date_str
                else:
                    raise ValueError('start_obj_tz_aware and end_obj_tz_aware must be tz aware datetime objects')
            elif isinstance(start_obj_tz_unaware, datetime) & isinstance(end_obj_tz_unaware, datetime):
                if not self.basking.check_if_datetime_obj_tz_aware(start_obj_tz_unaware) \
                        and not self.basking.check_if_datetime_obj_tz_aware(end_obj_tz_unaware):
                    self.log.debug('using the date objects: start_obj_tz_unaware=%s '
                                   'and end_obj_tz_unaware=%s', start_obj_tz_unaware, end_obj_tz_unaware)

                    building = self.basking.location.get_building(building_id=building_id, pandify=False)
                    timezone_data = building['data']['getBuilding']['timeZone']
                    start_date = self.basking.date_obj_to_timestamp_ms(start_obj_tz_unaware, timezone_data)
                    end_date = self.basking.date_obj_to_timestamp_ms(end_obj_tz_unaware, timezone_data)
                    start_date_str = datetime.utcfromtimestamp(start_date).strftime("%Y-%m-%dT%H:%M:%SZ")
                    end_date_str = datetime.utcfromtimestamp(end_date).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return start_date_str, end_date_str
                else:
                    raise ValueError('start_obj_tz_unaware and end_obj_tz_unaware must be tz Unaware datetime objects')
            else:
                if isinstance(start_unix_timestamp, int) & isinstance(end_unix_timestamp, int):
                    self.log.warning('using deprecated timestamps. Pls consider updating your code to use'
                                     ' start_obj_tz_aware and end_obj_tz_aware. start_unix_timestamp and end_unix_timestamp'
                                     ' will be deprecated in the future.')
                    start_date_str = datetime.utcfromtimestamp(start_unix_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
                    end_date_str = datetime.utcfromtimestamp(end_unix_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return start_date_str, end_date_str
                else:
                    self.log.error('start_unix_timestamp=%s (type=%s), end_unix_timestamp=%s (type=%s)'
                                   , start_unix_timestamp, type(start_unix_timestamp),
                                   end_unix_timestamp, type(end_unix_timestamp))
                    raise ValueError('start_unix_timestamp and end_unix_timestamp must be int')
        except TypeError:
            self.log.error('invalid datetime')

    def get_location_popular_days_of_visits(
            self,
            building_id=None,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
            pandify=None
    ):
        """
        Returns the popular days of visits for a location between the specified dates.

        :param building_id: building_id
        :type building_id: str.
        :param start_obj_tz_aware: Preferred way of passing the start date
        :type start_obj_tz_aware: datetime object.
        :param end_obj_tz_aware: Preferred way of passing the end date
        :type end_obj_tz_aware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param start_unix_timestamp: Old way of passing start date as seconds since epoch
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: Old way of passing the end date as seconds since epoch.
        :type end_unix_timestamp: int.
        :param pandify: if True makes the call return a panda dataframe else return json
        :type pandify: bool.

        :return: Data frame or array of popular days of visit.
        """
        try:
            start_date_str, end_date_str = self.aware_unaware_datetime_converter(
                building_id=building_id,
                start_obj_tz_aware=start_obj_tz_aware,
                end_obj_tz_aware=end_obj_tz_aware,
                start_obj_tz_unaware=start_obj_tz_unaware,
                end_obj_tz_unaware=end_obj_tz_unaware,
                start_unix_timestamp=start_unix_timestamp,
                end_unix_timestamp=end_unix_timestamp,
            )
            self.log.debug('Started get_popular_day_of_visit with'
                           ' - building_id=%s'
                           ' - start_date_str=%s'
                           ' - end_date_str=%s',
                           building_id, start_date_str, end_date_str)

            query, variables = self.basking.graphql_query.get_location_popular_days_of_visits_graphql_query(
                building_id,
                start_date_str,
                end_date_str
            )
            result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
            data = json.loads(result)
            if 'message' in data:
                self.basking.api_timeout_handler(data)
            if pandify:
                popular_day_data = data['data']['location']['occupancy']['popularDaysOfVisit']
                df = pd.DataFrame(popular_day_data)
                return df
            return data
        except TypeError:
            self.log.error('no data')

    def get_organization_duration_of_visits(
            self,
            organization_id=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            pandify=None
    ):
        """
        Returns the duration of visits in for an organization between the specified time range.

        :param organization_id: building_id
        :type organization_id: str.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param pandify: if True makes the call return a panda dataframe else return json.
        :type pandify: bool.

        :return: Data frame or array with the duration of visits histogram at organization level.
        """

        try:
            start_date_str = start_obj_tz_unaware.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date_str = end_obj_tz_unaware.strftime("%Y-%m-%dT%H:%M:%SZ")
            if organization_id and isinstance(start_date_str, str) and isinstance(end_date_str, str):
                query, variables = self.basking.graphql_query.get_organization_duration_of_visits_graphql_query(
                    organization_id=organization_id,
                    start_datetime=start_date_str,
                    end_datetime=end_date_str
                )
                result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
                data = json.loads(result)
                if 'message' in data:
                    self.basking.api_timeout_handler(data)
                if 'errors' in data:
                    self.log.error(data)
                    return data
                pd_data = data['data']['organization']['durationOfVisits']
                if pandify:
                    df = pd.DataFrame(pd_data)
                    return df
                return data
            else:
                return self.log.error('invalid param given')
        except TypeError:
            self.log.error('no data')

    def get_organization_frequency_of_visits(
            self,
            organization_id=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            pandify=None
    ):
        """
        Returns the frequency of visits for an organization between the selected dates.

        :param organization_id: organization id
        :type organization_id: str.
        :param start_obj_tz_unaware: Preferred way of passing the end date
        :type start_obj_tz_unaware: datetime object.
        :param end_obj_tz_unaware: Preferred way of passing the start date
        :type end_obj_tz_unaware: datetime object.
        :param pandify: if True makes the call return a panda dataframe else return json
        :type pandify: bool.

        :return: Data frame or array with the frequency of visits histogram at organization level.
        """

        try:
            start_date_str = start_obj_tz_unaware.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date_str = end_obj_tz_unaware.strftime("%Y-%m-%dT%H:%M:%SZ")
            if organization_id and isinstance(start_date_str, str) and isinstance(end_date_str, str):
                query, variables = self.basking.graphql_query.get_organization_frequency_of_visits_graphql_query(
                    organization_id=organization_id,
                    start_datetime=start_date_str,
                    end_datetime=end_date_str
                )

                result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
                data = json.loads(result)
                if 'message' in data:
                    self.basking.api_timeout_handler(data)
                if 'errors' in data:
                    self.log.error(data)
                    return data

                pd_data = data['data']['organization']['frequencyOfVisits']
                if pandify:
                    df = pd.DataFrame(pd_data)
                    return df
                return data
            else:
                self.log.error('invalid param given')
        except TypeError:
            self.log.error('no data')

    def get_organization_popular_days_of_visits(
            self,
            organization_id=None,
            start_date=None,
            end_date=None,
            pandify=None
    ):

        """
        Returns the popular days of visit between the specified time range at organization level.

        :param organization_id: organization_id
        :type organization_id: str.
        :param start_date: Preferred way of passing the start date
        :type start_date: datetime object.
        :param end_date: Preferred way of passing the start date
        :type end_date: datetime object.
        :param pandify: if True makes the call return a panda dataframe else return json.
        :type pandify: bool.

        :return: Data frame or array of popular days of visits at organization level.
        """

        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        query, variables = self.basking.graphql_query.get_organization_popular_days_of_visits_graphql_query(
            organization_id=organization_id,
            start_date_str=start_date_str,
            end_date_str=end_date_str
        )
        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)
        if 'errors' in data:
            return data
        if pandify:
            pd_data = data['data']['organization']['popularDaysOfVisits']
            if pd_data:
                df = pd.DataFrame(pd_data)
                return df
            else:
                self.log.error('no data')
        return data
