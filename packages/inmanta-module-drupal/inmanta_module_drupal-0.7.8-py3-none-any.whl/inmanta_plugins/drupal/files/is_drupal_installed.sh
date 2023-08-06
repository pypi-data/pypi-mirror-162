#!/bin/bash

# Install drupal using drush

DB_HOST=$1
DB_USER=$2
DB_PW=$3
DB_NAME=$4

mysql -h $DB_HOST -u $DB_USER -p$DB_PW -e "select value from variable where name = 'install_task'" $DB_NAME 2>/dev/null | grep done >/dev/null
