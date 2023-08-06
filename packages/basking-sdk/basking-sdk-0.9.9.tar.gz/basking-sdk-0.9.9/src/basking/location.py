# pylint: disable=line-too-long, invalid-name
"""
Basking.io — Python SDK
- Location Class: handles all functionality related to locations.
"""

import json
import logging
import pandas as pd


class Location:
    """
    The location class can be accessed as follows
    ::
        basking.location
    """

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_adjusted_capacity(self, building_id):
        """
        Returns the adjusted capacity at Building level in percentage

        :param building_id: building_id
        :type building_id: str.

        :return: return get_adjusted_capacity

        """

        query, variables = self.basking.graphql_query.get_adjusted_capacity_graphql_query(
            building_id
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data_ = json.loads(result)
        if 'message' in data_:
            self.basking.api_timeout_handler(data_)
        elif 'data' in data_:
            if 'getCapacity' in data_['data']:
                data = data_['data']['getCapacity']
            else:
                data = {}
        else:
            data = {}
        df = pd.DataFrame(data)
        return df

    def get_user_buildings(self, pandify=True):
        """
         This function returns the buildings this user has access to.

        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: building meta data object
        """

        query = self.basking.graphql_query.get_user_buildings_graphql_query()

        result = self.basking.graphql_query.graphql_executor(query=query, variables={})
        try:
            data = json.loads(result)['data']['viewer']['buildings']
            if 'message' in data:
                self.basking.api_timeout_handler(data)
        except TypeError:
            self.log.error('no valid data returned')
            self.log.error(result)
            return None

        if pandify:
            df = pd.DataFrame(data)
            df.set_index('id', inplace=True)
            return df
        return data

    def get_building(self, building_id, pandify=False):
        """
        Returns the meta information from a building.

        Example of use:
        ::
            basking.location.get_building(
                building_id='abcdef',
                pandify=True
            )

        :param building_id: The building ID
        :type building_id: str.
        :param pandify:  Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: building meta data object
        """

        query, variables = self.basking.graphql_query.get_building_graphql_query(building_id)

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)

        if 'message' in data:
            self.basking.api_timeout_handler(data)

        elif 'errors' in data:
            self.log.error(data)
            return data

        elif pandify:
            try:
                data = data['data']['getBuilding']['floors']
                df = pd.DataFrame(data)
                df.set_index('id', inplace=True)
                return df
            except TypeError:
                self.log.error("no data")
        else:
            return data

    def get_floors(
            self,
            building_id
    ):
        """
        get_flors
        Returns the building floor's meta information

        :param building_id: building_id
        :type building_id: str.

        :return: Pandas DataFrame
        """
        tmp_array_of_df = []
        try:
            basking_floors = self.get_building(building_id)['data']['getBuilding']['floors']
            for this_basking_floor in basking_floors:
                this_basking_floor_id = this_basking_floor['id']
                df_floor_meta_ = self.get_floor_meta_info(
                    basking_floor_id=this_basking_floor_id,
                    pandify=True
                )
                self.log.debug(
                    ">>> basking_floor_id=%s has %s floor areas",
                    this_basking_floor_id,
                    len(df_floor_meta_)
                )

                df_floor_meta_['building_id'] = building_id

                tmp_array_of_df.append(df_floor_meta_)
        except TypeError:
            self.log.error("no floor detail available")

        if len(tmp_array_of_df) > 0:
            df = pd.concat(tmp_array_of_df)
            return df
        self.log.info('got no data in get_floors')
        return pd.DataFrame()

    def get_floor_meta_info(
            self,
            basking_floor_id,
            pandify=True
    ):
        """get_floor_meta_info.

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.
        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: the meta information for a single floor.
        """

        query, variables = self.basking.graphql_query.get_floor_meta_info_graphql_query(basking_floor_id)
        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)
        if 'message' in data:
            self.basking.api_timeout_handler(data)
        elif 'errors' in data:
            self.log.error('Error in query:')
            self.log.error(data['errors'])
        data_ = data['data']['getFloor']
        if pandify:
            df = pd.DataFrame.from_records([data_], index='id')
            return df
        return data_

    def get_floor_areas_for_floor(
            self,
            basking_floor_id,
            pandify=False
    ):
        """
        the floor areas for a given floor.

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.
        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: the floor areas for a given floor.
        """

        query, variables = self.basking.graphql_query.get_floor_areas_for_floor_graphql_query(basking_floor_id)

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)
        if 'errors' in data:
            self.log.error('Error in query:')
            self.log.error(data['errors'])
        data_ = data['data']['getFloorArea']
        if pandify:
            df = pd.DataFrame(data_)
            return df
        return data_

    def get_floor_area(self, floorid, pandify=False):
        """
        deprecated function to ensure backwards compatibility

        :param floorid: floor id
        :type floorid: str.
        :param pandify: Function returns a DataFrame if this is True.
        :type pandify: bool.

        :return: data of get_floor_areas_for_floor
        """

        return self.get_floor_areas_for_floor(floorid, pandify)

    def get_floor_areas_for_building(
            self,
            building_id
    ):
        """
        get_floor_areas_for_building
        calls get_floor_areas_for_floor in batch and
        returns a combined df for each floor_area

        :param building_id: The basking building id
        :type building_id: str.

        :return: pandas DataFrame
        """

        tmp_array_of_df = []
        basking_floors = self.get_building(building_id)['data']['getBuilding']['floors']
        for this_basking_floor in basking_floors:
            this_basking_floor_id = this_basking_floor['id']
            df_floor_areas_ = self.get_floor_areas_for_floor(
                this_basking_floor_id,
                pandify=True
            )
            self.log.debug(
                """>>> basking_floor_id=%s has %s floor areas""",
                this_basking_floor_id,
                len(df_floor_areas_)
            )

            df_floor_areas_['basking_floor_id'] = this_basking_floor_id
            df_floor_areas_['building_id'] = building_id  # change in buildingid to building_id

            tmp_array_of_df.append(df_floor_areas_)
        if len(tmp_array_of_df):
            df = pd.concat(tmp_array_of_df)
            return df
        self.log.info('got no data in get_floor_areas_for_building')

    def get_building_floor_element_by_basking_floor_id(
            self,
            building_id,
            basking_floor_id
    ):
        """
        get_building_floor_element_by_basking_floor_id.

        :param building_id: building_id
        :type building_id: str.
        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.

        :return: the element of building.floors for the given basking_floor_id
        """

        if not isinstance(building_id, str):
            # has to be a string.
            raise AssertionError(f'wrong type for building_id {type(building_id)}. required type is str')

        if not len(building_id):
            # has to be a string.
            raise AssertionError(f'length for building_id {len(building_id)} is not correct.')

        if not isinstance(basking_floor_id, str):
            # has to be a string.
            raise AssertionError(f'wrong type for basking_floor_id {type(basking_floor_id)}. required type is str')

        if not len(basking_floor_id):
            # has to be a string.
            raise AssertionError(f'length for basking_floor_id {len(basking_floor_id)} is not correct.')

        building_meta = self.get_building(building_id=building_id)['data']['getBuilding']
        for floor_el in building_meta['floors']:
            this_floor_basking_floor_id = floor_el['id']
            if this_floor_basking_floor_id == basking_floor_id:
                return floor_el
        # if not found, we return this here.
        return None
