resource "aws_sqs_queue" "scraped_items" {
  name                        = "cac-pipeline-scraped-items.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.scraped_items_dlq.arn
    maxReceiveCount     = 2
  })
}

resource "aws_sqs_queue" "scraped_items_dlq" {
  name                        = "cac-pipeline-scraped-items-dlq.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}

resource "aws_sqs_queue_redrive_allow_policy" "scraped_items" {
  queue_url = aws_sqs_queue.scraped_items_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.scraped_items.arn]
  })
}

data "aws_iam_policy_document" "allow_send_to_scraped_items" {
  version = "2012-10-17"
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.scraped_items.arn]
  }
}

resource "aws_iam_policy" "allow_send_to_scraped_items" {
  name   = "allow-send-to-scraped-items"
  policy = data.aws_iam_policy_document.allow_send_to_scraped_items.json
}

resource "aws_iam_role_policy_attachment" "scraped_items_queue_policy" {
  role       = module.scraper.role.name
  policy_arn = aws_iam_policy.allow_send_to_scraped_items.arn
}

resource "aws_iam_role" "scraped_items_pipe_role" {
  name               = "scraped-items-pipe"
  assume_role_policy = data.aws_iam_policy_document.scraped_items_pipe_role_trust_policy.json
}

data "aws_iam_policy_document" "scraped_items_pipe_role_trust_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["pipes.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_iam_role_policy" "scraped_items_pipe_source" {
  name   = "scraped-items-pipe-source"
  role   = aws_iam_role.scraped_items_pipe_role.id
  policy = data.aws_iam_policy_document.scraped_items_pipe_source_policy.json
}

data "aws_iam_policy_document" "scraped_items_pipe_source_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
      "sqs:SendMessage"
    ]
    resources = [aws_sqs_queue.scraped_items.arn]
  }
}

resource "aws_iam_role_policy" "scraped_items_pipe_target" {
  name   = "scraped-items-pipe-target"
  role   = aws_iam_role.scraped_items_pipe_role.id
  policy = data.aws_iam_policy_document.scraped_items_pipe_target_policy.json
}

data "aws_iam_policy_document" "scraped_items_pipe_target_policy" {
  statement {
    effect = "Allow"
    actions = [
      "states:StartExecution"
    ]
    resources = [module.pipeline_step_function.state_machine_arn]
  }
}

resource "aws_pipes_pipe" "scraped_items" {
  name     = "scraped-items"
  role_arn = aws_iam_role.scraped_items_pipe_role.arn
  source   = aws_sqs_queue.scraped_items.arn
  target   = module.pipeline_step_function.state_machine_arn

  target_parameters {
    step_function_state_machine_parameters {
      invocation_type = "REQUEST_RESPONSE"
    }
  }
}
