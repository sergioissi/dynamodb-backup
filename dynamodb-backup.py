from aws_cdk import (
    aws_events,
    aws_iam,
    aws_lambda,
    aws_logs,
    aws_events_targets,
    core
)


class LambdaDynamoDBBackup(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        lambdaFn = aws_lambda.Function(
            self, "function",
            code=aws_lambda.AssetCode('./src'),
            handler="lambda_handler.main",
            function_name="dynamodb-backup",
            log_retention=aws_logs.RetentionDays.THREE_MONTHS,
            timeout=core.Duration.seconds(300),
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            environment={'TABLE_REGEX': 'production',
                         'BACKUP_REMOVAL_ENABLED': 'true',
                         'BACKUP_RETENTION_DAYS': '2'
                        }
        )
        lambdaFn.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=['dynamodb:ListTables',
                         'dynamodb:ListBackups',
                         'dynamodb:CreateBackup',
                         'dynamodb:DeleteBackup'],
                resources=['*'],
            )
        )

        # Run every 6 hours
        rule = aws_events.Rule(
            self, "Rule",
            schedule=aws_events.Schedule.cron(
                minute='01',
                hour='00,06,12,18')
        )
        rule.add_target(aws_events_targets.LambdaFunction(lambdaFn))


app = core.App()
LambdaDynamoDBBackup(app, "dynamodb-backup", env={'region': 'eu-west-1'})
app.synth()
