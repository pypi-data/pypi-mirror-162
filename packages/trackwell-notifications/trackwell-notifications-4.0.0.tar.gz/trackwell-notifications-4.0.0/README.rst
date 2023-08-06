===============
Notifications
===============

Notifications is a simple Django app to serve notifications to your users.

To start:

```
pip install trackwell-notifications
```


Quick start
-----------
1. `pip install trackwell-notifications`

2. Add "notifications" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'notifications',
    ]

Make sure it is after the auth etc.::

    MIDDLEWARE_CLASSES = (
        ...
        'notifications.middleware.NotificationMiddleware',
    )

3. Put the js and css imports in your base template where you want things to pop up

    <script type="text/javascript" src="{% static "notifications/Notifications.js" %}"></script>
    <link rel="stylesheet" href="{% static "css/notifications.css" %}" type="text/css" />

4. Include the polls URLconf in your project urls.py like this::

    path('notifications/', include('notifications.urls')),

5. Register the api

    from notifications.api.views import NotificationViewSet
    from notifications.api.views import UserNotificationViewSet

    router.register(r'users', UserViewSet)
    router.register(r'^users_in_groups', UsersInGroupsViewSet, 'Users in groups')


6. Run `python manage.py migrate` to create the notifications models.

7. Start the development server and visit http://127.0.0.1:8000/admin/notifications
