resource "aws_scheduler_schedule" "check_outcomes" {
  name        = "check-outcomes"
  description = "Triggers an execution of the pipeline, checking for new outcomes"

  # Run between 7am and 7pm, Monday to Friday
  schedule_expression          = "cron(0 7-19 ? * MON-FRI *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 5
  }

  target {
    arn      = module.pipeline_step_function.state_machine_arn
    role_arn = aws_iam_role.schedule_execution_role.arn
    input = jsonencode({
      "indexSuffix" = "0719"
    })
  }
}

resource "aws_iam_role" "schedule_execution_role" {
  name               = "pipeline-schedule-execution"
  assume_role_policy = data.aws_iam_policy_document.schedule_execution_role_assume_policy.json
}

data "aws_iam_policy_document" "schedule_execution_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "schedule_state_machine_execution" {
  name   = "pipeline-schedule-state-machine-execution"
  role   = aws_iam_role.schedule_execution_role.id
  policy = data.aws_iam_policy_document.schedule_state_machine_execution_policy.json
}

data "aws_iam_policy_document" "schedule_state_machine_execution_policy" {
  statement {
    actions   = ["states:StartExecution"]
    resources = [module.pipeline_step_function.state_machine_arn]
  }
}
