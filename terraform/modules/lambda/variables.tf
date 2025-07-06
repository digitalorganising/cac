variable "name" {
  type        = string
  description = "The name of the lambda function"
}

variable "image_uri" {
  type        = string
  description = "The image uri of the lambda function"
}

variable "image_command" {
  type        = list(string)
  default     = []
  description = "The command to run in the lambda function"
}

variable "environment" {
  type        = map(string)
  default     = {}
  description = "The environment variables for the lambda function"
}

variable "timeout" {
  type        = number
  default     = 60 * 5
  description = "The timeout of the lambda function"
}

variable "memory_size" {
  type        = number
  default     = 1024
  description = "The memory size of the lambda function"
}
