# Digital Time Capsule App
A web app where users can create digital time capsules (messages, files, images, or notes) that stay locked until a chosen future date.
When the time comes, the app automatically releases the capsule to the user (via email, dashboard, or shareable link).

## Features
### Capsule Creation 
	- Users write a message or upload files. 
	- Choose a "release date" (e.g., 10 years later). 
### Capsule Locking 
	- The capsule cannot be viewed until the chosen date. 
### Delivery System 
	- Email notification or a unique URL to open it. 
	- Scheduled tasks (using Django-Celery / FastAPI background tasks). 
### User Management 
	- Registration & login (Django Auth or FastAPI JWT).

## Tools
	- Django (or FastAPI) 
	- Celery + Redis (for scheduled capsule release) 
	- SQLite (database) 
	- SQLAlchemy (storage)
