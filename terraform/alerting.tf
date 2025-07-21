resource "aws_sns_topic" "pipeline_alerts" {
  name = "pipeline-alerts"
}

resource "aws_sns_topic_subscription" "pipeline_alerts_email" {
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "email"
  endpoint  = data.aws_organizations_organization.current.master_account_email
}

data "aws_organizations_organization" "current" {}

resource "aws_sns_topic_policy" "pipeline_alerts" {
  arn    = aws_sns_topic.pipeline_alerts.arn
  policy = data.aws_iam_policy_document.pipeline_alerts.json
}

data "aws_iam_policy_document" "pipeline_alerts" {
  statement {
    actions = ["SNS:Publish"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    resources = [aws_sns_topic.pipeline_alerts.arn]
  }
  statement {
    actions = [
      "SNS:Subscribe",
      "SNS:SetTopicAttributes",
      "SNS:RemovePermission",
      "SNS:Receive",
      "SNS:Publish",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:DeleteTopic",
      "SNS:AddPermission",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceOwner"

      values = [data.aws_caller_identity.current.account_id]
    }

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      aws_sns_topic.pipeline_alerts.arn,
    ]

    sid = "__default_statement_ID"
  }
}

resource "aws_cloudwatch_event_rule" "pipeline_alerts" {
  name = "pipeline-alerts"
  event_pattern = jsonencode({
    source      = ["aws.states"]
    detail-type = ["Step Functions Execution Status Change"]
    detail = {
      status          = ["FAILED"],
      stateMachineArn = [module.pipeline_step_function.state_machine_arn]
    }
  })
}

resource "aws_cloudwatch_event_target" "pipeline_alerts_email" {
  rule = aws_cloudwatch_event_rule.pipeline_alerts.name
  arn  = aws_sns_topic.pipeline_alerts.arn
}
