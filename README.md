# Scheduled Lambda for DynamoDB backup

This project create an Amazon CloudWatch Events rule to trigger an AWS Lambda function in your Aws Account.
The Aws Lambda is scheduled every 6 hours and removes backups older than 2 days. The deletion of older backups
can be enabled or disabled by one environment variable. It use a regex pattern (defined in the lambda environment)
to find out which tables to backup.

The only part you have to change to adapt to your prerequisites is the Lambda environment.

```
TABLE_REGEX => (string) used to find which tables to backup
BACKUP_REMOVAL_ENABLED => (boolean) Enable or disable the backup rotation
BACKUP_RETENTION_DAYS => (int) Number of days to retain
```

This project is created with the AWS Cloud Development Kit.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Commands for VirtualEnv setup (optional)

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .env directory. 

To manually create a virtualenv on MacOS and Linux:

```sh
$ pip3 install virtualenv # Only first time to install the virtualenv module, skip if already done.
$ virtualenv .env
$ source .env/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ make requirements
```

At this point you can now synthesize the CloudFormation template for this code and deploy.

```
$ cdk synth
$ cdk deploy
```

# Useful commands for manage infrastructure:

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack
 * `cdk destroy`     destroy this stack
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

