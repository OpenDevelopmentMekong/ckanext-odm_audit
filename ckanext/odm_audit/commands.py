from ckan.lib.cli import CkanCommand
from logging import getLogger
import stats as stats_lib

log = logging.getLogger(__name__)

class Report(CkanCommand):

	''' Gathers different metrics and generates a CSV file with results '''

		# init vars here

def command(self):

	private_packages_by_type = stats.private_packages_by_type()
	for pkg_count, pkg_type in private_packages_by_type:
		log.debug('Type:' + pkg_type + ' Count: ' + str(pkg_count))
