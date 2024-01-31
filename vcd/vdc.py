class VDC(object):
    def __init__(self, client, name=None, href=None, resource=None):
        self.client = client
        self.name = name
        if href is None and resource is None:
            raise Exception(
                "VDC initialization failed as arguments are either invalid "
                "or None")
        self.href = href
        self.resource = resource

        if resource is not None:
            self.name = resource.get('name')
            self.href = resource.get('href')
        self.is_admin = self.client.is_admin(self.href)
        self.href_admin = self.client.get_admin_href(self.href)

    def get_gateway(self, name, params=None, objectify_results=True,
                     extra_headers=None):
        result = self.client._do_request(
            'GET', self.href_admin + '/edgeGateways', objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)
        edge_gateways = []
        if hasattr(result, 'EdgeGatewayRecord'):
            for e in result.EdgeGatewayRecord:
                edge_gateways.append({
                    'name': e.get('name'),
                    'href': e.get('href')
                })
                if e.get('name').lower() == name.lower():
                    return self.client.get_resource(e.get('href'))
        raise Exception('EdgeGateway \'%s\' not found' % name)

    def get_all_metadata(self, params=None, objectify_results=True,
                     extra_headers=None):
        result = self.client._do_request(
            'GET', self.href_admin + '/metadata', objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)

        return result

    def list_edge_gateways(self, params=None, objectify_results=True,
                     extra_headers=None):
        result = self.client._do_request(
            'GET', self.href_admin + '/edgeGateways', objectify_results=objectify_results, params=params,
            extra_headers=extra_headers)
        edge_gateways = []
        if hasattr(result, 'EdgeGatewayRecord'):
            for e in result.EdgeGatewayRecord:
                edge_gateways.append({
                    'name': e.get('name'),
                    'href': e.get('href')
                })
        return edge_gateways

    def list_resources(self):
        result = []
        if hasattr(self.resource, 'ResourceEntities') and \
           hasattr(self.resource.ResourceEntities, 'ResourceEntity'):
            for resource in self.resource.ResourceEntities.ResourceEntity:
                if 'application/vnd.vmware.vcloud.vApp+xml' == resource.get('type'):
                    result.append({
                        'name': resource.get('name'),
                        'type': resource.get('type'),
                        'href': resource.get('href')
                    })
        return result

    def get_vapp(self, href):
        return self.client.get_resource(href)

