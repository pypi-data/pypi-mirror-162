"""this code shows an example of how to use the Basking SDK"""
# pylint: disable=import-error, invalid-name
# imports
from datetime import datetime
import logging
from basking_sdk import Basking

# set the default logging
logging.basicConfig()

# mofify the required level of logging for Basking
logging.getLogger('Basking').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.INFO)

# initialize the SDK and set general query parameters
basking = Basking()

# list buildings the current user has access to
df_buildings = basking.location.get_user_buildings(pandify=True)
# print(df_buildings)

building_id = '6210079'  # <-- set the building ID from the basking URL or the index of df_buildings
organization_id = '92'
start_date_obj = datetime(2022, 6, 5, 0, 0, 0)  # <-- starting date for the query
end_date_obj = datetime(2022, 6, 18, 0, 0, 0)  # <-- ending date for the query
# Format of the dates: year, month, day, hour, minute, second

# execute all function one by one

# get building meta data
building_meta_data = basking.location.get_building(
    building_id=building_id
)
tz_str = building_meta_data['data']['getBuilding']['timeZone']


# get building daily occupancy statistics
df_daily = basking.occupancy.get_building_occupancy_stats_daily(
    building_id=building_id,
    start_obj_tz_unaware=start_date_obj,
    end_obj_tz_unaware=end_date_obj,
    pandify=True
)
df_daily.to_csv('./df_daily.csv')
print(f"""- exported daily occupancy data with a length of {len(df_daily)} entries""")

# print(df_daily.head())

# get building hourly occupancy statistics
df_hourly = basking.occupancy.get_building_occupancy_hourly(
    building_id=building_id,
    start_obj_tz_unaware=start_date_obj,
    end_obj_tz_unaware=end_date_obj,
    pandify=True
)

# df_hourly.to_csv('./df_hourly.csv')
print(f"""- exported hourly occupancy data with a length of {len(df_hourly)} entries""")
# print(df_hourly)

# get the occupancy by floor
df_hourly_floors = basking.occupancy.get_building_occupancy_hourly_by_floor(
    building_id=building_id,
    start_obj_tz_unaware=start_date_obj,
    end_obj_tz_unaware=end_date_obj,
)
# df_hourly_floors.to_csv('./df_hourly_floors.csv')
print(f"- exported hourly occupancy data by floor with a length of {len(df_hourly_floors)} entries")
# print(df_hourly_floors)

df_floors_meta_data = basking.location.get_floors(building_id=building_id)
# df_floors_meta_data.to_csv('./df_floors_meta_data.csv')
print(f"""- exported floor meta info for {len(df_floors_meta_data)} floors""")

# get the occupancy by area
df_hourly_areas = basking.occupancy.get_building_occupancy_hourly_by_floor_area(
    building_id=building_id,
    start_obj_tz_unaware=start_date_obj,
    end_obj_tz_unaware=end_date_obj,
)

print(f"""- exported hourly occupancy data by areas with a length of {
len(df_hourly_areas)
} entries and {
len(df_hourly_areas.floor_area_id.unique())
} unique areas""")
# df_hourly_areas.to_csv('./df_hourly_areas.csv')


df_areas_meta_data = basking.location.get_floor_areas_for_building(
    building_id=building_id
)
print(f"""- exported areas meta data with {len(df_areas_meta_data)} areas""")
# df_areas_meta_data.to_csv('./df_areas_meta_data.csv')


# get the density of the last 7 days
days = 7

density_last_week = basking.occupancy.get_density_for_building_last_days(
    building_id=building_id,
    days=days
)

print(f"""the density for building {building_id} over the last {days} days is
 {density_last_week:.1f} RSM/Person at Peak.""")

# get the density between dates
density_dates = basking.occupancy.get_density_for_building(
    building_id=building_id,
    start_unix_timestamp=basking.date_obj_to_timestamp_ms(start_date_obj, tz_str),
    end_unix_timestamp=basking.date_obj_to_timestamp_ms(end_date_obj, tz_str)
)
print(f"""the density for building {building_id} between {start_date_obj} and {end_date_obj} is
 {density_last_week:.1f} RSM/Person at Peak.""")

# Rank locations by occupancy
df_loc_ranking = basking.organization.locations_rank_by_occupancy(
    organization_id=organization_id,
    start_obj_tz_unaware=start_date_obj,
    end_obj_tz_unaware=end_date_obj,
    ranking_metric='average_daily_peak_pct',
    pandify=True
)
