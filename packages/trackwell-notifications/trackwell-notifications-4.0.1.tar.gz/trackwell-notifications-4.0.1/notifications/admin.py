# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Optional, Sequence

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import (
    Device,
    DeviceSubscription,
    Notification,
    NotificationTopic,
    SentToDevice,
    UserNotification
)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    actions = ['really_delete_selected']

    list_display = (
        'user',
        'notification'
    )

    search_fields = (
        'user__username',
        'notification__name'
    )
    ordering = ('user__username', 'notification__name')

    def get_actions(self, request):
        actions = super(UserNotificationAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    @admin.action(description="Delete selected entries")
    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        # The queryset cache has the count after the loop above, no
        # need for extra call or storing count in variable.
        if queryset.count() == 1:
            message_bit = "1 UserNotification entry was"
        else:
            message_bit = "%s usernotification entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('management', 'aws_sns_id')
    fields = (
        'name_en',
        'name_is',
        'message_en',
        'message_is',
        'notification_type',
        'active_from',
        'expires',
        'needs_approval',
        'snooze_time',
        'groups',
        'look',
        'image',
        'management',
        'aws_sns_id',
        'topic',
    )
    list_display = (
        'name',
        'notification_type',
        'expires',
        'look',
        'needs_approval',
    )
    ordering = ('-id', )

    def has_change_permission(self, request: HttpRequest, obj: Optional[Notification] = None) -> Sequence[str]:
        if obj is not None and obj.aws_sns_id:
            return False
        return super().has_change_permission(request, obj)

    @admin.display(description='Management')
    def management(self, instance):
        EXCLUDED_FIELDS = [
            'groups',
            'id',
            'recipients',
            'attachment',
            'active_from',
            'snooze_lock',
            'recipients',
            'send_email',
            'aws_sns_id'
        ]
        params = ''
        for field in instance.__class__._meta.get_fields():
            if field.name in EXCLUDED_FIELDS:
                continue
            attr = getattr(instance, field.name, None)
            if attr is None or attr == '':
                continue
            if isinstance(attr, datetime):
                attr = attr.isoformat()
            if field.name == 'message':
                attr = ''.join(attr.split('\n'))
                attr = ''.join(attr.split('\r'))
            params += ' --{}=\'{}\''.format(field.name, attr)
        groups = ','.join(map(str, instance.groups.values_list('id', flat=True)))
        if groups:
            params += ' --groups={}'.format(groups)

        return "python manage.py import_notification{}".format(params)

    def save_model(self, request, obj, form, change):
        super(NotificationAdmin, self).save_model(request, obj, form, change)
        for group in form.cleaned_data['groups']:
            for user in group.user_set.all():
                UserNotification.objects.get_or_create(notification=obj, user=user)


class SentInline(admin.TabularInline):
    model = SentToDevice
    fields = ('notification', 'sent_at', 'get_sent', 'message_id')
    readonly_fields = ('notification', 'sent_at', 'get_sent', 'message_id')
    extra = 0
    can_delete = False

    def get_max_num(self, request: HttpRequest, obj: Optional[Notification] = None, **kwargs: Any) -> Optional[int]:
        if obj is not None:
            return obj.sent_notifications.count()
        return super().get_max_num(request, obj, **kwargs)

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    @admin.display(description='Successfully sent')
    def get_sent(self, obj):
        return obj.sent


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    inlines = [SentInline]
    list_display = (
        'user',
        'os',
        'token',
        'arn',
        'active',
        'created_at',
    )
    readonly_fields = (
        'arn',
        'active',
        'created_at',
        'updated_at',
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class NotificationInline(admin.TabularInline):
    model = Notification
    fields = ('name', 'message')
    extra = 0
    can_delete = False
    show_change_link = True

    def get_max_num(self, request: HttpRequest, obj: Optional[Notification] = None, **kwargs: Any) -> Optional[int]:
        if obj is not None:
            return obj.sent_notifications.count()
        return super().get_max_num(request, obj, **kwargs)

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(NotificationTopic)
class NotificationTopicAdmin(admin.ModelAdmin):
    inlines = [NotificationInline]
    list_display = (
        'name', 'language', 'arn', 'subscribed', 'sent'
    )
    readonly_fields = ('arn',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @admin.display(description='Subscribed')
    def subscribed(self, obj):
        return obj.subscriptions.count()

    @admin.display(description='Sent notifications')
    def sent(self, obj):
        return obj.sent_notifications.count()


@admin.register(DeviceSubscription)
class DeviceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('device_arn', 'topic', 'arn',)
    readonly_fields = ('device_arn', 'topic', 'arn',)
