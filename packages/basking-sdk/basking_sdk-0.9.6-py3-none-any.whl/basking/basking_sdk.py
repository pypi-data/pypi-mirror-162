# pylint: disable=line-too-long, import-error, invalid-name
"""
Basking.io — Python SDK
"""

import logging
import os
import re
from datetime import datetime

import boto3
import botocore
from botocore.config import Config
from pytz import timezone

from constant import (
    BASKING_API_URL,
    TIMEOUT_MESSAGE
)
from .graphql_query import GraphqlQuery
from .insight import Insight
from .location import Location
from .occupancy import Occupancy
from .organization import Organization

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class Basking:
    """ Class Basking
    """

    def __init__(self, *args, **kwargs):
        # Setting the logger
        self.basking_api_url = BASKING_API_URL
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Started Basking SDK in debugging level using %s', self.basking_api_url)

        # cognito
        self.auth_type = 'env_variables'
        config = Config(signature_version=botocore.UNSIGNED)
        self._boto3_client = boto3.client('cognito-idp', os.getenv('BASKING_AWS_REGION', 'eu-central-1'), config=config)
        #   occupancy object
        self.occupancy = Occupancy(basking_obj=self)
        #   location object
        self.location = Location(basking_obj=self)
        #   organization object
        self.organization = Organization(basking_obj=self)
        #   graphql_query object
        self.graphql_query = GraphqlQuery(basking_obj=self)
        #   insight object
        self.insight = Insight(basking_obj=self)

    def date_obj_to_timestamp_ms(self, date_obj, tz_str):
        """
        converts a date obj into a dateobj with timezone and then into ms for the api

        :param date_obj: datetime object
        :type date_obj: datetime object.
        :param tz_str: timezone
        :type tz_str: str.

        :return: converted datetime in ms
        """

        try:
            tz = timezone(tz_str)
            date_obj_tz = tz.localize(date_obj)
            timestamp = int(date_obj_tz.timestamp())
            self.log.debug('got %s for %s in tz=%s', timestamp, date_obj, tz_str)
            return timestamp
        except Exception as e:
            print(f"error in data_obj_timestamp -- > {e}")
            self.log.error('error on timezone for %s', tz_str)

    # Internal Methods
    @staticmethod
    def check_if_datetime_obj_tz_aware(dateobject):
        """
        check datetime is aware

        :param dateobject: date_time object
        :type dateobject: datetime object.

        :return: True or False
        """

        if dateobject.tzinfo and dateobject.tzinfo.utcoffset(dateobject):
            return True
        return False

    def _cognito_login_password_auth_(self):
        """
        internal method to authenticate the user.

        :return: return response
        """
        response = self._boto3_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': os.environ['BASKING_USERNAME'],
                'PASSWORD': os.environ['BASKING_USER_PASSWORD']
            },
            ClientId='7o5vqv7ukt9onolq1nvjt7m40e'  # add the dashboard auth.
        )

        return response

    def api_timeout_handler(self, api_data):
        """
        for handle api timeout error coming from graphql_query

        :param api_data: api_data
        :type api_data: dict

        :return: error message

        """
        if 'message' in api_data:
            if api_data['message'] == 'Endpoint request timed out':
                self.log.error(api_data['message'])
                return TIMEOUT_MESSAGE

    def get_new_cognito_token_(self):
        """
        Internal method to get new cognito token

        :return: return new token
        """

        # return cognito_login()
        return self._cognito_login_password_auth_(
        )['AuthenticationResult']['IdToken']

    def basking_handle_api_return_errors(self, api_return_data):
        """
        checks if there are errors in the return from the API

        :param api_return_data: api return data
        :type api_return_data: dict

        :return: TRUE if has error
        """

        has_errors = False
        if 'errors' in api_return_data:
            self.log.error('Error in query:')
            self.log.error(api_return_data['errors'])
            has_errors = True
        return has_errors

    def get_timestamp_from_date_inputs(
            self,
            start_obj_tz_aware=None,
            end_obj_tz_aware=None,
            start_obj_tz_unaware=None,
            end_obj_tz_unaware=None,
            start_unix_timestamp=None,
            end_unix_timestamp=None,
            building_id=None
    ):
        """
        convert datetime to timestamp object

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
        :param end_unix_timestamp: Old way of passing start date as seconds since epoch
        :type end_unix_timestamp: int.

        :return: this function returns the timestamp for aware or unaware date objects.
        """

        # checks
        if isinstance(start_obj_tz_aware, datetime) & isinstance(end_obj_tz_aware, datetime):
            if self.check_if_datetime_obj_tz_aware(start_obj_tz_aware) & self.check_if_datetime_obj_tz_aware(
                    end_obj_tz_aware):
                self.log.debug(
                    'using the date objects: start_obj_tz_aware=%s and end_obj_tz_aware=%s',
                    start_obj_tz_aware,
                    end_obj_tz_aware
                )
                start_unix_timestamp = int(start_obj_tz_aware.timestamp())
                end_unix_timestamp = int(end_obj_tz_aware.timestamp())
            else:
                raise ValueError('start_obj_tz_aware and end_obj_tz_aware must be tz aware datetime objects')
        elif isinstance(start_obj_tz_unaware, datetime) & isinstance(end_obj_tz_unaware, datetime):
            if not self.check_if_datetime_obj_tz_aware(start_obj_tz_unaware) \
                    and not self.check_if_datetime_obj_tz_aware(end_obj_tz_unaware):
                self.log.debug('using the date objects: start_obj_tz_unaware=%s and end_obj_tz_unaware=%s',
                               start_obj_tz_unaware, end_obj_tz_unaware)
                building = self.location.get_building(building_id=building_id)
                tz = timezone(building['data']['getBuilding']['timeZone'])
                start_obj_tz_aware = tz.localize(start_obj_tz_unaware)
                end_obj_tz_aware = tz.localize(end_obj_tz_unaware)
                start_unix_timestamp = int(start_obj_tz_aware.timestamp())
                end_unix_timestamp = int(end_obj_tz_aware.timestamp())
            else:
                raise ValueError('start_obj_tz_unaware and end_obj_tz_unaware must be tz UNaware datetime objects')
        else:
            if isinstance(start_unix_timestamp, int) & isinstance(end_unix_timestamp, int):
                self.log.warning('''using deprecated timestamps. Pls consider updating your code to use 
                start_obj_tz_aware and end_obj_tz_aware. start_unix_timestamp and end_unix_timestamp 
                will be deprecated in the future.''')
            else:
                raise ValueError('start_obj_tz_aware and end_obj_tz_aware must be objects')
        return start_unix_timestamp, end_unix_timestamp
