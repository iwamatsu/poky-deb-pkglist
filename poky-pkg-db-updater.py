# -*- coding: utf-8 -*-

import os, re
import sqlite3

POKY_REPO_BASE = os.environ.get('HOME') + "/dev/yocto/poky"
POKY_WORK_BASE = os.environ.get('HOME') + "/dev/yocto/yocto-recipe-lists/"

deb_codename = 'buster'
codenames = ['morty', 'pyro', 'rocko', 'sumo', 'master']
dbpath = './pkgdb.sqlite'

connection = sqlite3.connect(dbpath)
cursor = connection.cursor()

for codename in codenames:

    table = "pkginfo_%s_%s" % (codename, deb_codename)
    # print ("%s\n---------------------------------------------------------------" % codename)
    sql_exec = "CREATE TABLE IF NOT EXISTS %s (poky_pkg_name text PRIMARY KEY, poky_pkg_ver text, deb_pkg_name)" % (table)
    cursor.execute(sql_exec)

    pkg_list = POKY_WORK_BASE + 'log/' + 'poky-' + codename + '.qemuarm.show-recipes.lists'

    pkgs_list_start = 0

    poky_pkg_ver = ''
    poky_pkg_name = ''
    with open(pkg_list) as f:
        for line in f:
            if pkgs_list_start == 0:
                if '=== Available recipes: ===' in line:
                    pkgs_list_start = 1
                else:
                    continue

            line = line.replace('\n', '')
            m = re.match('^(.*):$', line)
            if m is None:
                if len(poky_pkg_ver) == 0 : 
                    m = re.match('^  (.*)\s+(.*)$', line)
                    if m is not None:
                        poky_pkg_ver = m.group(2)

                        # data check
                        sql_exec = "SELECT * FROM %s WHERE poky_pkg_name='%s'" % (table, poky_pkg_name)
                        cursor.execute(sql_exec)
                        row = cursor.fetchone()
                        if row is None:
                            sql_exec = "INSERT INTO %s VALUES ('%s', '%s', '')" % (table, poky_pkg_name, poky_pkg_ver)
                            #print ("Insert: %s %s" % (poky_pkg_name, poky_pkg_ver))
                        else:
                            sql_exec = "UPDATE %s SET poky_pkg_ver='%s' WHERE poky_pkg_name='%s'" % (table, poky_pkg_ver, poky_pkg_name)
                            #print ("Update: %s %s" % (poky_pkg_name, poky_pkg_ver))

                        cursor.execute(sql_exec)
            else:
                poky_pkg_name = m.group(1)
                poky_pkg_ver = ''

    connection.commit()

connection.close()
