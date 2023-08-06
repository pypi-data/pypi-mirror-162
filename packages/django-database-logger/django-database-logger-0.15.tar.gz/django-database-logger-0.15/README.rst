===============
DATABASE LOGGER
===============

Alpha: DO NOT USE IN PRODUCTION
Database logger is a Django app that allows you to log on a database 
table using standard logging commands. It can hook on existing logging
handlers and start storing them in the database

Quick start
-----------

1. Add "database_logger" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'database_logger',
    ]

2. Run ``python manage.py migrate`` to create the models.

4. Configure ....
