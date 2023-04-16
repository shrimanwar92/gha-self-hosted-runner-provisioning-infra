from aws_cdk import (
    Stack,
    aws_iam as iam
)
from constructs import Construct
import ast

class AutomationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ec2_instance_profile_role = iam.Role(self, "instance-profile-role",
            role_name = config['INSTANCE_PROFILE_ROLE']['RoleName'],
            assumed_by = iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        iam.CfnInstanceProfile(self, "instance-profile",
            roles = [ec2_instance_profile_role.role_name],
            instance_profile_name = ec2_instance_profile_role.role_name
        )

        ec2_instance_profile_role.add_to_policy(
            iam.PolicyStatement(
                effect = iam.Effect.ALLOW,
                resources = ["*"],
                actions = ast.literal_eval(config['INSTANCE_PROFILE_ROLE']['Permission'])
            )
        )

        lambda_role = iam.Role(self, "lambda-role",
            role_name = config['TARGET_ACCOUNT']['RoleName'],
            assumed_by = iam.CompositePrincipal(
                iam.ServicePrincipal("lambda.amazonaws.com"),
                iam.AnyPrincipal() #important to set trust relationship, so that this can be assumed by toolchain account
            )
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect = iam.Effect.ALLOW,
                resources = ["*"],
                actions = ast.literal_eval(config['TARGET_ACCOUNT']['Permission'])
            )
        )





class RoleUpdateAutomationStackInToolchain(Stack):
    def __init__(self, scope: Construct, construct_id: str, config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        import_role = iam.Role.from_role_name(self, 'import-and-update-role',
            role_name = config['TOOLCHAIN_ACCOUNT']['ToolchainAccountLambdaRoleName']                
        )

        import_role.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:iam::{config['TARGET_ACCOUNT']['AccountNumber']}:role/{config['TARGET_ACCOUNT']['RoleName']}",
                    f"arn:aws:iam::{config['TARGET_ACCOUNT']['AccountNumber']}:role/{config['TARGET_ACCOUNT']['RoleName']}/*"
                ],
                actions=["sts:AssumeRole"]
            )
        )
