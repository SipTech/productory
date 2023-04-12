# Base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app

# Create app directory
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev && \
    apt-get install -y default-mysql-client && \
    apt-get install -y netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt $APP_HOME/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy app files
COPY productory $APP_HOME/productory/
COPY manage.py $APP_HOME/

# Add script to create database user
COPY create_db_user.sh $APP_HOME/
RUN chmod +x $APP_HOME/create_db_user.sh && \
    $APP_HOME/create_db_user.sh

# Make migrations and migrate the database
COPY fixtures.json $APP_HOME/
RUN python manage.py makemigrations && \
    python manage.py migrate 
    #&& \
    #python manage.py loaddata fixtures.json

# Expose port
EXPOSE 8000

# Run the command to start the app
CMD ["gunicorn", "productory.wsgi:application", "--bind", "0.0.0.0:8000"]
