
Monni
=====

Monni is an open source monitoring service licensed under Apache v2 licence..
Developed in Python using the Flask framework, database Mongodb and a handfull of shell scripts.
Monni is an handy and 'easy to setup' solution to monitor services.

Monni is meant to monitor all traffics and events from/to your services (backend or frontend)


Work in progress
----------------
The Monni project is very young and currently in progress.
The project was created at Ovelin Oy (ovelin.com) for our internal use (monitor games,backend,frontend).

We are planing to add the following features in the near future:
- Advanced Alerts handling
- SMS Alerts
- Administration pannel with Settings management
- Monitor Server status (disk space usage, CPU usage)
- Monitor Database server status (write locks, replication lags)
- Monitor Services traffic
- AWS S3 access management


Features
--------
Monni can be used in 3 different ways:
OUTBOUND:
- Monitor HTTP services status.
- Alert mails are sent when a service is down.

INBOUND:
- Receive and handle events from your services.

UTILITIES:
- Logging file rotation


Setup
-----
- Install python dependencies.
- Install mongodb.
- Rename config/default.cfg.example to config/default.cfg and configure your environment.
- Setup Apache server or launch Monni from command line.
    - ./application.py
