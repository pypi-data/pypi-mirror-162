from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from user_agents import parse as parse_user_agents


class LogEntry(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)
    message = models.TextField()
    level_no = models.SmallIntegerField()
    level_name = models.CharField(max_length=50, db_index=True)
    func_name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    path_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    line_no = models.BigIntegerField()
    name = models.CharField(max_length=255, db_index=True)
    process = models.BigIntegerField()
    process_name = models.CharField(max_length=255)
    thread = models.BigIntegerField()
    thread_name = models.CharField(max_length=255)

    # main_instance is the main instance of some model for which we are recording this log entry
    # I might be saving a row of an invoice and want the main_instance to be the invoice rather than
    # the row; or I might even log twice: firstly with the invoice as the main_instance and the secondly
    # with the customer. Doing so I can easily aggregate logs against different entities.
    main_instance_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+',
                                                   null=True, blank=True)
    main_instance_object_id = models.PositiveIntegerField(null=True, blank=True)
    main_instance = GenericForeignKey('main_instance_content_type', 'main_instance_object_id')
    main_instance_role = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    secondary_instance_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+',
                                                   null=True, blank=True)
    secondary_instance_object_id = models.PositiveIntegerField(null=True, blank=True)
    secondary_instance = GenericForeignKey('secondary_instance_content_type', 'secondary_instance_object_id')
    secondary_instance_role = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    action_performed = models.CharField(max_length=100, db_index=True)

    extra_info_json = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    auth_user_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+', null=True,
                                               blank=True)
    auth_user_object_id = models.PositiveIntegerField(null=True, blank=True)
    auth_user = GenericForeignKey('auth_user_content_type', 'auth_user_object_id')

    @staticmethod
    def kwargs_from_request(request):
        user_agent = parse_user_agents(request.META['HTTP_USER_AGENT'])
        cookies = ''
        try:
            cookies = str(request.META['COOKIES'])
        except KeyError as ex:
            pass
        ip = ''
        try:
            ip = str(request.META['HTTP_X_FORWARDED_FOR'])
        except KeyError as ex:
            try:
                ip = str(request.META['REMOTE_ADDR'])
            except KeyError as ex:
                pass
        auth_user = None
        if request.user.is_authenticated:
            auth_user = request.user
        return {
            "auth_user": auth_user,
            'HTTP_USER_AGENT': str(user_agent),
            'IP_ADDRESS': ip,
            'COOKIES': cookies,
        }

    class Meta:
        app_label = 'database_logger'


class LogUsers(models.Model):
    log_entry = models.ForeignKey(LogEntry, on_delete=models.CASCADE, related_name='involved_users')
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    involved_user_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+', null=True,
                                                   blank=True)
    involved_user_object_id = models.PositiveIntegerField(null=True, blank=True)
    involved_user = GenericForeignKey('involved_user_content_type', 'involved_user_object_id')
    role = models.CharField(max_length=255, db_index=True)

    class Meta:
        app_label = 'database_logger'


class LogEntities(models.Model):
    log_entry = models.ForeignKey(LogEntry, on_delete=models.CASCADE, related_name='involved_entities')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    role = models.CharField(max_length=255, db_index=True, blank=True, null=True)

    class Meta:
        app_label = 'database_logger'


class Notifications(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'database_logger'
