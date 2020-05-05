#! /usr/bin/python3.7
# coding: utf-8
#
# RENAME database='telegraf' to database='telegraf_bak'!!
# Take back at influDB config: bind-address = “127.0.0.1:8088”

from influxdb import InfluxDBClient
import subprocess
import os
import glob
import re
import errno

fold = '/tmp/mysnapshot/'
## DB definions:
db = 'telegraid'
# where to restore backup, temporary db:
backup_db = 'telegraf_bak'
## Network definions:
# At influDB config: bind-address = “127.0.0.1:8088”
# host from where to make backup:
db_source = '127.0.0.1:8088'
# host to where pull restore:
db_dest = '127.0.0.1:8088'

# sudo rm -r /tmp/mysnapshot/*
# create folder if not exist
def clear_folder(fold):
    if not os.path.isdir(fold):
        os.mkdir(fold,700)
    files = glob.glob(fold + "*")
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print(e.strerror)


#  create backup
# CHANGE TO -since !!
def backup_db(db, db_source, fold):
    back = subprocess.run(['/usr/bin/influxd', 'backup', '-portable', '-database', db, '-start', '2020-04-08T11:20:00Z', '-end', '2020-04-08T11:40:00Z', '-host', db_source, fold ],stdout=subprocess.PIPE)
    print(back.stdout)
    print(back.stderr)
#    print(back)
#
# 3) Restore backup to temporary DB:
#sudo influxd restore -portable -db "telegraf" -newdb "telegraf_bak" /tmp/mysnapshot/
restore = subprocess.run(['/usr/bin/influxd', 'restore', '-portable', '-db', 'telegraf', '-newdb', 'telegraf_bak', '/tmp/mysnapshot/' ],stdout=subprocess.PIPE)
print(restore)
#
# 4) get list of keys from backup_DB:
list_of_keys = []
dbClient = InfluxDBClient(host='localhost', port=8086, username='USERNAME', password='PASSWORD', database='telegraf_bak', ssl=True, verify_ssl=False)
result = dbClient.query('show measurements')
points = result.get_points()

for measurements in points:
    nametype = dbClient.query("show field keys FROM %s" % (measurements['name']))
    points2 = nametype.get_points()
    for i in points2:
        if measurements.get('name') == "process_status" and re.search(r'^running_', i.get('fieldKey')):
            key_type = '%s::integer'%(i.get('fieldKey'))
            copy_DB = dbClient.query("SELECT %s INTO telegraf..:MEASUREMENT FROM %s GROUP BY *" % (key_type, measurements.get('name')))
        elif measurements.get('name') == "processes" and i.get('fieldKey') == "running":
            key_type = '%s::integer'%(i.get('fieldKey'))
            copy_DB = dbClient.query("SELECT %s INTO telegraf..:MEASUREMENT FROM %s GROUP BY *" % (key_type, measurements.get('name')))
        elif measurements.get('name') == "swap" and i.get('fieldKey') == "in":
            print("IN")
            key_type = '"%s"'%(i.get('fieldKey'))
            copy_DB = dbClient.query("SELECT %s INTO telegraf..:MEASUREMENT FROM %s GROUP BY *" % (key_type, measurements.get('name')))
        else:
            key_type = '%s::%s'%(i.get('fieldKey'),i.get('fieldType'))
    #        #list_of_keys.append(key_type) 
            copy_DB = dbClient.query("SELECT %s INTO telegraf..:MEASUREMENT FROM %s GROUP BY *" % (key_type, measurements.get('name')))

##        print(', '.join(list_of_keys))
#
# 5) Copy from temporary DB to main DB:
# USE telegraf_bak
# SELECT * INTO telegraf.autogen.:MEASUREMENT FROM /telegraf_bak.autogen_bak.*/ GROUP BY *
#print("SELECT %s INTO telegraf..:MEASUREMENT FROM /.*/ GROUP BY *" % (', '.join(list_of_keys)))
#copy_DB = dbClient.query("SELECT %s INTO telegraf..:MEASUREMENT FROM /.*/ GROUP BY *" % (', '.join(list_of_keys)))
#
 6) DROP telegraf_bak
dbClient.query('DROP database telegraf_bak')
f __name__ == '__main__':
   # 1) Check remote DB:
   check_db()
   # clear or create folder where to backup
   clear_folder(fold)
   # make backup
   backup_db(db, db_source, fold)
