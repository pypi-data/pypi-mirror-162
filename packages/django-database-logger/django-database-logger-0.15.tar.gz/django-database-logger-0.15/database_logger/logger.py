#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.utils.module_loading import import_string

from .models import LogEntry, LogEntities, LogUsers

db_default_formatter = logging.Formatter()
tmp_logger_django = logging.getLogger("django")


class DatabaseLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(DatabaseLogHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        tmp_logger_django.info("database_logger/logger.py emit")
        try:
            message = self.format(record)

            kwargs = {
                'message': message,
                'level_no': record.levelno,
                'level_name': record.levelname,
                'func_name': record.funcName,
                'module': record.module,
                'path_name': record.pathname,
                'file_name': record.filename,
                'line_no': record.lineno,
                'name': record.name,
                'process': record.process,
                'process_name': record.processName,
                'thread': record.thread,
                'thread_name': record.threadName,
            }
            le = LogEntry.objects.create(**kwargs)
            extra_info_json = {}
            if hasattr(record, 'args'):
                modified = False
                for k in record.args:
                    if hasattr(le, k):
                        if k == 'involved_users':
                            for involved_user in record.args[k]:
                                if hasattr(involved_user, '_wrapped') and hasattr(involved_user, '_setup'):
                                    # https://stackoverflow.com/a/13304403/1029569
                                    # also invoke _setup ??
                                    LogUsers.objects.create(log_entry = le, involved_user=involved_user._wrapped)
                                    # le.involved_users.add(involved_user._wrapped)
                                else:
                                    # shouldn't ever happen
                                    # le.involved_users.add(involved_user)
                                    LogUsers.objects.create(log_entry=le, involved_user=involved_user)
                        elif k == 'involved_entities':
                            for involved_entity in record.args[k]:
                                role = ''
                                if isinstance(involved_entity, dict):
                                    role = involved_entity['role']
                                    ie = involved_entity['instance']
                                else:
                                    ie = involved_entity
                                log_entities = LogEntities(log_entry=le, content_object=ie, role=role)
                                log_entities.save()
                        else:
                            modified = True
                            setattr(le, k, record.args[k])
                    else:
                        extra_info_json[k] = record.args[k]
                if len(extra_info_json.keys()) > 0:
                    le.extra_info_json = extra_info_json
                    modified = True
                if modified:
                    le.save()


        except Exception as ex:
            pass