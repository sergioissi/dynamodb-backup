"""
Python script for backup AWS DynamoDB tables.
"""
from datetime import datetime, timedelta
import os
import re
import logging
import sys
import boto3
import logger


# Initialize log
logger.logger_init()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.propagate = False


try:
    DYNAMODBCLIENT = boto3.client(
        'dynamodb',
        region_name='eu-west-1'
    )
except Exception as err:
    logger.error(f"Connection error to dynamodb. {str(err)}")
    sys.exit()


def main(event, context):
    """
    Main function to create and rotate the DynamoDb table backups.
    """
    tables = get_table_list()
    results = {
        "success": [],
        "failure": []
    }

    for table in tables:
        try:
            create_backup(table)
            results['success'].append(table)
        except Exception as err:
            logger.error(f"Error creating backup for table {table}. {str(err)}")
            results['failure'].append(table)

    if os.environ.get('BACKUP_REMOVAL_ENABLED') == 'true':
        try:
            rotate_backups(tables)
        except Exception as err:
            logger.error(f"Error removing old backups. {str(err)}")

    if not results['success'] and not results['failure']:
        logger.warning("Tried running DynamoDB backup, but no tables were specified. Please check your configuration.")
        return

    total = (len(results['success']) + len(results['failure']))

    logger.info(f"Tried to backup {total} DynamoDB tables. "
                f"{len(results['success'])} succeeded, and "
                f"{len(results['failure'])} failed."
               )

    if results['success']:
        for table_ok in results['success']:
            logger.info(f"The following table were successful: {table_ok}")

    if results['failure']:
        for table_ko in results['failure']:
            logger.info(f"The following table failed: {table_ko}")


def create_backup(table):
    """
    Create table backup, the name will be composed by the table name
    and the timestamp it was created.
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_name = f"{table}_{timestamp}"
    try:
        DYNAMODBCLIENT.create_backup(
            TableName=table,
            BackupName=backup_name
        )
    except Exception as err:
        logger.error(f"Can't create table backup. {str(err)}")


def rotate_backups(tables):
    """
    Trigger rotation based on time using the Environment
    variable 'BACKUP_RETENTION_DAYS'.
    """
    try:
        paginator = DYNAMODBCLIENT.get_paginator('list_backups')
    except Exception as err:
        logger.error(f"Can't rotate backups. {str(err)}")
    upper_bound = datetime.now() - timedelta(days=int(os.environ.get('BACKUP_RETENTION_DAYS')))

    logger.info(f"Removing backups before the following date: {upper_bound}")

    for page in paginator.paginate(TimeRangeUpperBound=upper_bound):
        for table in page['BackupSummaries']:
            if table['TableName'] in tables:
                DYNAMODBCLIENT.delete_backup(BackupArn=table['BackupArn'])
                logger.info(f"Succesfully removed backup {table['BackupName']}")


def get_table_list():
    """
    Check and pass the Environment variable 'TABLE_REGEX'
    to the function that search and list the tables to backup.
    """
    if os.environ.get('TABLE_REGEX'):
        return get_table_name_by_regex(os.environ.get('TABLE_REGEX'))
    logger.error("No tables configured. Please use TABLE_REGEX")
    return []


def get_table_name_by_regex(pattern):
    """
    Create a list with tables to backup using a regex pattern.
    """
    tables = []
    try:
        paginator = DYNAMODBCLIENT.get_paginator('list_tables')
        logger.info(f"Using regex pattern '{pattern}' to find tables.")
        for page in paginator.paginate():
            for table in page['TableNames']:
                if re.match(pattern, table):
                    tables.append(table)
    except Exception as err:
        logger.error(f"Connection to dynamodb not established. {str(err)}")
    return tables


if __name__ == "__main__":
    main('', '')
