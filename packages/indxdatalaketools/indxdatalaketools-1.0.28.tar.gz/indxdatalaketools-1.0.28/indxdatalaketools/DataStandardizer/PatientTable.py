#
#   Created by Ryan McDermott
#   Created on 2/22/2022
#

import datetime
import sys
import hashlib
import json
from indxdatalaketools import Helpers

HL7_SEX_MAP         = {"F":"female","M":"male","O":"other","U":"unknown",
                        "female":"female","male":"male","other":"other","unknown":"unknown"}


class Client():
    '''
        Creates Big query readable dictionary for the PATIENT table
    '''
    def __init__(self):
        pass
    

    def standardize(self, patient_data):
        '''
            Standardizes the patient json data to a form used by the 
            patients table API
            Args:
                patient_data (string|dict): Converts the data to a dictionary used by 
                PATIENT table API
            Returns:
                dict: Dictionary containing all fields in PATIENT schema, if the fields does
                    does not exist it is set to NONE
        '''
        json_structure = Helpers.determine_json_structure(patient_data)

        if isinstance(json_structure, list):
            return self.__standardize_multiple_patients_data_json(json_structure)

        return self.__standardize_patient_data(json_structure)


    def __standardize_multiple_patients_data_json(self, json_structure):
        '''
            Verifies multiple patients data passed by the client
            Args:
                json_structure (list[dict]): list of patient data
            returns:
                boolean: True if all patients' data is valid
        '''
        standardized_patients = []

        for patient in json_structure:

            standardized_patient_data = self.__standardize_patient_data(dict(patient))
            standardized_patients.append(standardized_patient_data)

        return standardized_patients

    
    def __standardize_patient_data(self, patient_data):
        '''
            converts all missing fields in patient data to None, updates the date format,
            and removes all extra fields in patient data
            Args:
                patient_data (dict):Dictionary of patient Data
            Returns:
                patient_data (dict):Dictionary of patient Data
        '''
        patient_data = self.__set_patient_id(patient_data)

        patient_data = self.__update_missing_fields_to_none(patient_data)

        patient_data = self.__remove_all_extra_fields_from_json(patient_data)

        patient_data = self.__convert_hl7_sex_code(patient_data)

        patient_data = self.__transform_date(patient_data)

        return self.__create_checksum(patient_data)
        

    def __set_patient_id(self, patient_data):
        '''
            checks if the PATIENT_ID exists if not it is created, if MRN and CLIENT_ID
            do not exist the program exits
            Args:
                patient_data (dict): Dictionary of patient Data
            Returns:
                patient_data (dict): Dictionary of patient Data
        '''
        if "PATIENT_ID" not in patient_data:
            patient_data["PATIENT_ID"] = Helpers.patient_hash(patient_data["CLIENT_ID"], 
            [patient_data["MRN"]])[0]

        return patient_data


    def __update_missing_fields_to_none(self, patient_data):
        '''
            converts all missing fields in patient data to None, updates the date format,
            and removes all extra fields in patient data
            Args:
                patient_data (dict):Dictionary of patient Data
            Returns:
                patient_data (dict):Dictionary of patient Data
        '''
        patients_schema     = ["CLIENT_ID","MRN","LASTNAME",
        "FIRSTNAME","PATIENT_ID","MIDDLENAME","DOB","SEX","RACE" ]

        for key in patients_schema:
            if key not in patient_data:
                patient_data[key] = None

        return patient_data

    def __convert_hl7_sex_code(self, patient_data):
        '''
            Converts the HL7 sex code if it is not in the right format 
            Args:
                patient_data (dict):Dictionary of patient Data
            Returns:
                patient_data (dict):Dictionary of patient Data
        '''
        if patient_data['SEX'] is None:
            return patient_data

        patient_data['SEX'] = HL7_SEX_MAP[patient_data['SEX']]
        return patient_data


    # Reviewers: Is there a better way to implement this logic?
    # cannot loop through a list and remove items while you loop
    def __remove_all_extra_fields_from_json(self, patient_data):
        '''
            Function that removes all fields from the json dictionary if
            they are not part of the PATIENTS table schema
            Args:
                patient_data (dict):Dictionary of patient Data
            Returns:
                None
        '''
        remove_arr          = []
        patients_schema     = ["CLIENT_ID","MRN","LASTNAME",
        "FIRSTNAME","PATIENT_ID","MIDDLENAME","DOB","SEX","RACE" ]

        for k in patient_data:
            if k not in patients_schema:
                remove_arr.append(k)
               
        for k in remove_arr:
            patient_data.pop(k, None)

        return patient_data


    def __create_checksum(self, patient_data):
        '''
            Create an MD5 checksum field in the dictionary 
            Args:
                patient_data (dict): The dictionary containing the patients data
            Returns:
                dict: The updated dictionary
        '''
        dhash = hashlib.md5()
        encoded = json.dumps(patient_data, sort_keys=True).encode()
        dhash.update(encoded)
        patient_data['CHECKSUM'] = dhash.hexdigest()
        return patient_data

    
    def __transform_date(self, patient_data):
        '''
            Create a data time using the passed paramaters
            Args:
                patient_data (dict): The dictionary containing the patients data
            Returns:
                boolean: True if the datetime was successfully created, False
                    if otherwise
        '''
        if patient_data['DOB'] is None:
            return patient_data

        year    = int(patient_data["DOB"][:4])
        month   = int(patient_data["DOB"][4:6])
        day     = int(patient_data["DOB"][6:8])

        patient_data['DOB'] = self.__create_datetime_date_from_dob(year, month, day)

        return patient_data


    def __create_datetime_date_from_dob(self, year, month, day):
        '''
            Creates a date time data object from the year month and day passed
            Args:
                year    (string): The year
                month   (string): The month
                day     (string): The day
            Returns:
                The correctly Formatted date
        '''
        try:
            date = datetime.date(year, month, day)
            return str(date)        
        except:
            Helpers.print_error("Date is not a valid date: Bad Request")
            sys.exit(1)