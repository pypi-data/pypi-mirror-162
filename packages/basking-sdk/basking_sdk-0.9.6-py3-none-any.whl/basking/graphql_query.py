# pylint: disable=invalid-name
"""
Basking.io — Python SDK
- Graphql Query Class: handles all graphql queries.
"""
import logging
import urllib
from urllib.error import HTTPError
import backoff
from graphqlclient import GraphQLClient


class GraphqlQuery:
    """
    graphql_query class
    """
    _ggraphql_client = None

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    @property
    def _graphql_client(self):
        try:
            if not self._ggraphql_client:
                if self.basking.auth_type == 'env_variables':
                    self.token = self.basking.get_new_cognito_token_()
                else:
                    raise ValueError('auth_type invalid.')
                self._ggraphql_client = GraphQLClient(self.basking.basking_api_url)
                self._ggraphql_client.inject_token(self.token)
        except (TypeError, AttributeError, ValueError):
            self.log.error("GraphQLClient error")
        return self._ggraphql_client

    @backoff.on_exception(backoff.expo,
                          urllib.error.HTTPError,
                          max_tries=8)
    def graphql_executor(
            self,
            query,
            variables
    ):
        """Implements backoff for graphql

        :param query: Graphql query to be executed
        :type query: str.
        :param variables: Variables for query
        :type variables: dict.

        :return: query result

        """
        try:
            graphql_executor_variable = self._graphql_client.execute(
                query=query,
                variables=variables
            )
            return graphql_executor_variable
        except AttributeError:
            self.log.error("get error while execute query")
        except HTTPError:
            return {"message": "Api Time out error"}

    @staticmethod
    def get_building_occupancy_stats_daily_graphql_query(building_id, start_date_str, end_date_str):

        """graphql query for get_building_occupancy_stats_daily function

        :param building_id: building_id
        :type building_id: str.
        :param start_date_str: start_date_str
        :type start_date_str: str.
        :param end_date_str: end_date_str
        :type end_date_str: str.

        :return: graphql query, variables

        """

        query = """
                    query get_building_occupancy_stats_daily(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!
                    ) {
                        location(id: $id) {
                            occupancy{
                                daily(
                                    from: $from,
                                    to: $to
                                ) {
                                    date, 
                                    peakCount,
                                    lastCount,
                                    avgCount,
                                    adjustedCapacity: capacity,
                                    adjustedCapacityPct: capacityPct,
                                    uniqueCount
                                }
                            }
                        }
                    }
                        """

        variables = {
            'id': str(building_id),
            'from': str(start_date_str),  # date.strftime("%Y-%m-%dT%H:%M:%SZ")
            'to': str(end_date_str)
        }

        return query, variables

    @staticmethod
    def get_building_graphql_query(building_id):
        """graphql query for get_building function

        :param building_id: building_id
        :type building_id: str.

        :return: graphql query, variables

        """

        query = """
                    query getBuilding($buildingid: ID){
                        getBuilding(id: $buildingid)
                        {
                            id,
                            workingDays,
                            name,
                            capacity,
                            numberOfDesks,
                            address,
                            timeZone,
                            lat,
                            lng,
                            organizationId,
                            organization{id, name},
                            merakiApFloors{id, apFloors, floorName, createdAt},
                            floors{id, buildingId,number, name, sqm, floorplanURL},
                            rentPriceSQM,
                            currency,
                            area,
                            operationStartTime,
                            operationEndTime,
                            measurementUnits,
                            targetOccupancy,
                            country,
                            countryRegion,
                            euroPerKWH,
                            pulsePerKW,
                        }
                    }
                """
        variables = {
            'buildingid': str(building_id)
        }
        return query, variables

    @staticmethod
    def get_building_occupancy_hourly_pagination_graphql_query(
            building_id,
            start_obj_tz_unaware,
            end_obj_tz_unaware
    ):
        """graphql query and variables for _get_building_occupancy_hourly_pagination function

        :param building_id: building_id
        :type building_id: str.
        :param start_obj_tz_unaware: start_obj_tz_unaware
        :type start_obj_tz_unaware: str.
        :param end_obj_tz_unaware: end_obj_tz_unaware
        :type end_obj_tz_unaware: str.

        :return: graphql query, variables

        """
        query = """
                query getBuildingMerakiHourlyData(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!,
                        $floorId: Int,
                        $floorAreaId: Int,
                    ) {
                        location(id: $id) {
                            occupancy{
                                hourly(
                                    from: $from,
                                    to: $to,
                                    floorId: $floorId,
                                    floorAreaId: $floorAreaId,
                                ) {
                                    hour, 
                                    occupancy: uniqueCount,
                                    adjustedCapacity: capacity,
                                    adjustedCapacityPct: capacityPct,
                                }
                            }
                        }
                    }

                """
        variables = {
            'id': str(building_id),
            "from": str(start_obj_tz_unaware),
            "to": str(end_obj_tz_unaware),
            "floorAreaId": 0,
            "floorId": 0
        }

        return query, variables

    @staticmethod
    def get_floor_heatmap_kpi_graphql_query(basking_floor_id,
                                            start_date_seconds_building_tz,
                                            end_date_seconds_building_tz):

        """graphql query for get_floor_heatmap_kpi function

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.
        :param start_date_seconds_building_tz: start_date_seconds_building_tz
        :type start_date_seconds_building_tz: int.
        :param end_date_seconds_building_tz: end_date_seconds_building_tz
        :type end_date_seconds_building_tz: int.

        :return: graphql query, variables

        """

        query = """
                       query getFloorHeatmapKPI($floorId: String, $startDate: String, $endDate: String)
                       {
                           getFloorHeatmapKPI(
                            floorId: $floorId,
                            startDate: $startDate,
                            endDate : $endDate,
                            resampleBy : 5
                        ){
                        floorAreaId,
                        maxDevices,
                        avgDevices,
                        maxTimeSpentMinutes,
                        avgTimeSpentMinutes,
                        minTimeSpentMinutes,
                        maxHumans,
                        avgHumans,
                        avgOcuppancy,
                        frequencyOfUse,
                        utilization
                    }}
                    """
        variables = {
            'floorId': str(basking_floor_id),
            'startDate': str(start_date_seconds_building_tz),
            'endDate': str(end_date_seconds_building_tz),
        }
        return query, variables

    @staticmethod
    def get_floor_meta_info_graphql_query(basking_floor_id):
        """graphql query for get_floor_meta_info function

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.

        :return: graphql query, variables

        """

        query = """
                        query readFloor($basking_floor_id: ID){
                            getFloor(id: $basking_floor_id) {
                                id, 
                                number, 
                                name, 
                                sqm, 
                                neCorner, 
                                swCorner, 
                                rotation, 
                                capacity
                            }
                        }
                        """
        variables = {
            'basking_floor_id': str(basking_floor_id)
        }
        return query, variables

    @staticmethod
    def get_floor_areas_for_floor_graphql_query(basking_floor_id):
        """graphql query for get_floor_areas_for_floor function

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.

        :return: graphql query, variables

        """
        query = """
                query readFloorArea(
                        $basking_floor_id: String
                    ){
                        getFloorArea(floorId: $basking_floor_id) {
                            id, 
                            name, 
                            capacity, 
                            geometry, 
                            areaTagId, 
                            tag{id, name}
                        }
                    }
                """
        variables = {
            'basking_floor_id': str(basking_floor_id)
        }
        return query, variables

    @staticmethod
    def get_adjusted_capacity_graphql_query(building_id):
        """graphql query for get_adjusted_capacity function

        :param building_id: building_id
        :type building_id: str.

        :return: graphql query, variables

        """
        query = """
                           query readCapacity($locationId: ID!){
                                getCapacity(locationId: $locationId) {
                                    id,
                                    capacity,
                                    start,
                                    end,
                                    buildingId:locationId,
                                    floorId,
                                    areaId
                                }
                            }
                        """

        variables = {
            'locationId': str(building_id),
        }
        return query, variables

    @staticmethod
    def get_user_buildings_graphql_query():
        """graphql query for get_user_buildings function

        :return: query
        """
        query = """
                    query {
                        viewer{
                            buildings{
                                id, name, address, capacity, timeZone, hasMeraki, lat, lng, organizationId
                                }
                            }
                        }
                """
        return query

    @staticmethod
    def get_location_duration_of_visits_graphql_query(building_id, start_date_str, end_date_str):
        """graphql query for get_duration_of_visits_histogram function

        :param building_id: building_id
        :type building_id: str.
        :param start_date_str: start_date_str
        :type start_date_str: str.
        :param end_date_str: end_date_str
        :type end_date_str: str.

        :return: graphql query, variables

        """
        query = """
                    query duration(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!
                    ) {
                        location(id: $id) {
                            occupancy{
                                duration(
                                    from: $from, 
                                    to: $to
                                ) {
                                    hoursCount, 
                                    clientsCount,
                                    clientsPct
                                }
                            }
                        }
                    }       
                """

        variables = {
            'id': str(building_id),
            'from': str(start_date_str),  # date.strftime("%Y-%m-%dT%H:%M:%SZ")
            'to': str(end_date_str)
        }

        return query, variables

    @staticmethod
    def get_location_frequency_of_visits_graphql_query(building_id, start_date_str, end_date_str):
        """graphql query for get_frequency_of_visits_histogram function

        :param building_id: building_id
        :type building_id: str.
        :param start_date_str: start_date_str
        :type start_date_str: str.
        :param end_date_str: end_date_str
        :type end_date_str: str.

        :return: graphql query, variables

        """
        query = """
                    query duration(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!
                    ) {
                        location(id: $id) {
                            occupancy{
                                daysPerWeek(
                                    from: $from, 
                                    to: $to
                                ) {
                                    daysPerWeek, 
                                    clientsCount
                                }
                            }
                        }
                    }       
                """

        variables = {
            'id': str(building_id),
            'from': str(start_date_str),  # date.strftime("%Y-%m-%dT%H:%M:%SZ")
            'to': str(end_date_str)
        }
        return query, variables

    @staticmethod
    def get_hoteling_by_org_graphql_query(organizationid, start_unix_timestamp, end_unix_timestamp):
        """graphql query for get_hoteling_by_org function

        :param organizationid: organizationid
        :type organizationid: str.
        :param start_unix_timestamp: start_unix_timestamp
        :type start_unix_timestamp: int.
        :param end_unix_timestamp: end_unix_timestamp
        :type end_unix_timestamp: int.

        :return: graphql query, variables

        """
        query = """
                   query getHotelingbyOrg(
                       $id: ID,
                       $startDate: String!, 
                       $endDate: String!
                   ){
                       organization:getOrganization(id: $id){
                           hoteling(startDate: $startDate, 
                                   endDate: $endDate) {
                               from,
                               to,
                               count,
                               country,
                               countryRegion
                           }
                       }
                   }
               """
        variables = {
            'id': str(organizationid),
            'startDate': str(start_unix_timestamp),
            'endDate': str(end_unix_timestamp)
        }
        return query, variables

    @staticmethod
    def get_organization_details_graphql_query(organization_id_str):
        """graphql query for get_organization function

        :param organization_id_str: organizationid
        :type organization_id_str: str.

        :return: graphql query, variables

        """
        query = """
                    query getOrganization(
                        $id: ID
                    ){
                        organization: getOrganization(id: $id) {
                            id, name   
                        }  
                    }
                """
        variables = {
            'id': organization_id_str,
        }
        return query, variables

    @staticmethod
    def get_user_organizations_graphql_query():
        """
        graphql query for get_user_organizations function.

        :return: query.
        """

        query = """
                query {
                    viewer{
                        organizationId, 
                        organizations{
                            id, 
                            name 
                        }
                    }
                }
                """
        return query

    @staticmethod
    def get_location_popular_days_of_visits_graphql_query(
            building_id,
            start_datetime,
            end_datetime

    ):
        """graphql query for get_location_popular_days_of_visits

        :param building_id: building_id
        :type building_id: str.
        :param start_datetime: start_datetime
        :type start_datetime: datetime object.
        :param end_datetime: end_datetime
        :type end_datetime: datetime object.

        :return: graphql query, variables


        """
        query = """
             query popularDays(
                $id: ID!,
                $from: DateTime!,
                $to: DateTime!
            ) {
                location(id: $id) {
                    occupancy{
                        popularDaysOfVisit(
                            from: $from, 
                            to: $to
                        ) {
                            dayOfWeek, 
                            clientsCount,
                            clientsPct
                        }
                    }
                }
            }
        """
        variables = {
            "id": str(building_id),
            "from": str(start_datetime),  # "2022-02-16T23:00:00.000Z"
            "to": str(end_datetime)  # "2022-02-24T09:00:00.000Z"
        }
        return query, variables

    @staticmethod
    def get_organization_frequency_of_visits_graphql_query(organization_id, start_datetime, end_datetime):
        """graphql query for het_frequency_of_visits

        :param organization_id: organization_id
        :type organization_id: str.
        :param start_datetime: start_datetime
        :type start_datetime: datetime object.
        :param end_datetime: end_datetime
        :type end_datetime: datetime object.

        :return: graphql query, variables


        """
        query = """
        query
            getOrgFrequencyOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
            organization: getOrganization(id: $id) {
            frequencyOfVisits(
                from: $from, to: $to) {
                    daysPerWeek,
                    clientCount,
                    percClient,
                    countryRegion
                }
            }
        }
        """

        variables = {
            "id": str(organization_id),
            "from": str(start_datetime),
            "to": str(end_datetime)
        }

        return query, variables

    @staticmethod
    def get_organization_duration_of_visits_graphql_query(organization_id, start_datetime, end_datetime):
        """graphql query for het_frequency_of_visits
        :param organization_id: organization_id
        :type organization_id: str.
        :param start_datetime: start_datetime
        :type start_datetime: datetime object.
        :param end_datetime: end_datetime
        :type end_datetime: datetime object.

        :return: graphql query, variables

        """

        query = """
            query
                getOrgDurationOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
                organization: getOrganization(id: $id) {
                durationOfVisits(
                    from: $from, to: $to) {
                        hPerDay,
                        clientCount,
                        percClient,
                        countryRegion
                     }
                }
            }
        """

        variables = {
            "id": str(organization_id),
            "from": str(start_datetime),
            "to": str(end_datetime)
        }

        return query, variables

    @staticmethod
    def get_insight_graphql_query(
            building_id,
            start_datetime,
            end_datetime
    ):
        """get_insight_data graphql query

        :param building_id: building_id
        :type building_id: str.
        :param start_datetime: start_datetime
        :type start_datetime: datetime object.
        :param end_datetime: end_datetime
        :type end_datetime: datetime object.

        :return: graphql query, variables

        """
        query = """
            query getInsights($id: ID!, $from: DateTime!, $to: DateTime!){
                getBuildingInsights(id: $id, from: $from, to: $to) {
                    buildingId,
                    monthlyRent,
                    capacity,
                    occupancyPeakMax,
                    occupancyPeakMaxPct,
                    occupancyPeakAvgPct,
                    opportunitySeats,
                    opportunitySeatsPct,
                    adjCapacityPct,
                    targetOccupancyPct,
                    opportunitySpace,  // in m2
                    opportunitySpacePct,
                    opportunityPeopleCount,
                    staffAllocationIncrease,
                    currencySymbol,
                    lengthUnits,
                    peopleImpact {
                        occupancyPeakAvgPct,
                        occupancyPeakMaxPct,
                        costSavings,
                        costSavingsStr,
                    }
                     spaceImpact {
                        occupancyPeakAvgPct,
                        occupancyPeakMaxPct,
                        costSavings,
                        costSavingsStr,
                    }
                }
            }
            """
        variables = {
            "id": str(building_id),  # "5a52e94",
            "from": str(start_datetime),  # "2021-11-20T23:00:00.000Z",
            "to": str(end_datetime)  # "2022-02-20T23:00:00.000Z"
        }
        return query, variables

    @staticmethod
    def get_organization_popular_days_of_visits_graphql_query(
            organization_id,
            start_date_str,
            end_date_str
    ):
        """graphql query for get_organization_popular_days_of_visits

        :param organization_id: organization_id
        :type organization_id: str.
        :param start_date_str: start_datetime
        :type start_date_str: datetime object.
        :param end_date_str: end_datetime
        :type end_date_str: datetime object.

        :return: graphql query, variables
        """
        query = """
            query getOrgPopularDaysOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
              organization: getOrganization(id: $id) {
                  popularDaysOfVisits(from: $from, to: $to) { 
                      dayOfWeek,
                      clientsCount,
                      clientsPct,
                      countryRegion
                      }}
        }
        """
        variables = {
            "id": str(organization_id),
            "from": start_date_str,
            "to": end_date_str
        }
        return query, variables

    @staticmethod
    def get_org_locations_graphql_query(organization_id):
        """graphql query for get_org_location

        :param organization_id: organization_id
        :type organization_id: int.

        :return: graphql query, variables
        """
        query = """
        query getOrgLocations($id: Int!) {
        locations: getBuildingsByOrganization(organizationId: $id) {
                  id,
                  name,
                  address,
                  capacity,
                  timeZone,
                  area,
                  rentPriceSQM,
                  organizationId,
                  targetOccupancy,
                  measurementUnits,
                  currency
                  country,
                  countryRegion,
                  hasMeraki,
                  workingDays
                }
              }
        """

        variables = {
            "id": int(organization_id)
        }
        return query, variables
