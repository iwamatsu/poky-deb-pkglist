# -*- coding: utf-8 -*-
import sys
import os
import sqlite3
import datetime, time
from psycopg2 import connect
from psycopg2.extras import DictCursor

dbpath = './pkgdb.sqlite'
codename = 'rocko'
deb_codename = 'buster'
table = "pkginfo_%s" % (deb_codename)
base_table = "pkginfo_%s_%s" % (codename, deb_codename)

query = """ 
    select sources_uniq.source, sources_uniq.version, sources_uniq.distribution, sources_uniq.release, sources_uniq.component
    from sources_uniq
    where sources_uniq.release = 'buster' and sources_uniq.component = 'main'
"""

udd_con = connect(database='udd', port=5432,
        host='public-udd-mirror.xvm.mit.edu',
        user='public-udd-mirror', password='public-udd-mirror')
udd_cur = udd_con.cursor(cursor_factory=DictCursor)
udd_cur.execute(query)
udd_rows = udd_cur.fetchall()
udd_cur.close()
udd_con.close()

#udd end

connection = sqlite3.connect(dbpath)
cursor = connection.cursor()

# create table
sql_exec = "CREATE TABLE IF NOT EXISTS %s (deb_pkg_name text PRIMARY KEY, deb_pkg_ver text)" % (base_table)
cursor.execute(sql_exec)

# create pkg list of poky
pkg_list = []
sql_exec = "SELECT * FROM %s" % (base_table)
for rows in cursor.execute(sql_exec):
    for row in rows:
        if row[2] != '':
            pkg_list.append(row[2])
        else:
            pkg_list.append(row[0])

for data in udd_rows:
    if data['source'] in pkg_list:

        sql_exec = "SELECT * FROM %s WHERE deb_pkg_name='%s'" % (table, data['source'])
        cursor.execute(sql_exec)
        __row_check = cursor.fetchone()
        if __row_check is None:
            sql_exec = "INSERT INTO %s VALUES ('%s', '%s')" % (table, data['source'], data['version'])
            print ("Insert: %s %s" % (data['source'], data['version']))
        else:
            sql_exec = "UPDATE %s SET deb_pkg_ver='%s' WHERE deb_pkg_name='%s'" % (table, data['version'], data['source'])
            print ("Update: %s %s" % (data['source'], data['version']))

        cursor.execute(sql_exec)

# finish
connection.commit()
connection.close()
