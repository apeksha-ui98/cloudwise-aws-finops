resource "aws_cloudwatch_dashboard" "cloudwise" {
  dashboard_name = "CloudWise-CostOptimization"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title   = "Total Monthly Waste (INR)"
          metrics = [["CloudWise/CostOptimization", "TotalMonthlyWasteINR"]]
          period  = 604800
          stat    = "Maximum"
          region  = "ap-south-1"
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Idle Resources Count"
          metrics = [
            ["CloudWise/CostOptimization", "IdleEC2Count"],
            ["CloudWise/CostOptimization", "UnattachedEBSCount"],
            ["CloudWise/CostOptimization", "IdleEIPCount"]
          ]
          period = 604800
          stat   = "Maximum"
          region = "ap-south-1"
        }
      }
    ]
  })
}
