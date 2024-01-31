from cloud.vcd.client import VmNicProperties


class VM(object):
    """A helper class to work with Virtual Machines."""

    def __init__(self, client, href=None, resource=None):
        """Constructor for VM object.
        :param str href: href of the vm.
        :param lxml.objectify.ObjectifiedElement resource: object containing
            EntityType.VM XML data representing the vm.
        """
        self.client = client
        if href is None and resource is None:
            raise Exception(
                'VM initialization failed as arguments are either invalid or'
                ' None')
        self.href = href
        self.resource = resource
        if resource is not None:
            self.href = resource.get('href')

    def get_metadata(self, params=None, objectify_results=True,
                     extra_headers=None):
        """Fetch all metadata entries of the org vdc.

        :return: an object containing EntityType.METADATA XML data which
            represents the metadata entries associated with the org vdc.

        :rtype: lxml.objectify.ObjectifiedElement
        """
        result = self.client._do_request(
            'GET', self.href + '/metadata', objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)

        return result

    def get_cpus(self):
        """Returns the number of CPUs in the vm.

        :return: number of cpus (int) and number of cores per socket (int) of
            the vm.

        :rtype: dict
        """
        self.get_resource()
        return {
            'num_cpus':
            int(self.resource.VmSpecSection.NumCpus.text),
            'num_cores_per_socket':
            int(self.resource.VmSpecSection.NumCoresPerSocket.text)
        }

    def get_resource(self):
        """Fetches the XML representation of the vm from vCD.

        Will serve cached response if possible.

        :return: object containing EntityType.VM XML data representing the vm.

        :rtype: lxml.objectify.ObjectifiedElement
        """
        if self.resource is None:
            self.reload()
        return self.resource

    def reload(self):
        """Reloads the resource representation of the vm.

        This method should be called in between two method invocations on the
        VM object, if the former call changes the representation of the
        vm in vCD.
        """
        self.resource = self.client.get_resource(self.href)
        if self.resource is not None:
            self.href = self.resource.get('href')

    def get_memory(self):
        """Returns the amount of memory in MB.

        :return: amount of memory in MB.

        :rtype: int
        """
        self.get_resource()
        return int(
            self.resource.VmSpecSection.MemoryResourceMb.Configured.text)

    def get_power_state(self, vm_resource=None):
        """Returns the status of the vm.

        :param lxml.objectify.ObjectifiedElement vm_resource: object
            containing EntityType.VM XML data representing the vm whose
            power state we want to retrieve.

        :return: The status of the vm, the semantics of the value returned is
            captured in pyvcloud.vcd.client.VCLOUD_STATUS_MAP

        :rtype: int
        """
        if vm_resource is None:
            vm_resource = self.get_resource()
        return int(vm_resource.get('status'))

    def is_powered_on(self, vm_resource=None):
        """Checks if a vm is powered on or not.

        :param lxml.objectify.ObjectifiedElement vm_resource: object
            containing EntityType.VM XML data representing the vm whose
            power state we want to check.

        :return: True if the vm is powered on else False.

        :rtype: bool
        """
        return self.get_power_state(vm_resource) == 4

    def get_operating_system_section(self):
        """Get operating system section of VM.

        :return: an object containing EntityType.OperatingSystemSection XML
                 data which contains operating system section of VM
        :rtype: lxml.objectify.ObjectifiedElement
        """
        uri = self.href + '/operatingSystemSection/'
        return self.client.get_resource(uri)

    def list_nics(self):
        """Lists all the nics of the VM.

        :return: list of nics with the following properties as a dictionary.
            nic index, is primary, is connected, connected network,
            ip address allocation mode, ip address, network adapter type

        :rtype: list
        """
        # get network connection section.
        net_conn_section = self.get_resource().NetworkConnectionSection

        nics = []
        if hasattr(net_conn_section, 'PrimaryNetworkConnectionIndex'):
            primary_index = net_conn_section.PrimaryNetworkConnectionIndex.text
            self.primary_index = primary_index

        if hasattr(net_conn_section, 'NetworkConnection'):
            for nc in net_conn_section.NetworkConnection:
                nic = {}
                nic[VmNicProperties.INDEX.value] = \
                    int(nc.NetworkConnectionIndex.text)
                nic[VmNicProperties.CONNECTED.value] = nc.IsConnected.text
                nic[VmNicProperties.PRIMARY.value] = (
                    primary_index == nc.NetworkConnectionIndex.text)
                nic[VmNicProperties.ADAPTER_TYPE.
                    value] = nc.NetworkAdapterType.text
                nic[VmNicProperties.NETWORK.value] = nc.get(
                    VmNicProperties.NETWORK.value)
                nic[VmNicProperties.IP_ADDRESS_MODE.
                    value] = nc.IpAddressAllocationMode.text
                if hasattr(nc, 'IpAddress'):
                    nic[VmNicProperties.IP_ADDRESS.value] = nc.IpAddress.text
                if hasattr(nc, 'MACAddress'):
                    nic[VmNicProperties.MAC_ADDRESS.value] = nc.MACAddress.text
                nics.append(nic)
        return nics
