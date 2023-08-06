#
#   Created by Ryan McDermott
#   Created on 3/16/2022
#

from google.api_core.exceptions import NotFound

from google.cloud import compute_v1
from google.cloud.compute_v1.types import Items
from google.cloud.compute_v1.types import AttachedDisk
from google.cloud.compute_v1.types import ServiceAccount
from google.cloud.compute_v1.types import AccessConfig
from indxdatalaketools import Helpers


class Wrapper:
    ''' Class that wraps the Compute Engine API Client '''
    __compute_engine_instance_client    = None
    __compute_engine_operation_client   = None

    def __init__(self, google_clients):
        self.__compute_engine_instance_client   = google_clients.compute_engine_instance_client
        self.__compute_engine_operation_client  = google_clients.compute_engine_operation_client

    
    def check_if_vm_exists(self, vm_name, zone_id, project_id):
        '''
            Function that checks if a VM exists
            Args:
                vm_name (string): The name of the vm
            Returns:
                boolean: True if the compute engine exists False if otherwise
        '''
        try:
            self.__compute_engine_instance_client.get(
                project=project_id, zone=zone_id, instance=vm_name)
            return True
        except NotFound:
            return False


    def create_disk(self, source_image, disk_size_gb, disk_type, auto_delete, boot, mode):
        ''' 
            Creates a disk instance 
            Args:
                source_image (string): The source image of the disk 
                    (projects/{image-family}/global/images/{image-name})
                disk_size_gb (int): The disk size in GB
                disk_type (string): The disk type (zones/{zone_id}/diskTypes/{disk_type})
                auto_delete (boolean): The flag to set auto delete after instance delete
                boot (boolean): flag to set if this is a boot disk
                mode (string): The mods to set
            Returns:
                google.cloud.compute_v1.types.AttachedDisk: The created disk
        '''
        attached_disk                   = AttachedDisk()
        initialize_params               = compute_v1.AttachedDiskInitializeParams()
        initialize_params.source_image  = source_image
        initialize_params.disk_size_gb  = disk_size_gb
        initialize_params.disk_type     = disk_type
        attached_disk.initialize_params = initialize_params
        attached_disk.auto_delete       = auto_delete
        attached_disk.boot              = boot
        attached_disk.mode              = mode
        
        return attached_disk


    def create_service_account_instance_with_scopes(self, service_account_email, scopes):
        ''' 
            Creates a service account instance with scopes to be used for the VM
            Args:
                service_account_email (string): the service account to authenticate to services
                scopes (list): list of scopes that the VM can use
            Returns:
                google.cloud.compute_v1.types.ServiceAccount: The created resource
        '''
        service_account         = ServiceAccount()
        service_account.email   = service_account_email
        service_account.scopes  = scopes

        # service account must be iterable for compute instance creations
        return service_account


    def create_compute_instance(self, vm_name, metadata, zone_id, machine_type, 
        disks, network_interfaces, service_accounts):
        '''
            Creates a compute engine instance 
            Args:
                vm_name (string): The name of the vm
                metadata (Sequence[Tuple[str, str]]): the vm metadata
                machine_type (string): The machine type
                disks (list[google.cloud.compute_v1.types.AttachedDisk]): The attached disks
                network_interfaces (compute_v1.NetworkInterface): The network interface
                service_account (list[compute_v1.ServiceAccount]): The Service Account
            Returns:
                Instance: The instance we wish to create
        '''
        instance                    = compute_v1.Instance()
        instance.name               = vm_name
        instance.metadata           = metadata
        instance.disks              = disks
        instance.machine_type       = 'zones/'+zone_id +'/machineTypes/' + machine_type
        instance.network_interfaces = network_interfaces
        instance.service_accounts   = service_accounts

        return instance


    def create_insert_instance_request(self, instance, zone_id, project_id):
        '''
            Creates a request instance object for creating a compute engine instance
            Args:
                instance: The instance object we wish to create
            Returns
                compute_v1.InsertInstanceRequest: The request instance we wish to create
        '''
        request                     = compute_v1.InsertInstanceRequest()
        request.zone                = zone_id
        request.project             = project_id
        request.instance_resource   = instance

        return request


    def create_compute_engine_instance_with_request(self, request):
        ''' 
            Creates a compute engine instance with a 
            compute_v1.InsertInstanceRequest instance 
            Args:
                request (compute_v1.InsertInstanceRequest): The request we want to create
            Returns:
                compute_v1.operation: The created operation
        '''
        try:
            return self.__compute_engine_instance_client.\
                insert(request=request)
        except Exception as exception:
            Helpers.print_error('Could not create Compute Engine Instance ' + str(exception))
            return None


    def stop_compute_engine_instance(self, instance_name, zone_id, project_id):
        '''
            Stops a compute engine Instance
            Args:
                instance_name (string): The name of the instance
                zone_id (string): The id of the zone
                project_id (string): The id of the project
            Returns:
                compute_v1.operation|None: The created operation

        '''
        try:
            return self.__compute_engine_instance_client.\
            stop(project=project_id, zone=zone_id, instance=instance_name)
        except Exception as e:
            Helpers.print_error('Failed To Stop instance ' + str(e))
            return None


    def create_default_network_interface(self):
        ''' 
            Creates an empty network interface object and returns it
            Args:
                None
            Returns:
                compute_v1.NetworkInterface
        '''
        network_interface               = compute_v1.NetworkInterface()
        network_interface.network       = 'global/networks/default'
        network_interface.access_configs= [AccessConfig()]
        
        return network_interface


    def wait_for_operation(self, operation, zone_id, project_id):
        ''' 
            Wait for the operation to be completed before returning True 
            Args:   
                operation (compute_v1.operation): the operation we are waiting for
                zone_id (string): The zone id of the operation
                project_id (string): The project id for the operation
            Returns:
                boolean: True if the operation was successful, False if otherwise
        '''
        while operation.status != compute_v1.Operation.Status.DONE:
            operation = self.__compute_engine_operation_client.wait(
                operation=operation.name, zone=zone_id, project=project_id
            )
        if operation.error:
            Helpers.print_error("Error during creation: " +  str(operation.error))
            return False
        if operation.warnings:
            Helpers.print_error("Warning during creation: " + str(operation.warnings))
            return False

        print(operation.name + ': Operation has finished')
        return True

    
    def create_then_stop_compute_instance(self, request, vm_name, zone_id, project_id):
        ''' 
            Function that creates then stops a VM instance
            Args:
                request (compute_v1.InsertInstanceRequest): The request to make a VM instance
                vm_name (string): The name of the VM we wish to create and stop
                zone_id (string): The Id of the zone
                project_id (string): The id of the project
            Returns:
                boolean: True if the instance was created and stopped, 
                    False if otherwise
        '''
        
        if not self.__create_compute_instance(request, zone_id, project_id):
            return False

        return self.__stop_compute_instance(vm_name, zone_id, project_id)

    
    def __create_compute_instance(self, request, zone_id, project_id):
        '''
            Performs logic and checks to create a compute instance
            Args:
                request (compute_v1.InsertInstanceRequest): The request to make a VM instance
                zone_id (string): The Id of the zone
                project_id (string): The id of the project
            Returns:
                boolean: True if the instance was created, 
                    False if otherwise
        '''
        create_operation               = self.\
            create_compute_engine_instance_with_request(request)

        if create_operation is None:
            return False 
        
        if not self.\
            wait_for_operation(create_operation, zone_id, project_id):
            Helpers.print_error('Operation to create VM instance did not complete')
            return False

        return True


    def __stop_compute_instance(self, vm_name, zone_id, project_id):
        '''
            Performs logic and checks to stop a compute instance
            Args:
                vm_name (string): The name of the VM we wish to create and stop
                zone_id (string): The Id of the zone
                project_id (string): The id of the project
            Returns:
                boolean: True if the instance was created, 
                    False if otherwise
        '''
        stop_operation               = self.\
            stop_compute_engine_instance(vm_name, zone_id, project_id)

        if stop_operation is None:
            return False 
        
        if not self.\
            wait_for_operation(stop_operation, zone_id, project_id):
            Helpers.print_error('Operation to stop VM instance did not complete')
            return False

        return True


    def create_metadata_item(self, key, value):
        '''
            Creates a metadata item for the backup compute engine
            Args:
                key (string): The key to the metadata
                value (string): The value to the key / value pair for the metadata
            Returns:
                google.cloud.compute_v1.types.Items: metadata item for client id
        '''
        item                    = Items()
        item.key                = key
        item.value              = value

        return item


    def create_metadata_item_from_file(self, key, file_path):
        '''
            Creates a metadata item from a file for the backup compute engine
            Args:
                key (string): The key to the metadata
                file_path (string): The path to the file we want to set as metadata
            Returns:
                google.cloud.compute_v1.types.Items: metadata item for client id
        '''
        item                    = Items()
        item.key                = key
        item.value              = self.__get_contents_from_file(file_path)

        return item


    def __get_contents_from_file(self, file_path):
        ''' 
            reads the contents of a file from the filepath and returns them
            Args:
                file_path (string): The path to the file we want to read
            Returns:
                string: The contents of the file
        '''
        with open(file_path, "r", encoding='utf-8') as file:
            return file.read()


