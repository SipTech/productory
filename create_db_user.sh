#!/bin/bash

if [ "$DB_USER" != "" ]; then
    mysql -h $DB_HOST -u $MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -e "CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED WITH mysql_native_password BY '$DB_PASSWORD';"
    mysql -h $DB_HOST -u $MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';"
    echo "Created user $DB_USER for database $DB_NAME"
else
    echo "No database user specified in environment variable DB_USER"
fi
