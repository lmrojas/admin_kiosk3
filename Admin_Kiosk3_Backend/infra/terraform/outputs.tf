output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.main.endpoint
}

output "db_endpoint" {
  description = "Endpoint for RDS database"
  value       = aws_db_instance.postgres.endpoint
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
} 