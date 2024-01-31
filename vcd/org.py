import urllib


class Org(object):
    def __init__(self, client, href=None, resource=None):
        """Constructor for Org objects.

        :param cloud.vcd.client.Client client: the client that will be used
            to make REST calls to vCD.
        :param str href: URI of the entity.
        :param lxml.objectify.ObjectifiedElement resource: object
            containing EntityType.ORG XML data representing the organization.
        """
        self.client = client
        if href is None and resource is None:
            raise Exception('Org initialization failed as '
                                            'arguments are either invalid '
                                            'or None')
        self.href = href
        self.resource = resource
        if resource is not None:
            self.href = resource.get('href')
        self.href_admin = get_admin_href(self.href)

    def list_vdcs(self, params=None, objectify_results=True,
                     extra_headers=None):
        uri = self.client._api_base_uri
        uri = uri + '/query?type=adminOrgVdc&filter=org%3D%3D' + self.href.split('/')[5]
        vdcs = self.client._do_request(
            'GET', uri, objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)

        result = []

        if hasattr(vdcs, 'AdminVdcRecord'):
            for vdc in vdcs.AdminVdcRecord:
                result.append({'name': vdc.get('name'), 'href': vdc.get('href')})

        return result

    def get_vdc(self, href, is_admin_operation=False):
        return self.client.get_resource(href)

    def reload(self):
        """Reloads the resource representation of the organization.

        This method should be called in between two method invocations on the
        Org object, if the former call changes the representation of the
        organization in vCD.
        """
        self.resource = self.client.get_resource(self.href)

    def list_users(self, name_filter=None):
        """Retrieve the list of users in the current organization.

        :param 2-tuple name_filter: filters retrieved users by name. First item
            in the tuple needs to be the string 'name' and the second item
            should be the value of the filter.

        :return: user data in form of lxml.objectify.ObjectifiedElement
            objects, which contains QueryResultUserRecordType XML data.

        :rtype: generator object
        """
        if self.resource is None:
            self.reload()
        resource_type = 'user'
        org_filter = None
        if self.client.is_sysadmin():
            resource_type = 'user'
            org_filter = 'org==%s' % \
                urllib.parse.quote(self.resource.get('href'))
        query = self.client.get_typed_query(
            resource_type,
            query_result_format=('application/vnd.vmware.vcloud.query.records+xml', 'records'),
            equality_filter=name_filter,
            qfilter=org_filter)

        return query.execute()


def get_admin_href(href):
    """Returns admin version of a given vCD url.

    This function is idempotent, which also means that if input href is already
    an admin href no further action would be taken.

    :param str href: the href whose admin version we need.

    :return: admin version of the href.

    :rtype: str
    """
    if '/api/admin/extension/' in href:
        return href.replace('/api/admin/extension', '/api/admin/')
    elif '/api/admin/' in href:
        return href
    else:
        return href.replace('/api/', '/api/admin/')
