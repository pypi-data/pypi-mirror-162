# pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals

"""
Basking.io — Python SDK
- Insight Class: handles all functionality related to insight.
"""

import json
import logging

import pandas as pd


class Insight:
    """insight class"""

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_location_insights(
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
        Returns insights data for a given location

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

        :return: insight data structure, either as a pandas dataframe or as a dict
        """

        try:
            start_date_str, end_date_str = self.basking.occupancy.aware_unaware_datetime_converter(
                building_id=building_id,
                start_obj_tz_aware=start_obj_tz_aware,
                end_obj_tz_aware=end_obj_tz_aware,
                start_obj_tz_unaware=start_obj_tz_unaware,
                end_obj_tz_unaware=end_obj_tz_unaware,
                start_unix_timestamp=start_unix_timestamp,
                end_unix_timestamp=end_unix_timestamp,
            )

            query, variables = self.basking.graphql_query.get_insight_graphql_query(
                building_id=building_id,
                start_datetime=start_date_str,
                end_datetime=end_date_str
            )
            result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
            data = json.loads(result)
            if 'message' in data:
                self.basking.api_timeout_handler(data)

            if 'errors' in data:
                self.log.error('Error in query:')
                self.log.error(data['errors'])
                return data

            # here we can assume we have no errors
            data['data']['getBuildingInsights']['staffAllocationIncreasePct'] = 100 * (
                    data['data']['getBuildingInsights']['staffAllocationIncrease'] - 1
            )
            if pandify:
                df = pd.DataFrame.from_dict(data['data']['getBuildingInsights'], orient='index').T
                return df
            return data
        except TypeError:
            self.log.error('invalid data')
