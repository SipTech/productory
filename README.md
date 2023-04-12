Productory

Productory is a containerized web application for managing products. It is built with Django and provides a RESTful API for creating, reading, updating, and deleting products.

Features

Create, read, update, and delete products via a RESTful API.
Authentication and authorization using JSON Web Tokens (JWT).
Search products by name, description, price, and category.
Filter products by category and price range.
Paginate products.
Cache product search results using Redis.
Handle CORS requests.
Logging and error reporting with Sentry.
Unit and integration testing using pytest.
Getting Started

To get started with Productory, you will need to have Docker and Docker Compose installed on your machine.

Clone the repository:
bash
Copy code
git clone https://github.com//productory.git
cd productory
Set environment variables:
Productory uses environment variables for configuration. Create a .env file in the root directory of the project and add the following variables:
makefile
Copy code
SECRET_KEY=
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=mysql
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
REDIS_URL=redis://cache:6379/0
SENTRY_DSN=
Build and run the containers:
css
Copy code
docker-compose up --build
This will build the Docker images and start the containers.
Run migrations:
bash
Copy code
docker-compose exec web python manage.py migrate
Create a superuser:
bash
Copy code
docker-compose exec web python manage.py createsuperuser
Access the application:
Open your web browser and go to http://localhost:8000/admin/ to access the Django admin interface. Login with the superuser credentials created in the previous step.
To access the API, go to http://localhost:8000/api/v1/.
Run tests:
To run the tests, execute the following command:
bash
Copy code
docker-compose exec web pytest
Contributing

If you would like to contribute to Productory, please fork the repository and submit a pull request.

Please make sure that your code adheres to the PEP 8 style guide, and that your changes are thoroughly tested.