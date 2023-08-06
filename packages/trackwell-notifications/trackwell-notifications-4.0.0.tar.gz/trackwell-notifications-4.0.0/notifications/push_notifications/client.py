from http.client import HTTPResponse
from typing import Optional, Tuple
from django.conf import settings
from django.db.models import Model
from django.utils.translation import activate as activate_translation
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import boto3
import json

from django.http import HttpResponse


class SNSClient(object):
    """ Class representing an AWS SNS client that supports mobile push notifications.
    """

    def __init__(self) -> None:
        self.connection = self.connect()
        # retrieve AWS credentials from settings.
        self.ios_arn = getattr(settings, 'IOS_PLATFORM_APPLICATION_ARN')
        self.android_arn = getattr(
            settings, 'ANDROID_PLATFORM_APPLICATION_ARN')

    @staticmethod
    def connect() -> BaseClient:
        """Method that creates a connection to AWS SNS

        Raises:
            NotImplementedError: If AWS settings are not defined in settings

        Returns:
            BaseClient: AWS client instance
        """
        # start an AWS session.
        session = boto3.Session()
        if getattr(settings, 'AWS_SNS_REGION_NAME', None) and getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            return session.client(
                "sns",
                region_name=getattr(settings, 'AWS_SNS_REGION_NAME'),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=getattr(
                    settings, 'AWS_SECRET_ACCESS_KEY'),
            )
        raise NotImplementedError('AWS settings are missing in environment')

    def retrieve_platform_endpoint_attributs(self, device: Model) -> dict:
        """Method that retrieves endpoint attributes for a device

        Args:
            device (Device): Device instance

        Returns:
            dict: Endpoint attributes
        """
        try:
            response = self.connection.get_endpoint_attributes(
                EndpointArn=device.arn
            )
            return response['Attributes']
        except ClientError:
            return {}

    def delete_platform_endpoint(self, device: Model) -> bool:
        """Deletes endpoint for given device

        Args:
            device (Device): Device instance

        Returns:
            bool: If successfully deleted
        """
        try:
            self.connection.delete_endpoint(
                EndpointArn=device.arn
            )
            return True
        except ClientError:
            return False

    def create_platform_endpoint(self, device: Model, custom_user_data: Optional[str] = None) -> Tuple[bool, str]:
        """Method that creates a platform endpoint for an Android device.

        Args:
            device (Device): Device instance
            custom_user_data (str): String to tie to user data

        Returns:
            Tuple[bool, str]: Success and arn or error message
        """
        arn = None
        if device.is_ios:
            arn = self.ios_arn
        elif device.is_android:
            arn = self.android_arn
        try:
            response = self.connection.create_platform_endpoint(
                PlatformApplicationArn=arn,
                Token=device.token,
                CustomUserData=custom_user_data
            )
            return True, response['EndpointArn']
        except ClientError as e:
            error_resp = e.response['Error']
            return False, error_resp['Message']

    def format_ios_message(
        self,
        title: str,
        text: str,
        notification_id: int = None
    ) -> dict:
        """Formats a push notification to be compatible with IOS notifications

        Args:
            title (str): Title of notification
            text (str): Contents of notification
            notification_type (str): Type of notification
            data (dict): Notification data
            notification_id (int): Notification id

        Returns:
            dict: Formatted message
        """
        return json.dumps({
            'aps': {
                'alert': {
                    'title': title,
                    'body': text,
                },
            },
            'id': notification_id,
        })

    def format_android_message(
        self,
        title: str,
        text: str,
        notification_id: int = None
    ) -> dict:
        """Formats a push notification to be compatible with Android notifications

        Args:
            title (str): Title of notification
            text (str): Contents of notification
            notification_type (str): Type of notification
            data (dict): Notification data
            notification_id (int): Notification id

        Returns:
            dict: Formatted message
        """
        return json.dumps({
            'notification': {
                'title': title,
                'text': text,
                'body': text,
            },
            'data': {
                'id': notification_id,
            }
        })

    def publish_to_device(
        self,
        device: Model,
        notification: Model,
        language: Optional[str] = None
    ) -> Tuple[str, HttpResponse]:
        """Publish a push notification to an endpoint

        Args:
            device (Device): Device instance
            notification (Notification): Notification instance
            language (str): Language for device

        Returns:
            Tuple[str, str]: Tuple containing published message along with the response from AWS
        """
        if notification is None:
            return False, "No notification to publish"
        if language is None:
            default_language = getattr(settings, 'LANGUAGE_CODE', 'en')
            profile = getattr(self.user, 'profile', None)
            prefs = getattr(profile, 'prefs', {})
            language = prefs.get('language', default_language)
        activate_translation(language)
        notification_id = notification.id
        title = notification.name
        message = {'default': notification.message}
        if not device.active:
            return False, 'Device is inactive'
        if device.is_ios:
            message['APNS'] = self.format_ios_message(title, message, notification_id)
        elif device.is_android:
            message['GCM'] = self.format_android_message(title, message, notification_id)
        try:
            response = self.connection.publish(
                TargetArn=device.arn,
                Message=json.dumps(message),
                MessageStructure='json',
            )
            return True, response['MessageId']
        except ClientError as e:
            error_resp = e.response['Error']
            message = error_resp['Message']
            if error_resp['Code'] == 'EndpointDisabled':
                device.active = False
                device.save(update_fields=['active'])
                message = f'{message}: Device marked as inactive'
            return False, message

    def publish_to_topic(self, topic: Model, notification: Model) -> Tuple[bool, str]:
        """Publish a push notification to a topic

        Args:
            topic_arn (Topic): Topic instance
            notification (Notification): Notification instance

        Returns:
            Tuple[bool, str]: Whether successful and then id or error message
        """
        activate_translation(topic.language)
        try:
            response = self.connection.publish(
                TopicArn=topic.arn,
                Subject=notification.name,
                Message=notification.message,
            )
            return True, response['MessageId']
        except ClientError as e:
            error_resp = e.response['Error']
            message = error_resp['Message']
        return False, message

    def create_topic(self, topic_name: str) -> Tuple[bool, str]:
        """Create topic in AWS

        Args:
            topic_name (str): Topic name

        Returns:
            Tuple[bool, str]: Whether successful and then topic arn or error message
        """
        try:
            response = self.connection.create_topic(Name=topic_name)
            return True, response['TopicArn']
        except ClientError as e:
            error_resp = e.response['Error']
            message = error_resp['Message']
            return False, message

    def get_topic_attributes(self, topic: Model) -> dict:
        """Gets attributes for topic

        Args:
            topic (Model): Topic instance

        Returns:
            dict: Topic attributes
        """
        try:
            return self.connection.get_topic_attributes(TopicArn=topic.arn)['Attributes']
        except ClientError:
            return {}
