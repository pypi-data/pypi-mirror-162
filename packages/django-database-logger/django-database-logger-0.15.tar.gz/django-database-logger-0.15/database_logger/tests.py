import datetime

from django.test import TestCase
import logging
from .models import LogEntry, LogUsers, LogEntities
from .logger import DatabaseLogHandler
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from io import StringIO
from django.core.management import call_command
from django.core import mail


class DBLoggerModelTests(TestCase):
    def setUp(self):
        self.logger = self.init_logger()
        self.user = self.init_user('goofy')
        self.other_user = self.init_user('mickey')
        self.fake_path = '/pippo/'
        self.fake_agent = 'Mozilla/5.0'

        self.logger_settings = {
            'logs': ['db_logger'],
            'db_logger': {
                'reports': {
                    'summary': {
                        'title': 'SUMMARY',
                        'group_by': 'auth_user',
                        'summarize_by': ['action_performed'],
                        'details': False
                    },
                },
                'active': True,
                'notifications': [
                    {
                        'name': 'Daily',
                        'frequency': 'd',  # h hour, d day, w week, m month
                        'email': ['test@example.com'],
                        'reports': ['summary']
                    },
                ]
            },
        }

    def call_notify_command(self, *args, **kwargs):
        with self.settings(DATABASE_LOGGER=self.logger_settings, SITE_NAME='test_suite'):
            out = StringIO()
            call_command(
                "database_logger_notify",
                *args,
                stdout=out,
                stderr=StringIO(),
                **kwargs,
            )
            return out.getvalue()

    def init_logger(self):
        logger = logging.getLogger('db_logger')
        logger.setLevel(logging.DEBUG)
        dbh = DatabaseLogHandler()
        dbh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        dbh.setFormatter(formatter)
        logger.addHandler(dbh)
        return logger

    def init_user(self, username):
        usr, created = User.objects.get_or_create(username=username, last_name='Gota', first_name='Filippo')
        usr.set_password('lapassword')
        authenticate(username=username, password='lapassword')
        return usr

    def test_is_writing(self):
        """check if it finds the message in the database"""
        db_logger = self.logger
        usr = self.user
        rf = RequestFactory()
        kwargs = {
            'action_peformed': 'test_is_writing'
        }
        request = rf.post(self.fake_path, data=kwargs, HTTP_USER_AGENT=self.fake_agent)
        request.user = usr
        kwargs = LogEntry.kwargs_from_request(request)
        msg = "un messaggio di test"
        db_logger.info(msg, kwargs)
        logentry = LogEntry.objects.filter().order_by('-creation_time').first()
        testvar = msg in logentry.message
        self.assertIs(testvar, True)

    def test_user(self):
        """check if the log is associated with the user"""
        db_logger = self.logger
        usr = self.user
        rf = RequestFactory()
        request = rf.post(self.fake_path, HTTP_USER_AGENT=self.fake_agent)
        request.user = usr
        kwargs = LogEntry.kwargs_from_request(request)
        kwargs['action_performed'] = 'test_user'
        msg = "verifica utente"
        db_logger.info(msg, kwargs)
        logentry = LogEntry.objects.filter().order_by('-creation_time').first()
        self.assertIs(usr.id, logentry.auth_user_object_id)

    def test_extra_info(self):
        """check if the extra_info is associated correctly"""
        db_logger = self.logger
        usr = self.user
        rf = RequestFactory()
        request = rf.post(self.fake_path, HTTP_USER_AGENT=self.fake_agent)
        request.user = usr
        kwargs = LogEntry.kwargs_from_request(request)
        kwargs['action_performed'] = 'test_extra_info'
        now = datetime.datetime.now()
        my_extra_info = f'timed extra info {now}'
        kwargs['my_extra_info'] = my_extra_info
        msg = "verifica extra_info"
        db_logger.info(msg, kwargs)
        last_logentry = LogEntry.objects.all().order_by('-creation_time').first()
        ei_logentry = LogEntry.objects.filter(extra_info_json__my_extra_info=my_extra_info).order_by(
            '-creation_time').first()
        self.assertEquals(last_logentry.pk, ei_logentry.pk)

    def test_notifier(self):
        """check if the notifier is working correctly"""
        db_logger = self.logger
        usr = self.user
        rf = RequestFactory()
        request = rf.post(self.fake_path, HTTP_USER_AGENT=self.fake_agent)
        request.user = usr
        kwargs = LogEntry.kwargs_from_request(request)
        kwargs['action_performed'] = 'test_notifier'
        msg = "test_notifier"
        db_logger.info(msg, kwargs)
        # set the creation_time to yesterday, so it is taken into account for the report
        for le in LogEntry.objects.all():
            le.creation_time += datetime.timedelta(days=-1)
            le.save()
        self.call_notify_command()
        # check if an email has been sent
        self.assertEqual(len(mail.outbox), 1)
        # verify that "[test_suite]" is contained in the subject of the message
        self.assertTrue('[test_suite]' in mail.outbox[0].subject)

    def test_involved_users(self):
        """check involved_users"""
        db_logger = self.logger
        for usr in [self.user, self.other_user]:
            rf = RequestFactory()
            request = rf.post(self.fake_path, HTTP_USER_AGENT=self.fake_agent)
            request.user = usr
            kwargs = LogEntry.kwargs_from_request(request)
            kwargs['action_performed'] = f'test_involved_users {usr.username}'
            kwargs['involved_users'] = [usr]
            msg = "test_involved_users"
            db_logger.info(msg, kwargs)
        self.assertTrue(LogUsers.objects.filter(involved_user_object_id=self.user.id).exists())
        self.assertTrue(LogUsers.objects.filter(involved_user_object_id=self.other_user.id).exists())

    def test_involved_entities(self):
        """check involved_entities"""
        db_logger = self.logger
        for usr in [self.user, self.other_user]:
            rf = RequestFactory()
            request = rf.post(self.fake_path, HTTP_USER_AGENT=self.fake_agent)
            request.user = usr
            kwargs = LogEntry.kwargs_from_request(request)
            kwargs['action_performed'] = f'test_involved_entities {usr.username}'
            kwargs['involved_entities'] = [usr]
            msg = "test_involved_entities"
            db_logger.info(msg, kwargs)
        self.assertTrue(LogEntities.objects.filter(object_id=self.user.id).exists())
        self.assertTrue(LogEntities.objects.filter(object_id=self.other_user.id).exists())

