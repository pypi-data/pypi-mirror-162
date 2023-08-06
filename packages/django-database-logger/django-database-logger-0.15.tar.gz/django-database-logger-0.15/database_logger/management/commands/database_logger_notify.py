from __future__ import unicode_literals
import logging
from datetime import datetime, timedelta, time
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from database_logger.models import LogEntry, Notifications

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = '''Processes database log and sends notification'''

    def handle(self, *args, **options):
        map_frequencies = {
            'h': _('hourly'),
            'd': _('daily'),
            'w': _('weekly'),
            'm': _('monthly')
        }
        logger.info("INIZIO database_logger_notify")
        if 'logs' in settings.DATABASE_LOGGER:
            for app in settings.DATABASE_LOGGER['logs']:
                logger.info("database_logger_notify app: %s" % app)
                s = settings.DATABASE_LOGGER[app]
                if s['active']:
                    for n in s['notifications']:
                        logger.info("database_logger_notify notification: %s" % n['name'])
                        try:
                            if n['frequency'] == 'h':
                                now = datetime.now()
                                one_hour_ago = now - timedelta(hours=1)
                                notification_start = one_hour_ago.replace(minute=0, second=0, microsecond=0)
                                notification_end = now.replace(minute=0, second=0, microsecond=0)
                            else: #DEFAULT is dayly ==> if n['frequency'] == 'd':
                                today = datetime.now().date()
                                yesterday = today - timedelta(1)
                                notification_start = datetime.combine(yesterday, time())
                                notification_end = datetime.combine(today, time())
                            if not Notifications.objects.filter(name=n['name'],
                                                                app=app,
                                                                start=notification_start,
                                                                end=notification_end).exists() \
                                    and LogEntry.objects.filter(name=app, creation_time__gte=notification_start,
                                                                creation_time__lt=notification_end).exists():
                                try:
                                    new_notification = Notifications(name=n['name'], app=app,
                                                                     start=notification_start, end=notification_end)
                                    notification_reports = {}
                                    for report in n['reports']:
                                        report_cfg = s['reports'][report]
                                        if 'group_by' in report_cfg:
                                            notification_report = {}
                                        else:
                                            notification_report = []
                                        for le in LogEntry.objects.filter(name=app, creation_time__gte=notification_start, creation_time__lt=notification_end):
                                            if 'group_by' in report_cfg:
                                                gb_attr = getattr(le, report_cfg['group_by'])
                                                if gb_attr is None:
                                                    gb_attr = _("No value for %s") % report_cfg['group_by']
                                                else:
                                                    gb_attr = str(gb_attr)
                                                if not gb_attr in notification_report:
                                                    notification_report[gb_attr] = {
                                                        'summaries': {},
                                                        'notifications': []
                                                    }
                                                    for summary in report_cfg['summarize_by']:
                                                        notification_report[gb_attr]['summaries'][summary] = {}
                                                if report_cfg['details']:
                                                    notification_report[gb_attr]['notifications'].append(le)
                                                if 'summarize_by' in report_cfg:
                                                    for summary in report_cfg['summarize_by']:
                                                        try:
                                                            if hasattr(le, summary):
                                                                value = getattr(le, summary)
                                                            else:
                                                                value = le.extra_info_json[summary]
                                                        except:
                                                            value = _('None')
                                                        if not value in notification_report[gb_attr]['summaries'][summary]:
                                                            notification_report[gb_attr]['summaries'][summary][value] = 1
                                                        else:
                                                            notification_report[gb_attr]['summaries'][summary][value] += 1
                                            else:
                                                notification_report.append(le)
                                        notification_reports[report] = notification_report

                                    htmly = get_template('email/email_notification.html')
                                    subject = ('[%s] - %s %s' % (settings.SITE_NAME, app, n['name']))
                                    d = {
                                        'app': app,
                                        'notification_name': n['name'],
                                        'notification_start': notification_start,
                                        'notification_end': notification_end,
                                        'site_name': settings.SITE_NAME,
                                        'frequency_verbose': map_frequencies[n['frequency']],
                                        'frequency': n['frequency'],
                                        'name': n['name'],
                                        'notification_reports': notification_reports
                                    }
                                    html_content = htmly.render(d)
                                    destinatari = ([n['email']] if type(n['email'])==str else n['email'])
                                    msg = EmailMultiAlternatives(subject, html_content, settings.DEFAULT_FROM_EMAIL,
                                                                 destinatari)
                                    msg.attach_alternative(html_content, "text/html")
                                    msg.send()

                                    new_notification.save()
                                except Exception as ex:
                                    logger.error("database_logger_notify error: %s" % str(ex))
                                    # errore invio
                        except Exception as ex:
                            logger.error("database_logger_notify unhandled error: %s" % str(ex))
                            # badly configured






