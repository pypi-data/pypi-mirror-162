

import datetime
import re
from indxdatalaketools import Helpers

from indxdatalaketools.DataLakeGlobals import DATE_REGEX


def validate_date(date):
        '''
            Validates the date
            Args:
                date (string): The date
            Returns:
                boolean: True if the date is valid, false if otherwise
        '''
        if re.fullmatch(DATE_REGEX, date) is None:
            print(date + ' does not match date regex: not a valid date')
            return False
        
        # check if valid date
        year    = int(date[:4])
        month   = int(date[4:6])
        day     = int(date[6:8])
        
        if __is_valid_date(year, month, day):
            return True

        Helpers.print_error(date + ' is not a valid date')
        return False

    
def __is_valid_date( year, month, day):
    '''
        checks if the year month and day creates a valid date
        Args:
            year    (string): The year
            month   (string): The month
            day     (string): the day
        Returns:
            boolean: True if a valid date is formed False if other wise
    '''
    try:
        datetime.datetime(year, month, day)
        return True
    except:
        return False


