terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
# 005_Terraform/providers.tf

# Provider para la Cuenta 1 (Networking / TGW / DX) - LocalStack
provider "aws" {
  alias                       = "networking"
  region                      = "us-east-1"
  access_key                  = "mock_access_key_networking"
  secret_key                  = "mock_secret_key"
  
  # Omitir validaciones de AWS real
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  # Redirigir el tráfico al contenedor de LocalStack
  endpoints {
    ec2           = "http://localhost:4566"
    ram           = "http://localhost:4566"
    directconnect = "http://localhost:4566"
    sts           = "http://localhost:4566"
  }
}

# Provider para la Cuenta 2 (Servicios / App) - LocalStack
provider "aws" {
  alias                       = "app"
  region                      = "us-east-1"
  access_key                  = "mock_access_key_app"
  secret_key                  = "mock_secret_key"
  
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    ec2           = "http://localhost:4566"
    ram           = "http://localhost:4566"
    sts           = "http://localhost:4566"
  }
}