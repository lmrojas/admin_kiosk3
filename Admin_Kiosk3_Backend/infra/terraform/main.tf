# Proveedor AWS
provider "aws" {
  region = var.aws_region
}

# VPC y Networking
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "kiosk-vpc"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "kiosk-cluster"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}

# RDS Database
resource "aws_db_instance" "postgres" {
  identifier        = "kiosk-db"
  engine            = "postgres"
  engine_version    = "13"
  instance_class    = "db.t3.medium"
  allocated_storage = 20
  
  name     = "admin_kiosk3"
  username = "user"
  password = var.db_password
} 