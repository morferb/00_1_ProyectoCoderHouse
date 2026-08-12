output "public_subnet_id" {
  description = "ID de la subred pública del Laboratorio"
  value       = aws_subnet.public.id
}
output "private_subnet_id" {
  description = "ID de la subred privada del Laboratorio"
  value       = aws_subnet.private.id
}
output "mgmt_subnet_id" {
  description = "ID de la subred de gestión del Laboratorio"
  value       = aws_subnet.mgmt.id
}
output "vpc_id" {
  description = "El ID de la VPC Laboratorio"
  value       = aws_vpc.Laboratorio.id
}