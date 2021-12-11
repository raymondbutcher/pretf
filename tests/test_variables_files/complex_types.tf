variable "aws_credentials" {
  type = map({
    nonprod = map(string)
    prod    = map(string)
  })
  default = {
    nonprod = {
      profile = "pretf-nonprod"
    }

    prod = {
      profile = "pretf-prod"
    }
  }
}
