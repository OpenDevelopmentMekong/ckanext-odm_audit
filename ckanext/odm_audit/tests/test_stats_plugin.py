import os

from ckan.tests import url_for

from ckanext.audit.tests import StatsFixture

class TestStatsPlugin(StatsFixture):

    def test_01_config(self):
        from pylons import config
        paths = config['extra_public_paths']
        publicdir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
            'public')
        assert paths.startswith(publicdir), (publicdir, paths)
