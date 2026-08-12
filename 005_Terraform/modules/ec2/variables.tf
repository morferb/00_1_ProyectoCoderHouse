variable "ami" {
  description = "ID de la Amazon Machine Image (AMI)"
  type        = string
}

variable "instance_type" {
  description = "El tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "subnet_id" {
  description = "El ID de la subred donde se desplegará la instancia"
  type        = string
}

variable "tags" {
  description = "Etiquetas a aplicar a la instancia"
  type        = map(string)
  default     = {}
}

variable "vpc_security_group_ids" {
  description = "Lista de IDs de Security Groups a asociar"
  type        = list(string)
  default     = []
}