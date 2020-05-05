# InfluxDB-master-master-replication
(template)
Not secure Influx master-master replication (uses password in clear way).
!!! This is just the template for master-master replication. When I have a time and inspiration, I'll finish it to the normall state !!!
InfluxDB doesn't have master-master replication in communite version, so I have to do it by myself.
The idea:
- run script by cron
1) Check remote DB, remember the time when remote DB doesn't answer to the requests (T1)
2) Create backup of the localDB from time T1 to the present time
3) Send this backup to the remote DB
4) At the "remote server" restore backup to temporary DB
5) Get list of keys from backup_DB (*)
6) Copy from temporary DB to main DB
7) Drop temporary DB
(*) If you have the same key names in different tables, InfluxDB won't restore it. Or if Telegraf created measurements with names like "in", you should take it in brackets and so on, that's why you need to get the list of the keys and assign them their original column types or modify them before restoring.
