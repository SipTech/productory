#Productory

Productory is a web application built with Django and Django Rest Framework (DRF) that allows users to browse and purchase products, combos, promotions, and menus.


##Features


Browse products by category

Add products to the cart

Create combos by selecting multiple products

Create promotions by selecting multiple combos and/or products

Create menus by selecting multiple combos, products, promotions, and categories

Manage products, combos, promotions, and menus via the admin interface

Authentication and authorization using JSON Web Tokens (JWT)


###Installation and Setup

####Prerequisites


Python 3.7 or higher

Django 3.2 or higher

Django Rest Framework (DRF) 3.12 or higher

MySQL 8.0 or higher

Node.js 14 or higher (for running frontend development server)


####Installation


Clone the repository:
``` bash
git clone https://github.com/username/Productory.git
cd Productory
```


Install Python dependencies:
``` bash
pip install -r requirements.txt
```

Create a PostgreSQL database and update the database settings in Productory/settings.py:
``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'productory_db',
        'USER': 'your_db_username',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

Run database migrations:
``` bash
python manage.py migrate
```

Load sample data:
``` bash
python manage.py loaddata fixtures/initial_data.json
```

Install frontend dependencies:
``` bash
cd frontend
npm install
```

Build frontend assets:
``` bash
npm run build
Run the development server:
python manage.py runserver
```

Visit http://localhost:8000 to view the application.


To get the IP Address of the database container, run:
``` bash
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}’ productory-sore
```

#####Usage (wishlist):


*Browse products by category on the homepage

*Click on a product to view its details

*Click the "Add to cart" button to add the product to the cart

*Click on the cart icon to view the cart and update the quantity of each product

*Click on the "Checkout" button to proceed to the checkout page

*Enter your shipping and billing information and click "Place order" to complete the purchase


####Contributing

If you'd like to contribute to Productory, please fork the repository and make changes as you'd like. Pull requests are welcome.


####License

The code in this project is licensed under the MIT License.

