#
#   Created By Ryan McDermott
#   Created on 2/22/2022
#

from indxdatalaketools import Helpers
from indxdatalaketools.ArgumentValidation import ValidationHelpers
from indxdatalaketools.PropertiesDBApi import Properties

HL7_SEX             = ["F", "M", "O", "U"]
HL7_FYR_SEX         = ["female", "male", "other", "unknown"]


class Validator():
    '''
        Class that helps validate the fields in the patient data passed by the client
    '''

    client_uuid                         =  ''
    patients_command                    =  ''
    arguments                           = {}

    __patient_data_validation_functions = None

    def __init__(self):
        '''
            initializes the Patient Data Validator
        '''
        self.__set_up_client_id_validation_functions()


    def __set_up_client_id_validation_functions(self):
        '''
            Sets up the mapping from the arguments passed in patient_data 
            to the function that will validate the given field
            Args:
                None
            Returns:
                None
        '''
        self.__patient_data_validation_functions = {
            'CLIENT_ID': self.__validate_client,
            'MRN': self.__validate_mrn,
            'PATIENT_ID': self.__validate_patient_id,
            'FIRSTNAME': self.__validate_name,
            'MIDDLENAME': self.__validate_name,
            'LASTNAME': self.__validate_name,
            'DOB': ValidationHelpers.validate_date,
            'SEX': self.__validate_sex,
            'RACE': self.__validate_race
        }


    def validate(self, patient_data, arguments):
        '''
            Validates the patient data
            Args:
                patient_data: structure or file containing one or more patients
                    data
            Returns:
                boolean: True if all Patients have valid data, False if otherwise
        '''
        self.client_uuid        = arguments['client_id']
        self.arguments          = arguments

        json_structure = Helpers.determine_json_structure(patient_data)

        if isinstance(json_structure, list):
            return self.__validate_multiple_patients_data_json(json_structure)

        return self.__validate_patient_data_json(json_structure)
    

    def __validate_multiple_patients_data_json(self, json_structure):
        '''
            Verifies multiple patients data passed by the client
            Args:
                json_structure (list[dict]): list of patient data
            returns:
                boolean: True if all patients' data is valid
        '''
        for i in json_structure:

            if not self.__validate_patient_data_json(i):
                return False
            
        return True


    def __validate_patient_data_json(self, patient_data):
        '''
            Verifies that the json passed contains valid attributes
            Args:
                None
            Returns:
                boolean: True if the patient data is valid, False if otherwise
        '''
        if 'MRN' not in patient_data or 'CLIENT_ID' not in patient_data:
            Helpers.print_error("required fields MRN or CLIENT_ID is missing")
            return False

        for field in patient_data:
            if not self.__validate_field_in_patient_data(field, patient_data):
                return False

        return True
        

    def __validate_field_in_patient_data(self, field, patient_data):
        '''
            Validates a given fields in the patient data json structure
            Args:
                field           (string): The field we are going to validate
                patient_data    (dict): The dictionary of the patient data
            Returns:
                boolean: True if the field value is valid, False if otherwise
        '''
        # special case for PATIENT_ID because it requires multiple fields to check
        # its validity

        if field == 'PATIENT_ID':
            return self.__validate_patient_id(patient_data)

        return self.__patient_data_validation_functions[field](patient_data[field])

    
    def __validate_client(self, client):
        '''
            Validates that the Client id passed is the same as the client_id in the 
            json object
            Args:
                None
            Returns:
                boolean: True if the bucket exists, False if otherwise
        '''
        if client != self.client_uuid:
            Helpers.print_error("Invalid CLIENT_ID " + client + ": Bad Request")
            return False

        return True


    def __validate_mrn(self, mrn):
        '''
            Validates that the MRN only contains digits and letters
            Args:
                None
            Returns:
                boolean: True if the MRN is valid, False if otherwise
        '''
        if all(character.isalpha() or character.isdigit() or \
            character == '-' for character in mrn):
            return True
        
        Helpers.print_error(mrn + " is not a valid MRN: Does Not contain only letters, digits and hyphens")
        return False


    def __validate_patient_id(self, patient_data):
        '''
            Validates that the hash of the mrn and the client ID is the patient ID that was 
            passed
            Args:
                patient_data (dict): The dictionary containing all of the patients information
            Returns:
                boolean: True if the patient_id is valid, False if otherwise
        '''
        expected_patient_id = Helpers.patient_hash(patient_data["CLIENT_ID"], 
            [patient_data["MRN"]])[0]

        if expected_patient_id != patient_data["PATIENT_ID"]:
            Helpers.print_error('the Patient ID passed is not valid: Bad Request')
            return False
        
        return True


    def __validate_name(self, name):
        '''
            Validates a first, last, or middle name of a patient. This includes checking for only 
            letters and spaces
            Args:
                name (string): the name that we wish to pass
            Returns:
                boolean: True if the name is valid, False if otherwise
        '''
        if all(character.isalpha() or character.isspace() for character in name):
            return True
        
        Helpers.print_error(name + " is not valid: Does Not contain only letters and spaces")
        return False


    def __validate_race(self, race):
        '''
            function that checks the race of a patient. Race should be identified 
            using the appropriate HL7 code represented as a string.  
            e.g. 1014-0 (Lipan Apache) should be represented as the string literal 1014-0. 
            Args:
                race (string): The HL7 code for race
            Returns:
                boolean: True if race is a valid HL7 code and false if other wise
        '''
        if race in Properties.Properties.instance().race_codes:
            return True
        
        Helpers.print_error("Race " + race + " is not a HL7 race code")
        return False


    def __validate_sex(self, sex):
        '''
            function that checks the sex of a patient. Sex is defined as 
            the administrative gender using the appropriate HL7 code represented as a string.  
            F for female, M for male, and UN for undifferentiated. 
            Args:
                sex (string): The HL7 code for sex
            Returns:
                boolean: True if race is a valid HL7 code and false if other wise
        '''
        if sex in HL7_SEX or sex in HL7_FYR_SEX:
            return True
        
        Helpers.print_error("sex " + sex + " is not a HL7 sex code")
        return False
