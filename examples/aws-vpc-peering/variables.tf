variable "aws_profiles" {
  type = map(string)
  default = {
    nonprod = "pretf-nonprod"
    prod    = "pretf-prod"
  }
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "aws_version" {
  type    = string
  default = ">= 2.15.0"
}
