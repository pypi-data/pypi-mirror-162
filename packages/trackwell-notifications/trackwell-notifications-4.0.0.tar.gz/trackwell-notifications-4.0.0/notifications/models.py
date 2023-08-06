# -*- coding: utf-8 -*-
import datetime
import reversion
from typing import Any, Dict, Optional, Tuple
from urllib3 import HTTPResponse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import models, transaction
from django.db.models import Q, F
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from tinymce.models import HTMLField
from notifications.push_notifications.client import SNSClient
from notifications.utils import get_tenant_identifier

User = get_user_model()


class NotificationError(Exception):
    ...


class NotificationAbstractModel(models.Model):
    class NotificationChoices(models.TextChoices):
        SIGN_COMPANY = 'SIGN_COMPANY'
        SIMPLE_OK = 'SIMPLE_OK'
        RELEASE_NOTES = 'RELEASE_NOTES'

    class TypeChoices(models.IntegerChoices):
        WEB = 0, _('Web notification')
        PUSH = 1, _('Push notification')
        EMAIL = 2, _('Email notification (not implemented)')

    name = models.CharField(
        max_length=250,
        unique=True,
        help_text="Used to reference notification, shown in title for some looks",
    )
    message = HTMLField(
        help_text="Full message as shown to user",
    )
    expires = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text="Notification will not be shown after this time.",
    )
    attachment = models.FileField(
        default=None,
        blank=True,
        null=True,
    )
    active_from = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
    )
    needs_approval = models.BooleanField(
        default=False,
        help_text="Set this field if approval is necessary, see snooze time.",
    )
    snooze_lock = models.IntegerField(
        default=None,
        null=True,
        blank=True,
    )
    snooze_time = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="If user dismisses message (when relevant), message is shown again after this many days.",
    )  # Days
    send_email = models.BooleanField(
        default=False,
    )
    # SIGN_COMPANY set as default because it's the only one current existing, safe to remove
    look = models.CharField(
        max_length=50,
        choices=NotificationChoices.choices,
        default=NotificationChoices.SIMPLE_OK,
        help_text="This controls the appearance of the notification.",
    )
    notification_type = models.IntegerField(
        _('Notification type'),
        choices=TypeChoices.choices,
        default=TypeChoices.WEB
    )
    image = models.ImageField(
        upload_to='notification_imgs',
        null=True,
        blank=True,
        help_text="Image to accompany notification (optional)",
    )
    display_only_if_url_path_matches_regex = models.CharField(
        max_length=64,
        default='.*',
        null=False,
        blank=False,
        help_text='Only display this notification if the provided regex matches the url-path',
    )
    aws_sns_id = models.UUIDField(
        _('Id of notification in AWS SNS'),
        default=None,
        null=True,
        blank=True,
        help_text=_('Message id in AWS, if notification is a push notification')
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        abstract = True

    def __str__(self) -> str:
        return self.name

    @property
    def is_web(self) -> bool:
        return self.notification_type == self.TypeChoices.WEB

    @property
    def is_push(self) -> bool:
        return self.notification_type == self.TypeChoices.PUSH

    def save(self, *args, **kwargs) -> None:
        if self.is_push:
            self.message = strip_tags(self.message)
            self.message_is = strip_tags(self.message_is)
            self.message_en = strip_tags(self.message_en)
        return super().save(*args, **kwargs)

@reversion.register()
class Notification(NotificationAbstractModel):
    external_id = models.IntegerField(
        null=True,
        help_text="Used to reference externally created notifications",
    )
    recipients = models.ManyToManyField(
        User,
        through='UserNotification',
        default=None,
        blank=True,
    )
    groups = models.ManyToManyField(
        Group,
        default=None,
        blank=True,
    )
    topic = models.ForeignKey(
        'NotificationTopic',
        related_name='sent_notifications',
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    @classmethod
    def notification_key(cls, user: User) -> str:
        """Get notification key as it is referred to in cache

        Args:
            user (User): User instance

        Returns:
            str: Cache key
        """
        return f'notifications_unseen:{user.id}'

    @classmethod
    def unseen(cls, user: User) -> dict:
        """Get unseen notifications for user

        Args:
            user (User): User instance

        Returns:
            dict: Unseen notifications
        """
        notifications = cache.get(cls.notification_key(user), default={})
        for user_notif_id in notifications:
            # To make sure cache is up to date for existing notifications
            # before cookies are populated.
            upd_notif = cache.get(cls.notification_key(user), default={})
            if (user_notif := UserNotification.objects.filter(
                id=user_notif_id,
                notification_type=NotificationAbstractModel.TypeChoices.WEB
            ).first()) is not None:
                user_notif.update_unseen_cache(unseen=upd_notif)

        updated_notifications = cache.get(cls.notification_key(user), default={})
        return updated_notifications

    def create_usernotifications_for_groups(self, database_name: Optional[str] = None) -> None:
        """Create user notifications for groups

        Args:
            database_name (Optional[str], optional): Database name to use. Defaults to None.
        """
        for group in self.groups.all():
            for user in group.user_set.all():
                if database_name is not None:
                    UserNotification.objects.using(database_name).get_or_create(notification=self, user=user)
                else:
                    UserNotification.objects.get_or_create(notification=self, user=user)

    def send_push_notifications(self, default_language: str = None) -> None:
        """Send push notifications to all

        Args:
            default_language (str, optional): Default language to fallback on. Defaults to None.
        """
        if not self.is_push:
            return
        for un in UserNotification.objects.filter(
            notification=self
        ).annotate(language=F('user__profile__prefs__language')):
            un.send_push_notification(un.language or default_language)

    def save(self, *args, **kwargs):
        """Override save so it creates user notifications after saving"""
        super(Notification, self).save(*args, **kwargs)
        using = kwargs.get('using', None)
        if self.groups.exists():
            self.create_usernotifications_for_groups(database_name=using)
        if self.topic is not None:
            self.topic.send(self)


@reversion.register()
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    next_display = models.DateTimeField(default=None, null=True, blank=True)
    answer = models.BooleanField(default=None, null=True, blank=True)
    answer_string = models.CharField(max_length=255, default=None, blank=True, null=True)

    class Meta:
        verbose_name = _('User notification')
        verbose_name_plural = _('User notifications')

    def __str__(self) -> str:
        return "{} - {} - seen:{} - answer:{} - answer_string:{}".format(
            self.notification.name,
            self.user.username,
            self.seen,
            self.answer,
            self.answer_string
        )

    def update_unseen_cache(self, unseen: Optional[dict] = None) -> Any:
        """Updates unseen notifications in cache

        Args:
            unseen (Optional[dict], optional): Unseen items. Defaults to None.

        Returns:
            Any: Return value from cache methods
        """
        if unseen is None:
            unseen = Notification.unseen(self.user)

        if (self.seen and self.answer) or (
            self.notification.expires is not None and self.notification.expires < datetime.datetime.now()
        ):
            if self.id in unseen:
                del unseen[self.id]
        elif self.next_display:
            unseen[self.id] = self.next_display
        else:
            # 10 Minute in the past to make up for discrepancy between client time and server time
            unseen[self.id] = datetime.datetime.now() - datetime.timedelta(minutes=10)
        if len(unseen) == 0:
            return cache.delete(Notification.notification_key(self.user))
        return cache.set(Notification.notification_key(self.user), unseen, timeout=None)

    def send_push_notification(self, language: str = None) -> None:
        """Send push notification for this notification

        Args:
            language (str, optional): Language for notification. Defaults to None.
        """
        if language is None:
            profile = getattr(self.user, 'profile', None)
            prefs = getattr(profile, 'prefs', {})
            language = prefs.get('language', language)
        for device in self.user.devices.filter(active=True):
            try:
                device.send(self.notification, language)
            except NotificationError:
                pass

    def save(self, *args, **kwargs) -> None:
        """Override save so it updates cache and does some snoozing"""
        lang = kwargs.pop('default_language', 'is')
        if self.answer is not None:
            self.seen = True
        if self.seen and not self.answer:
            snooze_time = self.notification.snooze_time or 1
            self.next_display = datetime.datetime.now() + datetime.timedelta(days=snooze_time)
        super(UserNotification, self).save(*args, **kwargs)
        if self.notification.is_web:
            self.update_unseen_cache()
        elif self.notification.is_push:
            self.send_push_notification(lang)

    def delete(self, *args, **kwargs) -> None:
        """Override delete so it clears notification from cache as well"""
        super(UserNotification, self).delete(*args, **kwargs)
        cache.delete(Notification.notification_key(self.user))

    @staticmethod
    def update_for_user(user: User) -> None:
        """Update notifications for user

        Args:
            user (User): User instance
        """
        uns = user.usernotification_set.exclude(answer=True).filter(
            Q(notification__expires=None) | Q(notification__expires__gt=datetime.datetime.now())
        ).filter(notification__notification_type=NotificationAbstractModel.TypeChoices.WEB)

        # Here to ensure cache is up to date
        for un in uns:
            un.update_unseen_cache()


class Topic(models.Model):
    '''Model for Push notification topic in AWS SNS'''
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(_('Topic name'), max_length=256)
    language = models.CharField(
        _('Language for topic'),
        choices=settings.LANGUAGES,
        max_length=6
    )
    arn = models.CharField(
        _('Topic ARN'),
        max_length=256,
        help_text=_('ARN used to identify topic in AWS SNS'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Notification topic')
        verbose_name_plural = _('Notification topics')
        abstract = True

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_subscription_model():
        raise NotImplementedError()

    def get_topic_name(self) -> str:
        """Method that defines how topic name will be referred to in AWS SNS
        Note that topic names must be unique

        Raises:
            NotImplemented: Not implemented for this abstract model

        Returns:
            str: Topic name as represented in AWS SNS
        """
        raise NotImplemented('You need to implement get_topic_name method')

    def save(self, **kwargs) -> 'Topic':
        """Override save to create topic in AWS SNS, if not created already"""
        if not self.arn:
            client = SNSClient()
            success, arn = client.create_topic(self.get_topic_name())
            if success:
                self.arn = arn
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to delete from AWS as well"""
        if self.arn is not None:
            client = SNSClient()
            client.connection.delete_topic(TopicArn=self.arn)
        return super().delete(*args, **kwargs)

    @property
    def attributes(self) -> dict:
        """Get topic attributes from AWS SNS

        Returns:
            dict: Attributes retrieved from SNS
        """
        client = SNSClient()
        attributes = client.get_topic_attributes(self)
        return attributes

    @property
    def confirmed_subscriptions(self) -> int:
        return int(self.attributes.get('SubscriptionsConfirmed', 0))

    @property
    def pending_subscriptions(self) -> int:
        return int(self.attributes.get('SubscriptionsPending', 0))

    @property
    def deleted_subscriptions(self) -> int:
        return int(self.attributes.get('SubscriptionsDeleted', 0))

    def subscribe(self, device: 'Device') -> 'Subscription':
        """Subscribe device to topic

        Args:
            device (Device): Device instance

        Returns:
            Model: Subscription instance
        """
        client = SNSClient()
        try:
            response = client.connection.subscribe(
                TopicArn=self.arn,
                Endpoint=device.arn,
                Protocol='application',
                ReturnSubscriptionArn=True
            )
        except Exception:
            # Subscription failed, so return None
            return None
        SubModel = self.get_subscription_model()
        sub = SubModel(device_arn=device.arn, topic=self)
        sub.arn = response['SubscriptionArn']
        sub.save()
        return sub

    def unsubscribe(self, device: 'Device') -> None:
        """Unsubscribe device from topic

        Args:
            device (Device): Device instance
        """
        sub = self.subscriptions.filter(device_arn=device.arn).first()
        if sub is not None:
            sub.delete()

    def send(self, notification: NotificationAbstractModel) -> HTTPResponse:
        """Send notification to topic

        Args:
            notification (dict): Notification

        Raises:
            NotificationError: If notification could not be created in AWS

        Returns:
            HTTPResponse: Response from SNS
        """
        client = SNSClient()
        success, id_or_error = client.publish_to_topic(self, notification)
        if not success:
            raise NotificationError(f'Could not create notification. Response from AWS: {id_or_error}')
        with transaction.atomic():
            notification.aws_sns_id = id_or_error
            notification.save(update_fields=['aws_sns_id'])
        return notification

    def delete(self, **kwargs) -> Tuple[int, Dict[str, int]]:
        """Override delete so it also deletes topic from SNS

        Returns:
            Tuple[int, Dict[str, int]]: Delete results
        """
        client = SNSClient()
        try:
            client.connection.delete_topic(TopicArn=self.arn)
        except Exception:
            # Topic not found, so nothing to delete
            pass
        return super().delete(**kwargs)


class Subscription(models.Model):
    """Abstract model to handle AWS SNS topic subscriptions"""
    device_arn = models.CharField(
        _('Device arn'),
        max_length=255,
        help_text=_('ARN for device subscribed to topic'),
    )
    topic = models.ForeignKey(
        'NotificationTopic',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    arn = models.CharField(
        _('Subscription ARN'),
        max_length=255,
        help_text=_('Used to identify subscription in AWS')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Device subscription')
        verbose_name = _('Device subscriptions')
        unique_together = ('device_arn', 'topic_id',)
        abstract = True

    def __str__(self) -> str:
        return f'{self.device_arn}: {self.topic}'

    @property
    def attributes(self) -> dict:
        """Get subscription attributes from AWS

        Returns:
            dict: Subscription attributes
        """
        client = SNSClient()
        try:
            return client.connection.get_subscription_attributes(
                SubscriptionArn=self.arn
            )
        except Exception:
            # Subsription doesn't exist in AWS, probably, so return empty dict
            return {}

    def delete(self, *args, **kwargs) -> None:
        """Override delete method so it will delete subscription from AWS as well"""
        client = SNSClient()
        try:
            client.connection.unsubscribe(
                SubscriptionArn=self.arn,
            )
        except Exception:
            # If error, then subscription probably doesn't exist, so nothing to do here
            pass
        return super().delete(*args, **kwargs)


class NotificationTopic(Topic):

    class Meta:
        verbose_name = _('Notification topic')
        verbose_name_plural = _('Notification topics')

    def get_topic_name(self) -> str:
        notif_identifier = get_tenant_identifier()
        return f'{notif_identifier}-{self.name}'

    @staticmethod
    def get_subscription_model():
        return DeviceSubscription


class SentToDevice(models.Model):
    """Model to track notifications sent to devices"""
    notification = models.ForeignKey('Notification', on_delete=models.CASCADE)
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    message_id = models.UUIDField(
        _('Message id in AWS'),
        null=True,
        blank=True,
    )

    @property
    def sent(self):
        return self.message_id is not None


class Device(models.Model):
    """Model class for a user device that can receive push notifications"""
    class DeviceChoices(models.IntegerChoices):
        IOS = (0, 'IOS')
        ANDROID = (1, 'Android')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    os = models.IntegerField(choices=DeviceChoices.choices)
    token = models.CharField(max_length=255, unique=True)
    arn = models.CharField(max_length=255, unique=True, blank=True, null=True)
    active = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='devices')
    sent_notifications = models.ManyToManyField(
        Notification,
        through=SentToDevice,
        through_fields=('device', 'notification'),
        related_name='sent_to_devices'
    )

    def __str__(self) -> str:
        return f'{self.user.username}: {self.os}'

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')

    @property
    def is_android(self) -> bool:
        return self.os == self.DeviceChoices.ANDROID

    @property
    def is_ios(self) -> bool:
        return self.os == self.DeviceChoices.IOS

    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:
        if self.arn is not None:
            self.deregister()
        return super().delete(*args, **kwargs)

    def update_from_aws(self) -> bool:
        """Method to update active status from what is registered in AWS

        Returns:
            bool: If updated
        """
        enabled = self.attributes.get('Enabled', None) == 'true'
        if self.active != enabled:
            self.active = enabled
            self.save(update_fields=['active'])
            return True
        return False

    def register(self) -> bool:
        """Method to register device to SNS so it can receive push notifications.
        It retrieves the arn for the device and saves it to use as the device
        identifier to send out push notifications

        Returns:
            bool: Successful registration
        """
        client = SNSClient()
        profile = getattr(self.user, 'profile', None)
        emp = getattr(profile, 'emp', None)
        empid = getattr(emp, 'empid', '')
        tenant = get_tenant_identifier()
        custom_user_data = f'{tenant}:empid({empid})'
        success, arn_or_error = client.create_platform_endpoint(
            self, custom_user_data=custom_user_data)
        if success:
            self.arn = arn_or_error
            self.active = True
            self.save(update_fields=['arn', 'active'])
        return success

    def deregister(self, update_instance: bool = True) -> None:
        """
        Method that deletes registered a device from SNS.
        """
        if self.arn is None:
            return
        client = SNSClient()
        client.delete_platform_endpoint(self)
        if update_instance:
            self.active = False
            self.save(update_fields=['active'])

    def send(self, notification: Notification, language: str = 'is') -> str:
        """Method that sends notification to device

        Args:
            title (str): Notification title
            text (str): Notification body
            notification_type (str): Notification type
            data (dict, optional): Notification data. Defaults to dict().
        Returns:
            HTTPResponse: Response from SNS
        """

        client = SNSClient()
        if SentToDevice.objects.filter(device=self, notification=notification).exists():
            raise NotificationError('Notification already sent to this device')
        success, id_or_error = client.publish_to_device(self, notification, language)
        with transaction.atomic():
            self.sent_notifications.through.objects.create(
                device=self,
                notification=notification,
                message_id=id_or_error if success else None,
            )
        if not success:
            raise NotificationError(id_or_error)

    def subscribe(self, topic: Topic) -> 'DeviceSubscription':
        """Subscribe device to topic

        Args:
            topic (Topic): Topic instance

        Returns:
            DeviceSubscription: Subscription instance
        """
        return topic.subscribe(self)

    def unsubscribe(self, topic: Topic) -> None:
        """Unsubscribe device from topic

        Args:
            topic (Topic): Topic instance
        """
        return topic.unsubscribe(self)

    @property
    def attributes(self) -> Dict[str, Any]:
        """Get attributes for device from AWS

        Returns:
            Dict[str, Any]: Attributes
        """
        try:
            client = SNSClient()
            return client.retrieve_platform_endpoint_attributs(self)
        except Exception:
            return {}


class DeviceSubscription(Subscription):
    SUB_TYPE = 'customer'
