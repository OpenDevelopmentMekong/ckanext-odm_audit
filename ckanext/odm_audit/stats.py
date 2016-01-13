import datetime

from pylons import config
from sqlalchemy import Table, select, join, func, and_

import ckan.plugins as p
import ckan.model as model

cache_enabled = p.toolkit.asbool(config.get(
    'ckanext.odm_audit.cache_enabled', 'True'))

if cache_enabled:
  from pylons import cache
  our_cache = cache.get_cache('odm_audit', type='dbm')

DATE_FORMAT = '%Y-%m-%d'


def table(name):
  return Table(name, model.meta.metadata, autoload=True)


def datetime2date(datetime_):
  return datetime.date(datetime_.year, datetime_.month, datetime_.day)


class Stats(object):

  @classmethod
  def private_packages(cls, limit=10000):
    package = table('package')

    s = """SELECT p.id as pkg_id, p.type as pkg_type FROM package p
           WHERE p.private = true
           ORDER BY p.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id)), pkg_type) for pkg_id, pkg_type in res_ids]
    return res_pkgs

  @classmethod
  def private_packages_by_type(cls, limit=10000):

    s = """SELECT count(p.id) as pkg_count, p.type as pkg_type FROM package p
           WHERE p.private = true
           GROUP BY p.type
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(pkg_count, pkg_type) for pkg_count, pkg_type in res_ids]
    return res_pkgs

  @classmethod
  def records_by_type(cls, limit=10000):
    package = table('package')

    s = select([func.count(package.c.id), package.c.type], from_obj=[package]).\
        group_by(package.c.type).\
        order_by(func.count(package.c.id).desc()).\
        limit(limit)

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(pkg_count, pkg_type) for pkg_count, pkg_type in res_ids]
    return res_pkgs

  @classmethod
  def records_missing_spatial_range(cls, limit=10000):

    s = """SELECT package.id FROM package
           WHERE package.id not in (
            SELECT distinct p.id FROM package p
            JOIN package_extra pe ON p.id = pe.package_id
            and pe.key = 'odm_spatial_range'
           )
           ORDER BY package.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def records_missing_copyright(cls, limit=10000):

    s = """SELECT package.id FROM package
           WHERE package.id not in (
            SELECT distinct p.id FROM package p
            JOIN package_extra pe ON p.id = pe.package_id
            and pe.key = 'odm_copyright'
           )
           GROUP BY package.id
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def datasets_missing_mandatory_fields(cls, limit=10000):

    s = """SELECT package.id FROM package
           WHERE package.type = 'dataset'
           AND package.id not in (
            SELECT distinct p.id FROM package p
            JOIN package_extra pe ON p.id = pe.package_id
            WHERE p.version != ''
            and pe.key in ('odm_language','taxonomy','odm_date_created','odm_date_uploaded','odm_spatial_range','odm_process','odm_source')
           )
           ORDER BY package.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def library_records_missing_mandatory_fields(cls, limit=10000):

    s = """SELECT package.id FROM package
           WHERE package.type = 'library_record'
           AND package.id not in (
            SELECT distinct p.id FROM package p
            JOIN package_extra pe ON p.id = pe.package_id
            WHERE p.version != ''
            and pe.key in ('odm_language','taxonomy','document_type','odm_date_uploaded','odm_spatial_range')
           )
           ORDER BY package.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def laws_records_missing_mandatory_fields(cls, limit=10000):

    s = """SELECT package.id FROM package
           WHERE package.type = 'laws_record'
           AND package.id not in (
            SELECT distinct p.id FROM package p
            JOIN package_extra pe ON p.id = pe.package_id
            WHERE pe.key in ('odm_language','taxonomy','odm_document_type','odm_laws_status','odm_date_uploaded','odm_spatial_range')
           )
           ORDER BY package.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def records_by_copyright(cls, limit=10000):

    s = """SELECT count(p.id) as pkg_count, pe.value as value FROM package p
          JOIN package_extra pe ON p.id = pe.package_id
          WHERE pe.key = 'odm_copyright'
          GROUP BY value
          LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(pkg_count, value) for pkg_count, value in res_ids]
    return res_pkgs

  @classmethod
  def records_not_migrated(cls, limit=10000):

    s = """SELECT p.id FROM package p
            WHERE p.id NOT IN (
              SELECT pe.package_id FROM package_extra pe
              WHERE key = 'title_translated'
            )
           ORDER BY p.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def library_records_not_migrated(cls, limit=10000):

    s = """SELECT p.id FROM package p
           WHERE p.type = 'library_record'
           AND p.id NOT IN (
              SELECT pe.package_id FROM package_extra pe
              WHERE key = 'title_translated'
            )
           ORDER BY p.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

  @classmethod
  def laws_records_not_migrated(cls, limit=10000):

    s = """SELECT p.id FROM package p
           WHERE p.type = 'laws_record'
           AND p.id NOT IN (
              SELECT pe.package_id FROM package_extra pe
              WHERE key = 'title_translated'
            )
           ORDER BY p.metadata_modified DESC
           LIMIT %(limit)s""" % {'limit': limit}

    res_ids = model.Session.execute(s).fetchall()
    res_pkgs = [(model.Session.query(model.Package).get(
        unicode(pkg_id[0]))) for pkg_id in res_ids]
    return res_pkgs

class RevisionStats(object):

  @classmethod
  def package_addition_rate(cls, weeks_ago=0):
    week_commenced = cls.get_date_weeks_ago(weeks_ago)
    return cls.get_objects_in_a_week(week_commenced,
                                     type_='package_addition_rate')

  @classmethod
  def package_revision_rate(cls, weeks_ago=0):
    week_commenced = cls.get_date_weeks_ago(weeks_ago)
    return cls.get_objects_in_a_week(week_commenced,
                                     type_='package_revision_rate')

  @classmethod
  def get_date_weeks_ago(cls, weeks_ago):
    '''
    @param weeks_ago: specify how many weeks ago to give count for
                      (0 = this week so far)
    '''
    date_ = datetime.date.today()
    return date_ - datetime.timedelta(days=datetime.date.weekday(date_) + 7 * weeks_ago)

  @classmethod
  def get_week_dates(cls, weeks_ago):
    '''
    @param weeks_ago: specify how many weeks ago to give count for
                      (0 = this week so far)
    '''
    package_revision = table('package_revision')
    revision = table('revision')
    today = datetime.date.today()
    date_from = datetime.datetime(today.year, today.month, today.day) -\
        datetime.timedelta(days=datetime.date.weekday(today) +
                           7 * weeks_ago)
    date_to = date_from + datetime.timedelta(days=7)
    return (date_from, date_to)

  @classmethod
  def get_date_week_started(cls, date_):
    assert isinstance(date_, datetime.date)
    if isinstance(date_, datetime.datetime):
      date_ = datetime2date(date_)
    return date_ - datetime.timedelta(days=datetime.date.weekday(date_))

  @classmethod
  def get_package_revisions(cls):
    '''
    @return: Returns list of revisions and date of them, in
             format: [(id, date), ...]
    '''
    package_revision = table('package_revision')
    revision = table('revision')
    s = select([package_revision.c.id, revision.c.timestamp], from_obj=[
               package_revision.join(revision)]).order_by(revision.c.timestamp)
    res = model.Session.execute(s).fetchall()  # [(id, datetime), ...]
    return res

  @classmethod
  def get_new_packages(cls):
    '''
    @return: Returns list of new pkgs and date when they were created, in
             format: [(id, date_ordinal), ...]
    '''
    def new_packages():
      # Can't filter by time in select because 'min' function has to
      # be 'for all time' else you get first revision in the time period.
      package_revision = table('package_revision')
      revision = table('revision')
      s = select([package_revision.c.id, func.min(revision.c.timestamp)], from_obj=[package_revision.join(
          revision)]).group_by(package_revision.c.id).order_by(func.min(revision.c.timestamp))
      res = model.Session.execute(s).fetchall()  # [(id, datetime), ...]
      res_pickleable = []
      for pkg_id, created_datetime in res:
        res_pickleable.append((pkg_id, created_datetime.toordinal()))
      return res_pickleable
    if cache_enabled:
      week_commences = cls.get_date_week_started(datetime.date.today())
      key = 'all_new_packages_%s' + week_commences.strftime(DATE_FORMAT)
      new_packages = our_cache.get_value(key=key,
                                         createfunc=new_packages)
    else:
      new_packages = new_packages()
    return new_packages

  @classmethod
  def get_deleted_packages(cls):
    '''
    @return: Returns list of deleted pkgs and date when they were deleted, in
             format: [(id, date_ordinal), ...]
    '''
    def deleted_packages():
      # Can't filter by time in select because 'min' function has to
      # be 'for all time' else you get first revision in the time period.
      package_revision = table('package_revision')
      revision = table('revision')
      s = select([package_revision.c.id, func.min(revision.c.timestamp)], from_obj=[package_revision.join(revision)]).\
          where(package_revision.c.state == model.State.DELETED).\
          group_by(package_revision.c.id).\
          order_by(func.min(revision.c.timestamp))
      res = model.Session.execute(s).fetchall()  # [(id, datetime), ...]
      res_pickleable = []
      for pkg_id, deleted_datetime in res:
        res_pickleable.append((pkg_id, deleted_datetime.toordinal()))
      return res_pickleable
    if cache_enabled:
      week_commences = cls.get_date_week_started(datetime.date.today())
      key = 'all_deleted_packages_%s' + week_commences.strftime(DATE_FORMAT)
      deleted_packages = our_cache.get_value(key=key,
                                             createfunc=deleted_packages)
    else:
      deleted_packages = deleted_packages()
    return deleted_packages

  @classmethod
  def get_num_packages_by_week(cls):
    def num_packages():
      new_packages_by_week = cls.get_by_week('new_packages')
      deleted_packages_by_week = cls.get_by_week('deleted_packages')
      first_date = (min(datetime.datetime.strptime(new_packages_by_week[0][0], DATE_FORMAT),
                        datetime.datetime.strptime(deleted_packages_by_week[0][0], DATE_FORMAT))).date()
      cls._cumulative_num_pkgs = 0
      new_pkgs = []
      deleted_pkgs = []

      def build_weekly_stats(week_commences, new_pkg_ids, deleted_pkg_ids):
        num_pkgs = len(new_pkg_ids) - len(deleted_pkg_ids)
        new_pkgs.extend([model.Session.query(
            model.Package).get(id).name for id in new_pkg_ids])
        deleted_pkgs.extend([model.Session.query(
            model.Package).get(id).name for id in deleted_pkg_ids])
        cls._cumulative_num_pkgs += num_pkgs
        return (week_commences.strftime(DATE_FORMAT),
                num_pkgs, cls._cumulative_num_pkgs)
      week_ends = first_date
      today = datetime.date.today()
      new_package_week_index = 0
      deleted_package_week_index = 0
      # [(week_commences, num_packages, cumulative_num_pkgs])]
      weekly_numbers = []
      while week_ends <= today:
        week_commences = week_ends
        week_ends = week_commences + datetime.timedelta(days=7)
        if datetime.datetime.strptime(new_packages_by_week[new_package_week_index][0], DATE_FORMAT).date() == week_commences:
          new_pkg_ids = new_packages_by_week[new_package_week_index][1]
          new_package_week_index += 1
        else:
          new_pkg_ids = []
        if datetime.datetime.strptime(deleted_packages_by_week[deleted_package_week_index][0], DATE_FORMAT).date() == week_commences:
          deleted_pkg_ids = deleted_packages_by_week[
              deleted_package_week_index][1]
          deleted_package_week_index += 1
        else:
          deleted_pkg_ids = []
        weekly_numbers.append(build_weekly_stats(
            week_commences, new_pkg_ids, deleted_pkg_ids))
      # just check we got to the end of each count
      assert new_package_week_index == len(new_packages_by_week)
      assert deleted_package_week_index == len(deleted_packages_by_week)
      return weekly_numbers
    if cache_enabled:
      week_commences = cls.get_date_week_started(datetime.date.today())
      key = 'number_packages_%s' + week_commences.strftime(DATE_FORMAT)
      num_packages = our_cache.get_value(key=key,
                                         createfunc=num_packages)
    else:
      num_packages = num_packages()
    return num_packages

  @classmethod
  def get_by_week(cls, object_type):
    cls._object_type = object_type

    def objects_by_week():
      if cls._object_type == 'new_packages':
        objects = cls.get_new_packages()

        def get_date(object_date):
          return datetime.date.fromordinal(object_date)
      elif cls._object_type == 'deleted_packages':
        objects = cls.get_deleted_packages()

        def get_date(object_date):
          return datetime.date.fromordinal(object_date)
      elif cls._object_type == 'package_revisions':
        objects = cls.get_package_revisions()

        def get_date(object_date):
          return datetime2date(object_date)
      else:
        raise NotImplementedError()
      first_date = get_date(
          objects[0][1]) if objects else datetime.date.today()
      week_commences = cls.get_date_week_started(first_date)
      week_ends = week_commences + datetime.timedelta(days=7)
      week_index = 0
      weekly_pkg_ids = []  # [(week_commences, [pkg_id1, pkg_id2, ...])]
      pkg_id_stack = []
      cls._cumulative_num_pkgs = 0

      def build_weekly_stats(week_commences, pkg_ids):
        num_pkgs = len(pkg_ids)
        cls._cumulative_num_pkgs += num_pkgs
        return (week_commences.strftime(DATE_FORMAT),
                pkg_ids, num_pkgs, cls._cumulative_num_pkgs)
      for pkg_id, date_field in objects:
        date_ = get_date(date_field)
        if date_ >= week_ends:
          weekly_pkg_ids.append(
              build_weekly_stats(week_commences, pkg_id_stack))
          pkg_id_stack = []
          week_commences = week_ends
          week_ends = week_commences + datetime.timedelta(days=7)
        pkg_id_stack.append(pkg_id)
      weekly_pkg_ids.append(build_weekly_stats(week_commences, pkg_id_stack))
      today = datetime.date.today()
      while week_ends <= today:
        week_commences = week_ends
        week_ends = week_commences + datetime.timedelta(days=7)
        weekly_pkg_ids.append(build_weekly_stats(week_commences, []))
      return weekly_pkg_ids
    if cache_enabled:
      week_commences = cls.get_date_week_started(datetime.date.today())
      key = '%s_by_week_%s' % (
          cls._object_type, week_commences.strftime(DATE_FORMAT))
      objects_by_week_ = our_cache.get_value(key=key,
                                             createfunc=objects_by_week)
    else:
      objects_by_week_ = objects_by_week()
    return objects_by_week_

  @classmethod
  def get_objects_in_a_week(cls, date_week_commences,
                            type_='new-package-rate'):
    '''
    @param type: Specifies what to return about the specified week:
                 "package_addition_rate" number of new packages
                 "package_revision_rate" number of package revisions
                 "new_packages" a list of the packages created
                 in a tuple with the date.
                 "deleted_packages" a list of the packages deleted
                 in a tuple with the date.
    @param dates: date range of interest - a tuple:
                 (start_date, end_date)
    '''
    assert isinstance(date_week_commences, datetime.date)
    if type_ in ('package_addition_rate', 'new_packages'):
      object_type = 'new_packages'
    elif type_ == 'deleted_packages':
      object_type = 'deleted_packages'
    elif type_ == 'package_revision_rate':
      object_type = 'package_revisions'
    else:
      raise NotImplementedError()
    objects_by_week = cls.get_by_week(object_type)
    date_wc_str = date_week_commences.strftime(DATE_FORMAT)
    object_ids = None
    for objects_in_a_week in objects_by_week:
      if objects_in_a_week[0] == date_wc_str:
        object_ids = objects_in_a_week[1]
        break
    if object_ids is None:
      raise TypeError('Week specified is outside range')
    assert isinstance(object_ids, list)
    if type_ in ('package_revision_rate', 'package_addition_rate'):
      return len(object_ids)
    elif type_ in ('new_packages', 'deleted_packages'):
      return [model.Session.query(model.Package).get(pkg_id)
              for pkg_id in object_ids]
