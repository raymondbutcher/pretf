variable "aws_credentials_dev" {
  default = {
    profile = "pretf-nonprod"
  }
}

variable "aws_credentials_prod" {
  default = {
    profile = "pretf-prod"
  }
}
