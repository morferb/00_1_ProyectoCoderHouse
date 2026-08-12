variable "name" {
  description = "Nombre del Security Group"
  type        = string
}

variable "description" {
  description = "Descripción del Security Group"
  type        = string
  default     = "Security Group gestionado por Terraform"
}

variable "vpc_id" {
  description = "ID de la VPC a la que se asociará el Security Group"
  type        = string
}

variable "ingress_rules" {
  description = "Lista de reglas de entrada"
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))
  default = []
}
variable "egress_rules" {
  description = "Lista de reglas de salida"
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))
  default = []
}

variable "tags" {
  description = "Etiquetas para el Security Group"
  type        = map(string)
  default     = {}
}