#!/usr/bin/env python3
import os
import aws_cdk as cdk
import configparser
from automation.automation_stack import AutomationStack, RoleUpdateAutomationStackInToolchain

config = configparser.ConfigParser()
os.chdir("../")
config.read('config.ini')

app = cdk.App()
AutomationStack(app, "AutomationStack",
    config,
    env=cdk.Environment(account=config['TARGET_ACCOUNT']['AccountNumber'], region=config['TARGET_ACCOUNT']['Region']),
    synthesizer=cdk.DefaultStackSynthesizer(
        generate_bootstrap_version_rule=False
    )
)

RoleUpdateAutomationStackInToolchain(app, "RoleUpdateAutomationStackInToolchain",
    config,
    env=cdk.Environment(account=config['TOOLCHAIN_ACCOUNT']['ToolchainAccountNumber'], region=config['TOOLCHAIN_ACCOUNT']['ToolchainRegion']),
    synthesizer=cdk.DefaultStackSynthesizer(
        generate_bootstrap_version_rule=False
    )
)

app.synth()
