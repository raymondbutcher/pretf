variable "aws_profile" {
  default = "pretf"
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "envtype" {
  default = "nonprod"
}

variable "user_names" {
  default = ["pretf-iam-user-1", "pretf-iam-user-2"]
}

variable "security_group_allowed_cidrs" {
  default = [
    "1.1.1.1/32",
    "8.8.8.8/32",
    "10.0.0.0/24",
    "192.168.0.0/24",
  ]
}
