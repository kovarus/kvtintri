"""

    Helper library used to manage Tintri VMstore devices via python. Use this for generating reports and automating
    actions on large numbers of virtual machines.

    This library gets updated as needed to support use cases. Apologies for any messes in the code!

"""

import requests
import json
import kvtintri.exceptions

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError:
    pass

class TintriBase(object):
    """This is here because it might be a good idea to have a base class for everything to inherit from"""
    pass

class VMStore(object):
    """

        This class is used to create a session with a Tintri VMstore appliance.

        This class should be instantiated via the @classmethod.

    """
    # TODO could probably just ditch the classmethod entirely and do it all through instantiation

    def __init__(self, device, user, session, api_version, ssl_verify):
        """
        VMStore class initializer. The class itself should only be instantiated via the login @classmethod.

        :param device:
        :param user:
        :param session:
        :param api_version:
        """
        self.device = device
        self.user = user
        self.session = session
        self.api_version = api_version
        self.headers = {'Content-Type': 'application/json',
                        'cookie': 'JSESSIONID=' + self.session}
        self.ssl_verify = ssl_verify

    @classmethod
    def login(cls, device, user, password, ssl_verify=False):
        """
        Used to construct the VMstore class and create the necessary headers for additional requests.

        Sample usage:
            # Log into a Tintri VMstore with the admin credentials

            import kvtintri

            session = kvtintri.VMStore.login(device="10.25.36.10", username="admin", password="secret!")

        :param device: A string containing the FQDN or IP address of a Tintri VMstore appliance.
        :param user: A string containing the username of an administrator on the VMstore appliance.
        :param password: A string containing the password for the user supplied.
        :param ssl_verify: A boolean that enables or disables SSL certificate validation. By default it is disabled.
        :return: Returns the session cookie to be used in subsequent requests.
        """

        api_version = 'v310'

        if not ssl_verify:
            try:
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            except AttributeError:
                pass

        headers = {'Content-Type': 'application/json'}
        payload = {'username': user,
                   'password': password,
                   'typeId': 'com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials'}

        url = "https://{}/api/{}/session/login".format(device, api_version)

        try:
            r = requests.post(url,
                              data=json.dumps(payload),
                              headers = headers,
                              verify = ssl_verify)

            session = r.cookies['JSESSIONID']

            return cls(device, user, session, api_version, ssl_verify)

        except requests.exceptions.RequestException as e:
            #TODO add proper exception handling here
            pass

    def logout(self):
        """
        Used to invalidate a session cookie.

        :return: The response from the webserver if needed.
        """

        url = "https://{}/api/{}/session/logout".format(self.device, self.api_version)

        try:
            r = requests.get(url,
                             headers = self.headers,
                             verify = self.ssl_verify)

            return r
        except requests.exceptions.RequestException:
            pass

    def _request(self, uri, request_method='GET', payload=None, **kwargs):
        """

        Generic request method to be invoked by other methods within this class.

        :param url: String - URL and URI for the API call
        :param request_method: String - Either 'PUT', 'POST', or 'GET'. This parameter will default to 'GET'
        :param payload: - dict of data to be used in the 'PUT' or 'POST'
        :param kwargs:
        :return: dict of response from the webserver.
        """

        url = "https://{}/api/{}/{}".format(self.device, self.api_version, uri)

        if request_method == "PUT" or "POST" and payload:
            payload = json.dumps(payload)
            r = requests.request(request_method,
                                 url=url,
                                 headers=self.headers,
                                 verify=self.ssl_verify,
                                 data=payload)
            # TODO Add exception handling here

            return r.content

        elif request_method == "GET":
            r = requests.request(request_method,
                                 url=url,
                                 headers=self.headers,
                                 verify=self.ssl_verify)
            result = json.loads(r.content)

            if type(result) == list:
                for i in result:
                    if i["typeId"] == "com.tintri.api.rest.v310.dto.domain.beans.TintriError":
                        raise kvtintri.exceptions.TintriError(message=result["message"], code=result["code"])
            else:
                if result["typeId"] == "com.tintri.api.rest.v310.dto.domain.beans.TintriError":
                    raise kvtintri.exceptions.TintriError(message=result["message"], code=result["code"])

            return json.loads(r.content)
        else:
            raise kvtintri.exceptions.InvalidRequestMethod(
                "Invalid request method. It must be either 'PUT', 'POST' or 'GET'. Request method called was: ",
                request_method)

    def _filter(self, **kwargs):
        """Generic filter function to allow you to filter on various REST API object properties"""

        filters = "?"
        if len(kwargs) >= 2:
            for i in kwargs.keys():
                filters = filters + i + "=" + kwargs[i] + "&"
            return filters
        else:
            for i in kwargs.keys():
                filters = filters + i + "=" + kwargs[i]
            return filters

    def get_virtualdisks(self, **kwargs):

        if kwargs:
            resource = self._filter(**kwargs)
            url = 'virtualDisk' + resource
            return self._request(url)
        else:
            return self._request('vm')

    def get_virtualdisk(self):
        """
        Retrieves all of the virtual disks and returns a python dictionary with the output.

        :param tintri: The tintri VMStore appliance that you're getting the data from
        :return: A python dictionary that contains the JSON payload

        """
        return self._request('virtualDisk')

    def get_vms(self, **kwargs):
        """
        Retrieves all virtual machines on the Tintri VMstore and returns a python dictionary with the output
        Supports filtering output via a number of optional keyword arguments.

         Sample usage:
            # Log into a Tintri VMstore with the admin credentials

            import kvtintri

            session = kvtintri.VMStore.login(device="10.25.36.10", username="admin", password="secret!")

            session.get_vms(from_name="my_vm_name")

            # You can also retrieve all VMs matching a specific pattern:

            session.get_vms(name="foo-")

            # Returns all virtual machines that have foo- in the name

        If invoking via VirtualMachine.from_name() classmethod then it's recommended to be as specific as possible,
        otherwise it will just return a list of dictionaries.

        Supports some of the following options as kwargs:
        name - a string containing all or part of the name of a virtual machine:

            session.get_vms(name="foo-") # returns all VMs with "foo-" in the name

        isPowered - A string containing either True or False that will return matching virtual machines

            session.get_vms(isPowered="False") # returns all virtual machines where the power state is off

        vcenterName - A string containing all or part of the name of the vCenter housing the virtual machine

            session.get_vms(vcenterName="dev-vc1") # Returns all of the VMs connected to dev-vc1

        host - Retrieve a list of virtual machines on the matching host

            session.get_vms(host="dev-esxi12")

        :parameter **kwargs: An optional parameter that allows filtering on any number of attributes.
        :return: A python dictionary containing the results of the query

        """

        if kwargs:
            resource = self._filter(**kwargs)
            url = 'vm' + resource
            return self._request(url)
        else:
            return self._request('vm')

    def get_vm(self, vm_id):
        """Retrives an individual VM based on passed in string for 'vm_id'"""
        uri = 'vm/' + vm_id
        return self._request(uri=uri)

    def set_qos(self, payload):
        """
        Used to update QoS values on a given virtual machine. QoS values are given as 'minNormalizedIops' and
        'maxNormalizedIops.' These values should be an integer and they'll need to be stored with a typeId in the payload
        variable.

        This method should generally be invoked via the VirtualMachine.update_qos() method.

        :param tintri:  The tintri VMStore appliance that you're modifyng QoS info on
        :param payload: JSON payload that includes the name of the VM and QoS parameters to configure
        :return: The server response code
        """
        uri = 'vm/qosConfig'
        return self._request(uri=uri, request_method='PUT', payload=payload)

    def get_datastores(self):
        """Get all of the datastores on the Tintri VMStore"""
        return self._request('datastore')

    def get_datastore(self, datastore_uuid='default'):
        """Returns a dictionary for the given datastore passed as a string"""
        # uri = 'datastore/' + str(datastore_uuid)
        uri = 'datastore/'
        return self._request(uri=uri)

    def get_appliances(self):
        """Returns a list containing information about the hardware appliances visible to the endpoint"""
        return self._request('appliance')

    def get_appliance(self, appliance_uuid='default'):
        """Returns a specific appliance"""
        uri = 'appliance/{}'.format(appliance_uuid)
        return self._request(uri)

    def get_service_groups(self):
        """Get all of the service groups on the Tintri VMStore"""
        return self._request('servicegroup')

    def get_service_group(self, service_group_uuid):
        """Returns a specific service group"""
        uri = 'servicegroup/' + service_group_uuid
        return self._request(uri=uri)

    def get_realtime_datastore_performance(self, uuid):
        uri = 'datastore/'
        return self._request(uri=uri)


    def get_view(self, view, request_method='GET', payload=None):
        """
        Generic method for collecting data from REST calls that haven't been implemented in this library yet

        :param view: A string containing the API resource you want to access
        """
        return self._request(view, request_method, payload)

    def __test__request_exception(self):
        return self._request('bogusUri', request_method='BLARG')

class Datastore(object):
    """

    Provides an interface to collect information about a given datastore. This can be used to determine capacity,
    performance and cache hit rate.


    Should be invoked via .get @classmethod. Requires a tintri session object to work.

    Sample usage:
            # Log into a Tintri VMstore with the admin credentials

            import kvtintri

            session = kvtintri.VMStore.login(device="10.25.36.10", username="admin", password="secret!")

            my_datastore = kvtintri.Datastore.get(session)

            # access attributes and properties
            print my_datastore.total_space_gib
            print my_datastore.space_free_percentage
            print my_datastore.performance_reserve_remaining

    """
    ### CLASS NO LONGER APPEARS TO BE WORKING
    ###

    def __init__(self, datastore):
        self.space_used_gib = datastore['stat']['spaceUsedGiB']
        self.performance_reserve_remaining = datastore['stat']['performanceReserveRemaining']
        self.performance_reserve_used = datastore['stat']['performanceReserveUsed']
        self.total_space_gib = datastore['stat']['spaceTotalGiB']
        self.space_used_gib = datastore['stat']['spaceUsedGiB']
        self.flash_hit_percentage = datastore['stat']['flashHitPercent']
        self.space_remaining_physical = datastore['stat']['spaceRemainingPhysicalGiB']
        self.space_used_physical_gib = datastore['stat']['spaceUsedPhysicalGiB']
        self.uuid = datastore['uuid']['uuid']
        self.storage_containers = datastore['storageContainers']

    @property
    def space_used_percentage(self):
        return (self.space_used_gib / self.total_space_gib) * 100

    @property
    def space_free_percentage(self):
        return 100 - ((self.space_used_gib / self.total_space_gib) * 100)

    def get_realtime_performance(self, session):
        return session.get_realtime_datastore_performance(self)


    @classmethod
    def get(cls, session, datastore_uuid=None):
        datastore = session.get_datastore(datastore_uuid)
        return cls(datastore)

class VirtualMachine(object):
    '''

        It may be handy in the future to store instances of virtual machines to retrieve other bits of data
        This should probably leverage super to use VMStore as parent class

    '''
    # TODO learn more about @property to avoid getters/setters
    # TODO consider @property for QoS params

    def __init__(self, virtualmachine, virtual_disks=None):
        self.typeid = virtualmachine['typeId']
        self.uuid = virtualmachine['uuid']['uuid']
        self.vcenter = virtualmachine['vmware']['vcenterName']
        self.name = virtualmachine['vmware']['name']
        self.power_state = virtualmachine['vmware']['isPowered']
        self.is_template = virtualmachine['vmware']['isTemplate']
        self.hypervisor = virtualmachine['vmware']['hypervisorType']

        if 'vcenterName' in virtualmachine['vmware'].keys():
            self.vcenter = virtualmachine['vmware']['vcenterName']

        if 'mor' in virtualmachine['vmware'].keys():
            self.moref = virtualmachine['vmware']['mor']

        if 'storageContainers' in virtualmachine['vmware'].keys():
            self.storage_containers = virtualmachine['vmware']['storageContainers']

        if 'qosConfig' in virtualmachine.keys():
            self.qos_max_iops = virtualmachine['qosConfig']['maxNormalizedIops']
            self.qos_min_iops = virtualmachine['qosConfig']['minNormalizedIops']
            self.qos_typeid = virtualmachine['qosConfig']['typeId']
        else:
            self.qos_max_iops = False
            self.qos_min_iops = False
            self.qos_typeid = False

        self.virtualdisks = virtual_disks

    @classmethod
    def from_name(cls, session, name):
        """
        Creates an instance of a class from the specified name

        :param session:
        :param name:
        :return:

        """
        virtual_machine_list = session.get_vms(name=name)

        if virtual_machine_list['filteredTotal'] == 1:
            for i in virtual_machine_list['items']:
                virtual_machine = i['uuid']['uuid']
                return cls(session.get_vm(vm_id=virtual_machine))
        else:
            return virtual_machine_list


    @classmethod
    def from_dict(cls, vm):
        """
        Creates an instance of a class from existing JSON that may have been retrieved previously.

        This method is generally faster than .from_uuid() since it doesn't require a REST call for every virtual machine.

        Sample usage:
            # get logged into the the tintri VMStore first:
            import kvtintri

            session = kvtintri.VMStore.login(device="10.25.36.10", username="admin", password="secret!")

            # retrieve a dictionary of virtual machines from an instance of VMStore:
            virtualmachines = tintri.get_vms()

            # Create a list and iterate through the items stored in virtualmachines
            vm_list = []
            for vm in virtualmachines['items']:
                vm_list.append(kvtintri.VirtualMachine.from_dict(vm))

            # Assign new QoS values to a virtual machine named "test-vm"
            for i in vm_list:
            if i.name == "test-vm":
                i.qos_max_iops = 10000
                i.qos_min_iops = 100
                i.update_qos_session

        :param vm: A dictionary object (for example one retrieved via the VMStore.get_vms() method.)
        :return: An instance of the VirtualMachine class.
        """

        return cls(vm)

    @classmethod
    def from_uuid(cls, session, vm_uuid):
        """
        Create an instance of this class by the UUID of a given virtual machine. This will use the REST API on the
        Tintri VMStore and may be slower than using VirtualMachine.from_dict.

        :param session: An instance of the VMStore object
        :param vm_uuid: The UUID of a virtual machine that is available in the instance of the VMStore object)
        :return: An instance of this class that includes a number of parameters and attributes.
        """
        virtual_disks = session.get_virtualdisks(vmUuid=vm_uuid)
        return cls(session.get_vm(vm_uuid), virtual_disks)

    def update_qos(self, session):
        """
        Updates QoS parameters based on the values stored in self.qos_min_iops and self.qos_max_iops

        :param session: An instance of the VMStore object
        :return: Returns a python dictionary that includes the http response.
        """
        # TODO retrieve keys and values from VM JSON to populate these vars

        mod_qos = {"typeId": "com.tintri.api.rest.v310.dto.domain.beans.vm.VirtualMachineQoSConfig",
                   "minNormalizedIops": self.qos_min_iops,
                   "maxNormalizedIops": self.qos_max_iops}

        payload = {"typeId": "com.tintri.api.rest.v310.dto.MultipleSelectionRequest",
                    "ids": [self.uuid],
                    "newValue": mod_qos,
                    "propertyNames": ["minNormalizedIops", "maxNormalizedIops"]}

        return session.set_qos(payload)




class ServiceGroup(object):
    """
    Coming soon!

    """
    def __init__(self):
        pass


    @classmethod
    def get(cls, session, service_group_uuid):
        service_group = session.get_service_group(service_group_uuid)
        return cls(service_group)

