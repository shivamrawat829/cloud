class VApp(object):
    def __init__(self, client, name=None, href=None, resource=None):
        """Constructor for VApp objects.

        :param cloud.vcd.session session: the session that will be used
            to make REST calls to vCD.
        :param str name: name of the entity.
        :param str href: URI of the entity.
        :param lxml.objectify.ObjectifiedElement resource: object containing
            EntityType.VAPP XML data representing the vApp.
        """
        self.client = client
        self.name = name
        if href is None and resource is None:
            raise Exception(
                "VApp initialization failed as arguments are either invalid "
                "or None")
        self.href = href
        self.resource = resource
        if resource is not None:
            self.name = resource.get('name')
            self.href = resource.get('href')


    def get_metadata(self, params=None, objectify_results=True,
                     extra_headers=None):
        """Fetch metadata of the vApp.

        :return: an object containing EntityType.METADATA XML data which
            represents the metadata associated with the vApp.

        :rtype: lxml.objectify.ObjectifiedElement
        """
        result = self.client._do_request(
            'GET', self.href + '/metadata', objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)
        return result

    def get_all_vms(self):
        """Retrieve all the vms in the vApp.

        :return: a list of lxml.objectify.ObjectifiedElement objects, where
            each object contains EntityType.VM XML data and represents one vm.

        :rtype: empty list or generator object
        """
        if hasattr(self.resource, 'Children') and \
                hasattr(self.resource.Children, 'Vm') and \
                len(self.resource.Children.Vm) > 0:
            return self.resource.Children.Vm
        else:
            return []
