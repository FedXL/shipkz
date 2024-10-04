#!/bin/bash

# Settings
DB_USER="postgres"
DB_PASSWORD="12345"
DB_NAME="test_db"
BACKUP_DIR="/root/backup"
DATE=$(date +\%Y-\%m-\%d_\%H-\%M-\%S)
TOKEN="5928544625:AAFvaSoDkBoS-C_x5TgaHxiBRd5QrGS_Qc8"
CHAT_ID="-1001808930707"
HOST="localhost"

# Create directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Export password variable
export PGPASSWORD="$DB_PASSWORD"

# Perform database dump
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER  -h $HOST -d $DB_NAME > $BACKUP_DIR/$DB_NAME_$DATE.sql

# Check the status of the command execution
if [ $? -eq 0 ]; then
    curl  -F document=@"$BACKUP_DIR/$DB_NAME_$DATE.sql" https://api.telegram.org/bot$TOKEN/sendDocument?chat_id=$CHAT_ID
else
    echo "Error creating backup"
fi

# Clear password variable
unset PGPASSWORD