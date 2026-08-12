output "instance_id" {
  description = "El ID de la instancia EC2 creada"
  value       = aws_instance.this.id
}

output "public_ip" {
  description = "La IP pública de la instancia (si aplica)"
  value       = aws_instance.this.public_ip
}