# -*- coding: utf-8 -*-

# rocko support only.....

import os, re, sys
import sqlite3
import csv

dbpath = './pkgdb.sqlite'
deb_codename = 'buster'
codenames = ['rocko', 'sumo', 'master']

if len(sys.argv) == 1 or len(sys.argv) > 2:
    exit()

codename = sys.argv[1]

if codename not in codenames:
    exit()

table = "pkginfo_%s_%s" % (codename, deb_codename)

connection = sqlite3.connect(dbpath)
cursor = connection.cursor()

sql_exec = "CREATE TABLE IF NOT EXISTS %s (poky_pkg_name text PRIMARY KEY, poky_pkg_ver text, deb_pkg_name)" % (table)
cursor.execute(sql_exec)

with open('oe-deb-comparison.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[3] is not '':
            # data check
            sql_exec = "SELECT * FROM %s WHERE poky_pkg_name='%s'" % (table, row[0])
            cursor.execute(sql_exec)
            __row_check = cursor.fetchone()
            if __row_check is None:
                sql_exec = "INSERT INTO %s VALUES ('%s', '', '%s')" % (table, row[0], row[3])
                print ("Insert: %s %s" % (row[0], row[3]))
            else:
                sql_exec = "UPDATE %s SET deb_pkg_name='%s' WHERE poky_pkg_name='%s'" % (table, row[3], row[0])
                print ("Update: %s %s" % (row[3], row[0]))

            cursor.execute(sql_exec)

sql_exec = "SELECT * FROM %s" % table
for row in cursor.execute(sql_exec):
        print (row)

connection.commit()
connection.close()
