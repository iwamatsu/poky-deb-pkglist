# -*- coding:utf-8 -*-

import sqlite3
from bottle import route, run, template

dbpath = './pkgdb.sqlite'
codename = 'rocko'
deb_codename = 'buster'
base_table = "pkginfo_%s_%s" % (codename, deb_codename)
deb_table = "pkginfo_%s" % (deb_codename)

def get_pkgs_list():

    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    sql_exec = "SELECT * FROM %s" % (base_table)

    cursor.execute(sql_exec)
    base_rows = cursor.fetchall()
    
    pkgs_list = []
    for base_row in base_rows:
        if len(base_row) == 3 and base_row[2] != '':
            deb_pkg_name = base_row[2]
        else:
            deb_pkg_name = base_row[0]

        poky_pkg_name = base_row[0]
        poky_pkg_ver = base_row[1]

        sql_exec = "SELECT * FROM %s WHERE deb_pkg_name='%s'" % (deb_table, deb_pkg_name)
        cursor.execute(sql_exec)
        __row_check = cursor.fetchone()
        if __row_check is not None:
            deb_pkg_ver = __row_check[1]
        else:
            deb_pkg_ver = "unknown"

        if poky_pkg_name == deb_pkg_name:
            deb_pkg_name = "-"
	
        # print ("%s, %s, %s, %s" % (poky_pkg_name, poky_pkg_ver, deb_pkg_name, deb_pkg_ver))

        pkgs_list.append ({
            "poky": poky_pkg_name,
            "poky_ver": poky_pkg_ver,
            "deb": deb_pkg_name,
            "deb_ver": deb_pkg_ver
        })

    # finish
    connection.commit()
    connection.close()

    return pkgs_list

@route("/")
def index():
    pkgs_list = get_pkgs_list()
    return template("index", pkgs_list=pkgs_list)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
