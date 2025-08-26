# FinRisk AI Copilot - Terraform Variables

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
  
  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "AWS region must be in the format 'us-west-2'."
  }
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the EKS cluster endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT gateway for all private subnets"
  type        = bool
  default     = false
}

# Database configuration
variable "aurora_instance_class" {
  description = "Instance class for Aurora PostgreSQL"
  type        = string
  default     = "db.r6g.large"
}

variable "aurora_backup_retention_period" {
  description = "Backup retention period for Aurora cluster"
  type        = number
  default     = 30
  
  validation {
    condition     = var.aurora_backup_retention_period >= 7 && var.aurora_backup_retention_period <= 35
    error_message = "Backup retention period must be between 7 and 35 days."
  }
}

variable "aurora_preferred_backup_window" {
  description = "Preferred backup window for Aurora cluster"
  type        = string
  default     = "07:00-09:00"
}

variable "aurora_preferred_maintenance_window" {
  description = "Preferred maintenance window for Aurora cluster"
  type        = string
  default     = "sun:09:00-sun:10:00"
}

# Redis configuration
variable "redis_node_type" {
  description = "Node type for ElastiCache Redis"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes for Redis cluster"
  type        = number
  default     = 3
  
  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 20
    error_message = "Number of cache nodes must be between 1 and 20."
  }
}

variable "redis_parameter_group_name" {
  description = "Parameter group name for Redis"
  type        = string
  default     = "default.redis7"
}

# OpenSearch configuration
variable "opensearch_instance_type" {
  description = "Instance type for OpenSearch cluster"
  type        = string
  default     = "r6g.large.search"
}

variable "opensearch_instance_count" {
  description = "Number of instances in OpenSearch cluster"
  type        = number
  default     = 3
  
  validation {
    condition     = var.opensearch_instance_count >= 1 && var.opensearch_instance_count <= 10
    error_message = "OpenSearch instance count must be between 1 and 10."
  }
}

variable "opensearch_ebs_volume_size" {
  description = "EBS volume size for OpenSearch instances (GB)"
  type        = number
  default     = 100
  
  validation {
    condition     = var.opensearch_ebs_volume_size >= 10 && var.opensearch_ebs_volume_size <= 3584
    error_message = "EBS volume size must be between 10 and 3584 GB."
  }
}

variable "opensearch_ebs_volume_type" {
  description = "EBS volume type for OpenSearch instances"
  type        = string
  default     = "gp3"
  
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.opensearch_ebs_volume_type)
    error_message = "EBS volume type must be one of: gp2, gp3, io1, io2."
  }
}

# MSK Kafka configuration
variable "kafka_instance_type" {
  description = "Instance type for MSK Kafka brokers"
  type        = string
  default     = "kafka.m5.large"
}

variable "kafka_number_of_broker_nodes" {
  description = "Number of broker nodes in MSK cluster"
  type        = number
  default     = 3
  
  validation {
    condition     = var.kafka_number_of_broker_nodes >= 3 && var.kafka_number_of_broker_nodes <= 15
    error_message = "Number of Kafka broker nodes must be between 3 and 15."
  }
}

variable "kafka_ebs_volume_size" {
  description = "EBS volume size for Kafka brokers (GB)"
  type        = number
  default     = 100
  
  validation {
    condition     = var.kafka_ebs_volume_size >= 1 && var.kafka_ebs_volume_size <= 16384
    error_message = "Kafka EBS volume size must be between 1 and 16384 GB."
  }
}

variable "kafka_version" {
  description = "Kafka version for MSK cluster"
  type        = string
  default     = "3.5.1"
}

# EKS Node Groups configuration
variable "eks_node_groups" {
  description = "EKS managed node groups configuration"
  type = map(object({
    instance_types = list(string)
    capacity_type  = string
    min_size      = number
    max_size      = number
    desired_size  = number
    disk_size     = number
    ami_type      = string
    labels        = map(string)
    taints = map(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  
  default = {
    general = {
      instance_types = ["m6i.large", "m5.large", "m5n.large"]
      capacity_type  = "ON_DEMAND"
      min_size      = 2
      max_size      = 10
      desired_size  = 3
      disk_size     = 50
      ami_type      = "AL2_x86_64"
      labels = {
        NodeType = "general"
      }
      taints = {}
    }
    
    ml_workloads = {
      instance_types = ["r6i.xlarge", "r5.xlarge"]
      capacity_type  = "ON_DEMAND"
      min_size      = 1
      max_size      = 5
      desired_size  = 2
      disk_size     = 100
      ami_type      = "AL2_x86_64"
      labels = {
        NodeType = "ml-workloads"
      }
      taints = {
        ml-workload = {
          key    = "ml-workload"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
    
    spot = {
      instance_types = ["m5.large", "m5.xlarge", "m5a.large", "m5a.xlarge"]
      capacity_type  = "SPOT"
      min_size      = 0
      max_size      = 10
      desired_size  = 2
      disk_size     = 50
      ami_type      = "AL2_x86_64"
      labels = {
        NodeType = "spot"
      }
      taints = {
        spot = {
          key    = "spot"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }
}

# Security configuration
variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for all services"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit for all services"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

# Monitoring and logging
variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 14
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.cloudwatch_log_retention_days)
    error_message = "CloudWatch log retention must be a valid value."
  }
}

variable "enable_performance_insights" {
  description = "Enable Performance Insights for RDS"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition     = contains([7, 731], var.performance_insights_retention_period)
    error_message = "Performance Insights retention period must be 7 or 731 days."
  }
}

# Cost optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = true
}

variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling for predictable workloads"
  type        = bool
  default     = false
}

# Backup and disaster recovery
variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for disaster recovery"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "Region for cross-region backups"
  type        = string
  default     = "us-east-1"
}

# Compliance and governance
variable "enable_config_rules" {
  description = "Enable AWS Config rules for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for audit logging"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable GuardDuty for threat detection"
  type        = bool
  default     = true
}

# Additional tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Domain and DNS
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "finrisk.ai"
}

variable "create_route53_zone" {
  description = "Create Route53 hosted zone for the domain"
  type        = bool
  default     = false
}

# SSL/TLS
variable "ssl_certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

variable "create_acm_certificate" {
  description = "Create ACM certificate for the domain"
  type        = bool
  default     = false
}
