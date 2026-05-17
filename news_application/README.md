# News Application

## Overview

This is a full-stack Django News Application that allows users to read, create, and manage news articles and newsletters depending on their assigned roles. The system supports Readers, Journalists, and Editors, each with different permissions and access levels.

The application also includes a fully functional RESTful API, token-based authentication (JWT), automated unit tests, and an approval workflow that triggers notifications and external API logging.

---

## Project Objectives

This project was built to satisfy the following requirements:

*  Role-based news platform (Reader, Journalist, Editor)
*  Article publishing system (independent or publisher* based)
*  Newsletter creation system
*  Editorial approval workflow
*  RESTful API for external access
*  JWT authentication
*  Automated unit testing
*  Email notifications and external API integration on approval

---

## User Roles & Permissions

### Reader
*  Can view approved articles and newsletters
*  Can subscribe to:
  *  Publishers
  *  Journalists
*  Can access only subscribed content via API

### Journalist
*  Can create articles and newsletters
*  Can edit/delete their own content
*  Can publish independently or under a publisher

### Editor
*  Can approve or reject articles
*  Can edit and delete any article or newsletter
*  Controls publication workflow

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

When an editor approves an article:

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
git clone <repo-url>
cd news_application
```
2. Create virtual environment
```
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Install and Create MySQL database
```
mysql -u root -p
```
5. Apply migrations
```
python manage.py migrate
python manage.py makemigrations

```
6. Create superuser (optional)
```
python manage.py createsuperuser
```
7. Run server
```
python manage.py runserver
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
* The project uses role-based access control via both:
  * Django Groups
  * CustomUser role field
  * Article approval triggers both:
  * Email notifications
  * External API logging
  * Tests use mocking to avoid sending real HTTP requests or emails