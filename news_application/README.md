# News Application

## Overview

This is a full-stack Django News Application that allows users to read, create, and manage news articles and newsletters depending on their assigned roles. The system supports Readers, Journalists, and Editors, each with different permissions and access levels.

The application also includes a fully functional RESTful API, token-based authentication (JWT), automated unit tests, and an approval workflow that triggers notifications and external API logging.

---

## Project Objectives

This project was built to satisfy the following requirements:

*  Role-based news platform (Reader, Journalist, Editor)
*  Article publishing system (independent or publisher based)
*  Newsletter creation system
*  Editorial approval workflow
*  RESTful API for external access
*  JWT authentication
*  Automated unit testing
*  Email notifications and external API integration for when subscribed journalists / publishers release an article

---

## User Roles & Permissions

### Reader
*  Can view approved articles and newsletters
*  Can subscribe to:
    * Journalists
    * Publishers
*  Can access only subscribed content via API

### Journalist
*  Can create articles and newsletters
*  Can edit/delete their own content
*  Can publish independently or under a publisher
*  Can apply to join a publisher

### Editor
*  Can approve any article
*  Can edit and delete any article or newsletter within their publisher
*  Can create, manage and delete publishers
*  Can apply to join a publisher


### All Users
* Can view all approved articles
* Can view all newsletters
* Can view all Journalists
* Can view all Publishers
---

## Models

### Article
*  `title`
*  `content`
*  `author` (Journalist)
*  `publisher` (optional)
*  `created_at`
*  `approved` (boolean)

### Publisher
*  `name`
*  `description`
*  `editors` (ManyToMany)
*  `journalists` (ManyToMany)
*  `pending editors` (ManyToMany)
*  `pending journalists` (ManyToMany)

### Newsletter
*  `title`
*  `description`
*  `author` (Journalist)
*  `publisher` (optional)
*  `articles` (ManyToMany)
*  `created_at`

### CustomUser
Extends Django AbstractUser with:
*  `role` (reader, journalist, editor)
*  `subscriptions_to_publishers`
*  `subscriptions_to_journalists`

---

## Authentication & Authorization

* JWT authentication via `djangorestframework-simplejwt`
* Token endpoints:
  *  `/api/token/`
  *  `/api/token/refresh/`

### Access Control Rules:
*  Readers: read-only access
*  Journalists: create/update/delete own content
*  Editors: full moderation and approval rights

---

## REST API Endpoints

### Articles

| Method | Endpoint | Description                      |
|--------|----------|----------------------------------|
| GET | `/api/articles/` | All approved articles            |
| GET | `/api/articles/subscribed/` | Reader-specific feed             |
| GET | `/api/articles/<id>/` | Single article                   |
| POST | `/api/articles/create/` | Create article (journalist only) |
| PUT | `/api/articles/<id>/update/` | Update article                   |
| DELETE | `/api/articles/<id>/delete/` | Delete article                   |
| PUT | `/api/articles/<id>/approve/` | Approve article (editor only)    |

---

## Approval Workflow (Business Logic)

When an editor approves an article or an article is published independently:

1. Article is marked as `approved=True`
2. Email notifications are sent to:
   * Subscribers of the journalist
   * Subscribers of the publisher (if applicable)
3. A POST request is sent to internal API endpoint:
```
/api/approved/
```
This simulates external integration and logs approved articles.

This logic is handled in:
```
main_app/views.py > approve_article()
```

---

## External API Integration

The system logs approved articles using:

* Endpoint: `/api/approved/`
* Method: POST
* Purpose: Simulates third-party content sharing

---

## Serializers (DRF)

* `ArticleSerializer`
* `UserSerializer`
* `PublisherSerializer`
* `NewsletterSerializer`

All API responses use Django REST Framework serializers.

---

## Automated Testing

The project includes automated unit tests using Django’s testing framework.

### Coverage includes:

* Authentication per role  
* Reader subscription filtering  
* Journalist article creation  
* Editor approval & deletion  
* Newsletter creation and validation  
* API access control  
* External API call mocking (`requests.post`)  
* Both successful and failed request scenarios  

### Running tests:

```
python manage.py test
```

### Setup Instructions
1. Clone repository
```
git clone https://github.com/samia-islam-01/NewsApplication_Django
cd NewsApplication_Django/news_application
```
2. Create virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Install MYSQL using this link in your browser:
```
https://dev.mysql.com/downloads/installer/
```
5. Choose Setup Type Developer Default and install requirements
6. Choose a Password Authentication method and create a password for a blank username (root)
7. Connect to database
8. Write in the query editor:
```
DROP DATABASE news_app_db;
CREATE DATABASE news_app_db;
```
9. Duplicate the `.env.example` file and rename it to `.env`
10. Replace the filler values with your database name (`news_app_db`) and login credentials
11. Create a secret key using the code below in the terminal and replace the `SECRET_KEY` value with this
```
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
12. Replace the email values with your email address and your Google App Password, which you can generate using the link below:
```
https://myaccount.google.com/apppasswords
```
13. Execute it using the lightning symbol 
14. Apply migrations
```
python manage.py makemigrations
python manage.py migrate
```
15. Create superuser (optional)
```
python manage.py createsuperuser
```
16. Run server
```
python manage.py runserver
```
17. Type this into your browser to use the application:
```
http://127.0.0.1:8000
```
### Technologies Used
* Django 6
* Django REST Framework
* JWT Authentication (SimpleJWT)
* MySQL
* Python Requests (external API simulation)
* Django Unit Testing Framework
* Bootstrap (frontend UI)

### Notes
* All users can view articles, newsletters and publishers. Although this wasn't specified in the brief, this is a personal preference
    * Because of this, I have specified a reason that the different roles are able to see these pages (e.g. applying to join a publisher)
* I have implemented the publisher functionality under the editor role (e.g. creating and managing)
* In the future, I would like to implement a notification system where editors creating publishers select journalists and editors they want for it but those people have to accept the invitation in order to be a part of it, however that is not required for this task
