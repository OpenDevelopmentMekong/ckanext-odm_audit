from logging import getLogger

import ckan.plugins as p

log = getLogger(__name__)

class OdmAuditPlugin(p.SingletonPlugin):
    '''ODM Audit plugin.'''

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def after_map(self, map):
        map.connect('audit', '/audit',
            controller='ckanext.odm_audit.controller:AuditController',
            action='index')
        map.connect('audit_action', '/audit/{action}',
            controller='ckanext.odm_audit.controller:AuditController')
        return map

    def update_config(self, config):
        templates = 'templates'
        p.toolkit.add_template_directory(config, templates)
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('public/ckanext/audit', 'ckanext_audit')
