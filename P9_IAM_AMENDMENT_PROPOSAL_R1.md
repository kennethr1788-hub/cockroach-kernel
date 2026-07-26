# P9 IAM Amendment Proposal R1

## Conflict

The frozen P9 contract requires CloudWatch logs for `ck-p9-evaluator` with
one-day retention and simultaneously blocks any wildcard IAM resource. Lambda
creates log-stream names at runtime. An execution role cannot write those
streams using one predeclared exact stream ARN.

## Narrow amendment

Interpret the wildcard stop condition as blocking:

- wildcard actions;
- a global `Resource: *`;
- wildcard accounts, regions, services, log groups, functions, or roles; and
- any wildcard that expands beyond the exact project resource.

Permit only the AWS-required dynamic stream suffix beneath the exact log group:

`arn:aws:logs:us-west-2:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/ck-p9-evaluator:log-stream:*`

The log group is pre-created with one-day retention, so the Lambda execution
role does not receive `logs:CreateLogGroup`. Its only actions are
`logs:CreateLogStream` and `logs:PutLogEvents` on that resource. No network,
database, secret, model, function invocation, S3, queue, IAM, or control-plane
permission is granted to the function.

## Acceptance

- independent non-authoring GLM review is GREEN on this exact proposal;
- template tests reject wildcard actions, global wildcard resources, wrong
  region/account placeholder/log group, and any additional action;
- live account ID substitution and IAM simulation remain post-activation gates;
- no template is deployed while `AWS_ACCOUNT_SETUP_HUMAN_GATE` remains open.

## Kill line

If AWS requires broader permission than the exact log-stream suffix, disable
application logging and revise the evidence design, or keep P9 blocked. Never
grant a broader wildcard to make deployment pass.
