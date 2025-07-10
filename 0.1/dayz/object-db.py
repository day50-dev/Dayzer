#!/usr/bin/python3
import threading
import logging
import sqlite3
import time
import os
import sys
import json
from datetime import timedelta
from threading import Lock
from pprint import pprint

_dbcount = 0
_lock = Lock()
_instance = {}

# This is a way to get the column names after grabbing everything
# I guess it's also good practice
_PROCESSOR = {
  'objects' : {
    'meta': {
      'pre': lambda x, row: json.dumps(x),
      'post': lambda x, row: json.loads(x)
    }
  }
}

_PRAGMA = [
  ('journal_mode', 'wal')
]

_SCHEMA = {
  'objects': [
    ('id', 'integer primary key autoincrement'),
    ('data', 'text'),
    ('meta', 'text'),
  ],
  'relationship': [
    ('id', 'integer primary key autoincrement'),
    ('src_id', 'integer'),
    ('dest_id', 'integer'),
  ]
}


def _checkForTable(what):
  global _SCHEMA
  if what not in _SCHEMA:
    raise Exception("Table {} not found".format(what))

def _parse(table, data):
  _checkForTable(table)

  data = process(data, table, 'pre')
  known_keys = [x[0] for x in _SCHEMA[table]] 
  shared_keys = list(data.keys() & known_keys)

  # Make sure that the ordinal is maintained.
  value_list = [data[key] for key in shared_keys]

  return (shared_keys, value_list)

def _insert(table, data):
  shared_keys, value_list = _parse(table, data)

  key_string = ','.join(shared_keys)
  value_qlist = ['?'] * len(value_list)
  value_string = ','.join(value_qlist)

  return ['insert into {}({}) values({})'.format(table, key_string, value_string), shared_keys, value_list]
  
def delete(table, id):
  return run('delete from {} where id = ?'.format(table), (id, ))

def insert(table, data):
  last = False
  qstr, key_list, values = _insert(table, data)
  try:
    res, last = run(qstr, values, with_last = True)
    return last

  except Exception as exc:
    logging.warning("Unable to insert a record {} {} ({})".format(qstr, json.dumps(values), exc))

  
def update(table, where_dict, set_dict):
  shared_keys, where_values = _parse(table, where_dict)
  where_string = ' and '.join(["{}=?".format(key) for key in shared_keys])

  shared_keys, set_values = _parse(table, set_dict)
  set_string = ','.join(["{}=?".format(key) for key in shared_keys])

  qstr = 'update {} set {} where {}'.format(table, set_string, where_string)

  try:
    res, last = run(qstr, set_values + where_values, with_last = True)
    return last

  except:
    logging.warning("Unable to update a record {}|{}|{}".format(qstr, ', '.join([str(x) for x in set_values]), ', '.join([str(x) for x in where_values])))

def _find(table, where_dict, fields):
  shared_keys, where_values = _parse(table, where_dict)
  where_string = ' and '.join(["{}=?".format(key) for key in shared_keys])

  # The where string could be empty
  if len(where_string) > 0:
    where_string = "where {}".format(where_string)

  qstr = 'select {} from {} {} order by id desc'.format(fields, table, where_string)

  try:
    return run(qstr, where_values)

  except:
    logging.warning("Unable to find a record {}|{}".format(qstr, ', '.join([str(x) for x in where_values])))

def findOne(table, where_dict = {}, fields='*'):
  res = _find(table, where_dict, fields)

  if res is not None:
    rowList = process(res.fetchone(), table, 'post')
    if rowList:
      return list(rowList)

def find(table, where_dict = {}, fields='*'):
  res = _find(table, where_dict, fields)
  if res is not None:
    return process([record for record in res.fetchall()], table, 'post')

def upsert(table, data):
  qstr, key_list, values = _insert(table, data)
  update_list = ["{}=?".format(key) for key in key_list]

  qstr += "on conflict(id) do update set {}".format(','.join(update_list))

  try:
    res, last = run(qstr, values + values, with_last = True)
    return last

  except:
    logging.warning("Unable to upsert a record {}".format(','.join([str(x) for x in values])))

def pragma_update(db):
  if '_PRAGMA' in globals():
    for name, value in _PRAGMA:
      existing_value = db['c'].execute('pragma {}'.format(name)).fetchone()

      try:
        if existing_value[0].lower() != value:
          logging.info("Changing {} from {} to {}".format(name, existing_value[0], value))
          db['c'].execute('pragma {} = {}'.format(name, value))

      except Exception as ex:
        logging.warning("Failed to query or change pragma {} to {}: {}".format(name, value, ex))
    db['conn'].commit()


# Ok so if column order or type changes, this isn't found ... nor
# are we doing formal migrations where you can roll back or whatever
# because way too fancy ...
def upgrade():
  my_set = __builtins__['set']
  db = connect()

  pragma_update(db)

  for table, schema in list(_SCHEMA.items()):
    existing_schema = db['c'].execute('pragma table_info(%s)' % table).fetchall()
    existing_column_names = [str(row[1]) for row in existing_schema]

    our_column_names = [row[0] for row in schema]

    # print table, existing_column_names, our_column_names

    to_add = my_set(our_column_names).difference(my_set(existing_column_names))

    # These are the things we should add ... this can be an empty set, that's fine.
    for key in to_add:
      # 
      # sqlite doesn't support adding things into positional places (add column after X)
      # they just get tacked on at the end ... which is fine - you'd have to rebuild 
      # everything to achieve positional columns - that's not worth it - we just always 
      # tack on at the end as a policy in our schema and we'll be fine.
      #
      # However, given all of that, we still need the schema
      #
      our_schema = schema[our_column_names.index(key)][1]
      # print 'alter table %s add column %s %s' % (table, key, our_schema)
      qstr = 'alter table %s add column %s %s' % (table, key, our_schema)
      try:
        db['c'].execute(qstr)
        db['conn'].commit()
        logging.debug("Adding column {} to {}".format(key, table))

      except Exception as ex:
        logging.warning("Failed: {} ({})".format(qstr, ex))

    to_remove = my_set(existing_column_names).difference(my_set(our_column_names))

    if len(to_remove) > 0:
      our_schema = ','.join(["%s %s" % (key, klass) for key, klass in schema])
      our_columns = ','.join(our_column_names)

      drop_column_sql = """
      CREATE TEMPORARY TABLE my_backup(%s);
      INSERT INTO my_backup SELECT %s FROM %s;
      DROP TABLE %s;
      CREATE TABLE %s(%s);
      INSERT INTO %s SELECT %s FROM my_backup;
      DROP TABLE my_backup;
      """ % (our_schema, our_columns, table, table,    table, our_schema, table, our_columns)

      try:
        for sql_line in drop_column_sql.strip().split('\n'):
          db['c'].execute(sql_line)

        logging.debug("Removing column {} from {}".format(','.join(to_remove), table))

        db['conn'].commit()

      except Exception as ex:
        logging.warningn("Failed: {} ({})".format(drop_column_sql, ex))

def map(row_list, table, db=None):
  # Using the schema of a table, map the row_list to a list of dicts.
  mapped = []
  my_schema = schema(table, db)

  if not row_list:
    return row_list

  if type(row_list[0]) is str:
    row_list = [row_list]

  for row in row_list:
    mapped_row = {}
    for ix in range(len(my_schema)):
      mapped_row[my_schema[ix]] = row[ix]

    mapped.append(mapped_row)

  return mapped


def all(table, field_list='*', sort_by='id'):
  # Returns all entries from the sqlite3 database for a given table. 

  column_count = 1
  if type(field_list) is not str:
    column_count = len(field_list)
    field_list = ','.join(field_list)

  query = run('select %s from %s order by %s asc' % (field_list, table, sort_by))
  if column_count is 1 and field_list != '*':
    return [record[0] for record in query.fetchall()]

  else:
    return process([record for record in query.fetchall()], table, 'post')


def schema(table, db=None):
  existing_schema = run('pragma table_info({})'.format(table), db=db).fetchall()
  if existing_schema:
    return [str(row[1]) for row in existing_schema]

  return None


def disconnect(what):
  what['conn'].close()
  pass  
  
def connect(db_file=None):
  # A "singleton pattern" or some other fancy $10-world style of maintaining 
  # the database connection throughout the execution of the script.
  # Returns the database instance.
  global _dbcount, _instance

  id = threading.get_ident()

  if id in _instance:
    return _instance[id] 

  timeout = float(os.environ.get('SQLTIMEOUTMS') or "5000.0") / 1000.0

  if 'DB' in os.environ:
    default_db = os.environ['DB']
    logging.debug("Using {} as the DB as specified in the DB shell env variable")
  else:
    default_db = 'config.db'
    logging.debug("Using {} as the DB".format(default_db))

  if not db_file:
    db_file = default_db

  #
  # We don't have to worry about the different memory sharing models here.
  # Really, just think about it ... it's totally irrelevant.
  #

  _instance[id] = {}

  if not os.path.exists(db_file):
    sys.stderr.write("Info: Creating db file %s\n" % db_file)

  conn = sqlite3.connect(db_file, timeout=timeout)
  conn.row_factory = sqlite3.Row

  if 'DEBUG' in os.environ:
    conn.set_trace_callback(logging.debug)

  _instance[id].update({
    'conn': conn,
    'c': conn.cursor()
  })

  if db_file == default_db and _dbcount == 0: 

    pragma_update(_instance[id])

    for table, schema in list(_SCHEMA.items()):
      dfn = ','.join(["%s %s" % (key, klass) for key, klass in schema])
      _instance[id]['c'].execute("CREATE TABLE IF NOT EXISTS %s(%s)" % (table, dfn))

    _instance[id]['conn'].commit()

  _dbcount += 1 

  return _instance[id]



def process(res, table, what):
  if table in _PROCESSOR:
    unwrap = False
    if type(res) is not list:
      unwrap = True
      res = [ res ]
     
    for ix, row in enumerate(res):
      if row:
        # The SQLITE3.ROW type is immutable so
        # we need to convert it to a dict in order
        # to get it back to our user
        row = dict(row)
        for k, v in _PROCESSOR[table].items():
          # If a pre/post is defined for this key
          # on this table then we do it
          if what in v:
            row[k] = v[what](row[k], row)

        res[ix] = row

    if unwrap:
      res = res[0]
  
  return res

def get(table, id = False):
  _checkForTable(table)

  res = run("select * from {} where id = ?".format(table), (id, ))

  if res:
    return process(res.fetchone(), table, 'post')


def range(table, start, end, field='*'):
  if type(start) is int:
    # if it's in milliseconds or if the year > 2514
    # (which would be truly remarkable)
    if start > 2**34:
      start /= 1000
      end /= 1000

  query = run("select {} from {} where created_at >= datetime(?, 'unixepoch') and created_at <= datetime(?, 'unixepoch')".format(field, table), (start, end))
  return process([record for record in query.fetchall()], table, 'post')
  #return [[x for x in record] for record in query.fetchall()]

def run(query, args=None, with_last=False, db=None):
  global _lock
  start = time.time()
  """
  if args is None:
    print "%d: %s" % (_dbcount, query)
  else:
    $print "%d: %s (%s)" % (_dbcount, query, ', '.join([str(m) for m in args]))
  """

  _lock.acquire()
  if db is None:
    db = connect()

  res = None

  try:
    if args is None:
      res = db['c'].execute(query)
    else:
      res = db['c'].execute(query, args)

    db['conn'].commit()
    last = db['c'].lastrowid

    if db['c'].rowcount == 0:
      raise Exception("0 rows")

  except Exception as exc:
    logging.info("{} {}".format(query, exc))
    logging.info("desc:{} in_transaction:{}".format(db['c'].description, db['conn'].in_transaction))
    raise exc

  finally:
    _lock.release()

  if with_last:
    return (res, last)

  return res


