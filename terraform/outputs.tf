output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.nanoquant_instance.public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.nanoquant_instance.private_ip
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.nanoquant_vpc.id
}

output "subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public_subnet.id
}