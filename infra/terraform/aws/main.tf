# FinRisk AI Copilot - AWS Infrastructure
# Production-grade Terraform configuration for AWS deployment

terraform {
  required_version = ">= 1.6"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  
  backend "s3" {
    bucket         = "finrisk-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "finrisk-terraform-locks"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "FinRisk AI Copilot"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "FinRisk AI Labs"
      CostCenter  = "Engineering"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local variables
locals {
  name_prefix = "finrisk-${var.environment}"
  
  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)
  
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  intra_subnets   = ["10.0.51.0/24", "10.0.52.0/24", "10.0.53.0/24"]
  
  common_tags = {
    Project     = "FinRisk AI Copilot"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.4"
  
  name = "${local.name_prefix}-vpc"
  cidr = local.vpc_cidr
  
  azs             = local.azs
  private_subnets = local.private_subnets
  public_subnets  = local.public_subnets
  intra_subnets   = local.intra_subnets
  
  enable_nat_gateway     = true
  single_nat_gateway     = false
  enable_vpn_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true
  
  # Enable flow logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true
  
  # Public subnet tags for ALB
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.name_prefix}-eks" = "shared"
    "kubernetes.io/role/elb"                         = "1"
  }
  
  # Private subnet tags for internal LB
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.name_prefix}-eks" = "shared"
    "kubernetes.io/role/internal-elb"                = "1"
  }
  
  tags = local.common_tags
}

# Security Groups
resource "aws_security_group" "eks_additional" {
  name_prefix = "${local.name_prefix}-eks-additional"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-eks-additional"
  })
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.21"
  
  cluster_name    = "${local.name_prefix}-eks"
  cluster_version = "1.28"
  
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true
  cluster_endpoint_public_access_cidrs = var.allowed_cidr_blocks
  
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
    aws-efs-csi-driver = {
      most_recent = true
    }
  }
  
  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets
  
  # EKS Managed Node Groups
  eks_managed_node_groups = {
    # General purpose nodes
    general = {
      name = "general"
      
      instance_types = ["m6i.large", "m5.large", "m5n.large"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 10
      desired_size = 3
      
      ami_type                   = "AL2_x86_64"
      platform                   = "linux"
      cluster_primary_security_group_id = module.eks.cluster_primary_security_group_id
      
      vpc_security_group_ids = [aws_security_group.eks_additional.id]
      
      k8s_labels = {
        Environment = var.environment
        NodeType    = "general"
      }
      
      update_config = {
        max_unavailable_percentage = 25
      }
      
      tags = {
        ExtraTag = "general-nodes"
      }
    }
    
    # High-memory nodes for ML workloads
    ml_workloads = {
      name = "ml-workloads"
      
      instance_types = ["r6i.xlarge", "r5.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 1
      max_size     = 5
      desired_size = 2
      
      ami_type = "AL2_x86_64"
      platform = "linux"
      
      k8s_labels = {
        Environment = var.environment
        NodeType    = "ml-workloads"
      }
      
      taints = {
        ml-workload = {
          key    = "ml-workload"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
      
      tags = {
        ExtraTag = "ml-nodes"
      }
    }
    
    # Spot instances for cost optimization
    spot = {
      name = "spot"
      
      instance_types = ["m5.large", "m5.xlarge", "m5a.large", "m5a.xlarge"]
      capacity_type  = "SPOT"
      
      min_size     = 0
      max_size     = 10
      desired_size = 2
      
      k8s_labels = {
        Environment = var.environment
        NodeType    = "spot"
      }
      
      taints = {
        spot = {
          key    = "spot"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
      
      tags = {
        ExtraTag = "spot-nodes"
      }
    }
  }
  
  # Cluster access entries
  access_entries = {
    admin = {
      kubernetes_groups = []
      principal_arn     = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      
      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }
  
  tags = local.common_tags
}

# RDS Aurora PostgreSQL Cluster
module "aurora" {
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 8.5"
  
  name               = "${local.name_prefix}-aurora"
  engine             = "aurora-postgresql"
  engine_version     = "15.4"
  database_name      = "finrisk"
  master_username    = "finrisk_admin"
  manage_master_user_password = true
  
  instances = {
    writer = {
      instance_class      = "db.r6g.large"
      publicly_accessible = false
    }
    reader1 = {
      identifier          = "${local.name_prefix}-reader-1"
      instance_class      = "db.r6g.large"
      publicly_accessible = false
    }
    reader2 = {
      identifier          = "${local.name_prefix}-reader-2"
      instance_class      = "db.r6g.large"
      publicly_accessible = false
    }
  }
  
  vpc_id               = module.vpc.vpc_id
  db_subnet_group_name = module.vpc.database_subnet_group_name
  security_group_rules = {
    vpc_ingress = {
      cidr_blocks = [local.vpc_cidr]
    }
  }
  
  apply_immediately   = true
  skip_final_snapshot = false
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  backup_retention_period      = 30
  preferred_backup_window      = "07:00-09:00"
  preferred_maintenance_window = "sun:09:00-sun:10:00"
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  
  tags = local.common_tags
}

# ElastiCache Redis Cluster
module "elasticache" {
  source = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.2"
  
  cluster_id               = "${local.name_prefix}-redis"
  description              = "FinRisk Redis cluster"
  
  engine_version           = "7.0"
  port                     = 6379
  parameter_group_name     = "default.redis7"
  node_type                = "cache.r6g.large"
  num_cache_nodes          = 3
  
  subnet_group_name        = "${local.name_prefix}-redis-subnet-group"
  subnet_ids               = module.vpc.private_subnets
  
  security_group_ids       = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth.result
  
  maintenance_window       = "sun:05:00-sun:09:00"
  snapshot_window          = "03:00-05:00"
  snapshot_retention_limit = 7
  
  tags = local.common_tags
}

resource "aws_security_group" "redis" {
  name_prefix = "${local.name_prefix}-redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis"
  })
}

# OpenSearch Domain
resource "aws_opensearch_domain" "finrisk" {
  domain_name    = "${local.name_prefix}-opensearch"
  engine_version = "OpenSearch_2.9"
  
  cluster_config {
    instance_type            = "r6g.large.search"
    instance_count           = 3
    dedicated_master_enabled = true
    master_instance_type     = "r6g.medium.search"
    master_instance_count    = 3
    zone_awareness_enabled   = true
    
    zone_awareness_config {
      availability_zone_count = 3
    }
  }
  
  vpc_options {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.opensearch.id]
  }
  
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 100
    throughput  = 250
  }
  
  encrypt_at_rest {
    enabled = true
  }
  
  node_to_node_encryption {
    enabled = true
  }
  
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  
  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "finrisk_admin"
      master_user_password = random_password.opensearch_master.result
    }
  }
  
  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch.arn
    log_type                 = "INDEX_SLOW_LOGS"
  }
  
  tags = local.common_tags
}

resource "aws_security_group" "opensearch" {
  name_prefix = "${local.name_prefix}-opensearch"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-opensearch"
  })
}

# MSK Kafka Cluster
resource "aws_msk_cluster" "finrisk" {
  cluster_name           = "${local.name_prefix}-kafka"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3
  
  broker_node_group_info {
    instance_type   = "kafka.m5.large"
    client_subnets  = module.vpc.private_subnets
    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
    security_groups = [aws_security_group.msk.id]
  }
  
  encryption_info {
    encryption_at_rest_kms_key_id = aws_kms_key.msk.arn
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  
  configuration_info {
    arn      = aws_msk_configuration.finrisk.arn
    revision = aws_msk_configuration.finrisk.latest_revision
  }
  
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk.name
      }
    }
  }
  
  tags = local.common_tags
}

resource "aws_security_group" "msk" {
  name_prefix = "${local.name_prefix}-msk"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 9092
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  ingress {
    from_port   = 2181
    to_port     = 2181
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-msk"
  })
}

# S3 Buckets
resource "aws_s3_bucket" "artifacts" {
  bucket = "${local.name_prefix}-artifacts-${random_id.bucket_suffix.hex}"
  
  tags = local.common_tags
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${local.name_prefix}-data-lake-${random_id.bucket_suffix.hex}"
  
  tags = local.common_tags
}

resource "aws_s3_bucket" "ml_models" {
  bucket = "${local.name_prefix}-ml-models-${random_id.bucket_suffix.hex}"
  
  tags = local.common_tags
}

# Random resources
resource "random_password" "redis_auth" {
  length  = 32
  special = true
}

resource "random_password" "opensearch_master" {
  length  = 16
  special = true
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# KMS Keys
resource "aws_kms_key" "msk" {
  description             = "KMS key for MSK encryption"
  deletion_window_in_days = 7
  
  tags = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "opensearch" {
  name              = "/aws/opensearch/domains/${local.name_prefix}-opensearch"
  retention_in_days = 14
  
  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aws/msk/${local.name_prefix}-kafka"
  retention_in_days = 14
  
  tags = local.common_tags
}

# MSK Configuration
resource "aws_msk_configuration" "finrisk" {
  kafka_versions = ["3.5.1"]
  name           = "${local.name_prefix}-kafka-config"
  
  server_properties = <<PROPERTIES
auto.create.topics.enable=false
default.replication.factor=3
min.insync.replicas=2
num.partitions=3
log.retention.hours=168
compression.type=snappy
PROPERTIES
}
