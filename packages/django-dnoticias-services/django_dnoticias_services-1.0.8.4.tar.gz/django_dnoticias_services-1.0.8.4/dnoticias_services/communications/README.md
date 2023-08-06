
# dnoticias services - Communications

This submodule of the dnoticias_services package is responsable for every API call to the communications site.

## Menu

1. [Mailing](#mailing)
2. [Notifications](#notifications)
3. [API documentation](#api-documentation)

## Mailing
This submodule send an email/campaign to one or many users through the communications system

#### Mail settings
```py
EMAIL_BASE_URL  # Communications base URL (https://comunicacao.dnoticias.pt)
DEFAULT_FROM_EMAIL  # Email that will be show on 'From'
MAIL_SERVICE_ACCOUNT_API_KEY  # API Key generated on Communications
MAIL_SERVICE_REQUEST_TIMEOUT  # Timeout in seconds
SEND_EMAIL_API_URL  # API PATH to send an email (/api/send/mail/)
EMAIL_BRAND_GROUP_UUID  # Brand group UUID
```

#### How to use: Mail

```py
# Just import the package in your project
from dnoticias_services.mail import send_email

# And now just call the send_email function
send_email(
    email,  # To:
    TEMPLATE,  # Template UUID (Generated in Communications)
    BRAND_GROUP_UUID,  # Brand group UUID (Generated in Communications)
    SUBJECT,  # Mail subject
    context=context, # Mail context (Used in the template generated on Communications)
    attachments=files_info  # Attached files (if needed, optional)
)

# This package has a send_campaign and send_bulk_email functions too.
```

## Notifications
Module used to send a push notification via Firebase through Communications system.

#### Settings
```py
COMMUNICATION_BASE_API_URL  # Base communications API url (same as EMAIL_BASE_URL but with /api/ at the end (yup, unnecessary, fixing soon))
NOTIFICATIONS_APPLICATION_DOMAIN  # Application domain. An application with this domain must exists on Communications!
NOTIFICATIONS_DEFAULT_ICON  # Default icon (if the user leaves the icon field in blank)
CREATE_NOTIFICATION_API_URL  # Create notification API PATH url
NOTIFICATION_API_URL  # Notification API PATH url (this path already includes get/update/delete)
GET_NOTIFICATION_LIST_API_URL  # Notification list API PATH url (Returns a datatable-use JSON list)
SEND_NOTIFICATION_API_URL  # Send notification API PATH url
CREATE_TOPIC_API_URL  # Create topic API PATH url
TOPIC_API_URL  # Topic API PATH url (Already includes get/update/delete)
GET_TOPICS_SELECT2_API_URL  # Topic select2 API PATH url
GET_TOPIC_LIST_API_URL  # Topic list API PATH url (Returns a datatable-use JSON list)
```

#### How to use: BACKOFFICE
First, you will need to define all settings we've already put before, then you will need to define the notifications URLs in your project.

To define the notifications URLs, just go to your urls.py, import and include the urls from notifications

````py
# Import the notification URLs
from dnoticias_services.communications.urls import urlpatterns as notifications_urlpatterns

urlpatterns += [
    ...
    path("notifications/", include(notifications_urlpatterns)),
]
````

Notifications URLs includes the following names:
```py
fcm-notification-list  # Link to the datatable list
fcm-notification-datatable  # Datatable API url
fcm-notification-create  # Notification create form
fcm-notification-update  # Notification update form
fcm-notification-delete  # Notification delete view
fcm-notification-send  # Notification send view
fcm-topic-select2  # Topic select2 view
fcm-topic-list  # Topic datatable list
fcm-topic-datatable  # Topic datatable API url
fcm-topic-create  # Topic create form
fcm-topic-update  # Topic update form
fcm-topic-delete  # Topic delete view
```

To access to those links, just define the list names in your menu, the datatable view already includes update/view/delete/create links!
```html
...
<a href="{% url 'fcm-notification-list' %}">...</a>
...
```

#### How to use: Notifications class

Inside the communications.notification package, you will find a Notifications class that has methods to do every request automatically instead of using the API directly.
Every method is documentated and uses typed parameters to make the function more easy and readable.

#### How to use: API

Before you do the first request to the Communications server, you will need to set the following header in all of your requests:

```bash
// The domain must exists on Communications server otherwise will return a BAD REQUEST status
X-FCM-APPLICATION-DOMAIN: your-domain.com
```

After that, you can start using the API routes.

## API documentation

#### Create token

```http
  POST /api/token/create/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `token` | `string` | **Required**. Firebase generated token |
| `access_type` | `string` | Access type. Default: web |
| `fingerprint` | `string` | Device fingerprint |
| `user_email` | `string` | User email (if is logged in) |

#### Create notification

```http
  POST /api/notification/create/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `title` | `string` | **Required**. Notification title |
| `icon_url` | `string` | **Required**. Icon image URL |
| `image_url` | `string` | **Required**. Notification image URL |
| `redirect_url_web` | `string` | **Required**. Redirect URL to web type devices (access_type=web) |
| `object_id` | `int` | **Required**. Object id that the notification belongs to |
| `content_type_id` | `int` | **Required**. ContentType id that the notification belongs to |
| `topics` | `array` | **Required**. Topics slugs array |
| `body` | `string` | Notification body |
| `redirect_url_app` | `string` | Redirect url to app devices. If empty, will use the redirect_url_web |
| `scheduled_for` | `string` | Datetime that the notification will be sent |
| `to_send` | `boolean` | ```true``` if the notification will be sent after being processed on Communications|

#### Update notification

```http
  PUT /api/notification/{{ id }}
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `title` | `string` | **Required**. Notification title |
| `icon_url` | `string` | **Required**. Icon image URL |
| `image_url` | `string` | **Required**. Notification image URL |
| `redirect_url_web` | `string` | **Required**. Redirect URL to web type devices (access_type=web) |
| `object_id` | `int` | **Required**. Object id that the notification belongs to |
| `content_type_id` | `int` | **Required**. ContentType id that the notification belongs to |
| `topics` | `array` | **Required**. Topics slugs array |
| `body` | `string` | Notification body |
| `redirect_url_app` | `string` | Redirect url to app devices. If empty, will use the redirect_url_web |
| `scheduled_for` | `string` | Datetime that the notification will be sent |
| `to_send` | `boolean` | ```true``` if the notification will be sent after being processed on Communications|

#### Delete notification

```http
  DELETE /api/notification/{{ id }}
```

#### Get notification

```http
  GET /api/notification/{{ id }}
```

#### Create topic

```http
  POST /api/topic/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `name` | `string` | **Required**. Topic name |
| `slug` | `string` | **Required**. Topic slug |
| `active` | `boolean` | Topic active |
| `content_type_id` | `int` | Content type id that the topic belongs to |
| `object_id` | `int` | Object id that the topic belongs to |

#### Update topic

```http
  PUT /api/topic/{{ id }}
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `name` | `string` | **Required**. Topic name |
| `slug` | `string` | **Required**. Topic slug |
| `active` | `boolean` | Topic active |
| `content_type_id` | `int` | Content type id that the topic belongs to |
| `object_id` | `int` | Object id that the topic belongs to |

#### Delete topic

```http
  DELETE /api/topic/{{ id }}
```

#### Get topic

```http
  GET /api/topic/{{ id || slug }}
```

#### Subscribe device to topic

```http
  POST /api/topic/subscribe/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `token` | `string` | **Required**. Device token |
| `topic_id` | `string` | **Required if topic slug is empty**. Topic id |
| `topic_slug` | `boolean` | **Required if topic id is empty** Topic slug |

#### Unsubscribe device from topic

```http
  POST /api/topic/unsubscribe/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `token` | `string` | **Required**. Device token |
| `topic_id` | `string` | **Required if topic slug is empty**. Topic id |
| `topic_slug` | `boolean` | **Required if topic id is empty** Topic slug |


#### Check if device is subscribed to topic

```http
  POST /api/device/topic/
```

| Parameter   | Type       | Description                           |
| :---------- | :--------- | :---------------------------------- |
| `token` | `string` | **Required**. Device token |
| `topic_id` | `string` | **Required if topic slug is empty**. Topic id |
| `topic_slug` | `boolean` | **Required if topic id is empty** Topic slug |


### API responses

All the responses from the API will have the same structure

```js
{
    "error": "",
    "message": "",
    "data": {}
}
```

- If some required parameter is missing on a request will return a **400 BAD REQUEST** status
- If the required object does not exists will return a  **404 NOT FOUND** status
- If the request returns an object, this will be serialized inside the `data` key
- The `message` key will contains a PT response from Communications (used in views)
- The `error` key will contains a PT response from Communications (used in views)
