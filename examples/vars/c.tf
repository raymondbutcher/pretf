variable "five" {
  type = string
}

variable "six" {
  type    = list(string)
  default = ["six1", "six2"]
}

variable "seven" {}
