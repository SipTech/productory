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
COPY requirements.txt $APP_HOME/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy app files
COPY . $APP_HOME/

# Expose port
EXPOSE 8000

# Run the command to start the app
CMD ["gunicorn", "productory_api.wsgi:application", "--bind", "0.0.0.0:8000"]
