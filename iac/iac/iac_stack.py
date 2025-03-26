from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy
)
import json
from constructs import Construct

class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC for the Aurora cluster
        vpc = ec2.Vpc(self, "BedrockVPC", max_azs=2, nat_gateways=0)
        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )

# Create a secret in Secrets Manager for the database credentials
        database_secret = secretsmanager.Secret(
            self,
            "AuroraDatabaseSecret",
            secret_name="AuroraDbCredentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": bedrock_user}),
                generate_string_key="password",
                exclude_punctuation=True,
            ),
        )
 
# Create an Aurora PostgreSQL V2 Serverless cluster
        aurora_cluster = rds.DatabaseCluster(
            self,
            "BedrockAuroraCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_14_10),
            vpc=vpc,
            default_database_name=default_database_name,
            credentials=rds.Credentials.from_secret(database_secret),
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=1,
            writer=rds.ClusterInstance.serverless_v2(id="AuroraWriter",
                                                     instance_identifier="BedrockAuroraCluster-writer",
                                                     auto_minor_version_upgrade=False,
                                                     allow_major_version_upgrade=False,
                                                     publicly_accessible=False,
                                                     ),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            enable_data_api=True,
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY
        )
