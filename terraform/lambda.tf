data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../"
  output_path = "${path.module}/cloudwise.zip"
  excludes    = ["terraform", "venv", ".git", "__pycache__", ".env"]
}

resource "aws_lambda_function" "cloudwise" {
  filename         = "${path.module}/cloudwise.zip"
  function_name    = "CloudWiseScanner"
  role             = aws_iam_role.cloudwise_lambda_role.arn
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 300
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = "production"
    }
  }
}

resource "aws_cloudwatch_event_rule" "weekly_scan" {
  name                = "CloudWiseWeeklyScan"
  description         = "Triggers CloudWise scanner every Monday 9am UTC"
  schedule_expression = "cron(0 9 ? * MON *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly_scan.name
  target_id = "CloudWiseLambda"
  arn       = aws_lambda_function.cloudwise.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cloudwise.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_scan.arn
}
