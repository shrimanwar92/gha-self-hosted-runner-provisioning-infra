import aws_cdk as core
import aws_cdk.assertions as assertions

from automation.automation_stack import AutomationStack

# example tests. To run these tests, uncomment this file along with the example
# resource in automation/automation_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AutomationStack(app, "automation")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
