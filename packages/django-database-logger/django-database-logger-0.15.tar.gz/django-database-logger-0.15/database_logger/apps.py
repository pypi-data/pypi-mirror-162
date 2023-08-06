from django.apps import AppConfig
from django.conf import settings
import logging.config


class DatabaseLoggerConfig(AppConfig):
    name = 'database_logger'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        DatabaseLoggerConfig.append_logger()

    @staticmethod
    def append_logger():
        try:
            if hasattr(settings, 'DATABASE_LOGGER'):
                settings.LOGGING['handlers']['database_logger'] = {
                    'level': 'DEBUG',
                    'class': 'database_logger.logger.DatabaseLogHandler'
                }
                if 'logs' in settings.DATABASE_LOGGER:
                    for app in settings.DATABASE_LOGGER['logs']:
                        if settings.DATABASE_LOGGER[app]['active']:
                            try:
                                if app in settings.LOGGING['loggers'] and not 'database_logger' in settings.LOGGING['loggers'][app]['handlers']:
                                    settings.LOGGING['loggers'][app]['handlers'].append('database_logger')
                            except Exception as ex:
                                pass  # badly configured
                logging.config.dictConfig(settings.LOGGING)
        except Exception as ex:
            pass  # badly configured
