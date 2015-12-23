import ckan.plugins as p
from ckan.lib.base import BaseController, config
import stats as stats_lib
import ckan.lib.helpers as h

class AuditController(BaseController):

    def index(self):
        c = p.toolkit.c
        stats = stats_lib.Stats()
        rev_stats = stats_lib.RevisionStats()
        c.private_packages = stats.private_packages()

        # Used in new CKAN templates gives more control to the templates for formatting.
        c.raw_packages_by_week = []
        for week_date, num_packages, cumulative_num_packages in c.num_packages_by_week:
            c.packages_by_week.append('[new Date(%s), %s]' % (week_date.replace('-', ','), cumulative_num_packages))
            c.raw_packages_by_week.append({'date': h.date_str_to_datetime(week_date), 'total_packages': cumulative_num_packages})

        c.all_package_revisions = []
        c.raw_all_package_revisions = []
        for week_date, revs, num_revisions, cumulative_num_revisions in c.package_revisions_by_week:
            c.all_package_revisions.append('[new Date(%s), %s]' % (week_date.replace('-', ','), num_revisions))
            c.raw_all_package_revisions.append({'date': h.date_str_to_datetime(week_date), 'total_revisions': num_revisions})

        c.new_datasets = []
        c.raw_new_datasets = []
        for week_date, pkgs, num_packages, cumulative_num_packages in c.new_packages_by_week:
            c.new_datasets.append('[new Date(%s), %s]' % (week_date.replace('-', ','), num_packages))
            c.raw_new_datasets.append({'date': h.date_str_to_datetime(week_date), 'new_packages': num_packages})

        return p.toolkit.render('ckanext/audit/index.html')

    def leaderboard(self, id=None):
        c = p.toolkit.c
        c.solr_core_url = config.get('ckanext.odm_audit.solr_core_url','http://solr.okfn.org/solr/ckan')
        return p.toolkit.render('ckanext/odm_audit/leaderboard.html')
