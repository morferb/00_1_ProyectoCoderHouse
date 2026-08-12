# 1. Llamada a tu modulo de red
module "vpc" {
  source = "./modules/vpc"
  providers = {
    aws = aws.networking
  }
}

module "sg_mgmt_app" {
  source    = "./modules/sg"
  providers = {
    aws = aws.app
  }

  name      = "Security-Group-Mgmt"
  description = "Security Group para gestion de instancias"
  vpc_id    = module.vpc.vpc_id

  ingress_rules = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["172.100.250.0/24"]
      description = "Permitir SSH desde la red de gestion"
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["172.100.250.0/24"]
      description = "Permitir HTTPS desde la red de gestion"
    },
            {
      from_port   = 161
      to_port     = 161
      protocol    = "udp"
      cidr_blocks = ["172.100.250.0/24"]
      description = "Permitir SNMP desde la red de administracion"
      },
    {
      from_port   = 161
      to_port     = 161
      protocol    = "tcp"
      cidr_blocks = ["172.100.250.0/24"]
      description = "Permitir SNMP desde la red de administracion"
    },
  ]
  egress_rules = []
}

module "sg_mgmt_admin" {
  source    = "./modules/sg"
  providers = {
    aws = aws.app
  }
  name      = "Security-Group-Admin"
  description = "Security Group para administracion de instancias"
  vpc_id    = module.vpc.vpc_id

  ingress_rules = []
  egress_rules = [
        {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["172.100.1.0/24"]
      description = "Permitir SSH desde la red de administracion"
      },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["172.100.2.0/24"]
      description = "Permitir SSH desde la red de administracion"
    },
        {
      from_port   = 161
      to_port     = 161
      protocol    = "udp"
      cidr_blocks = ["172.100.1.0/24"]
      description = "Permitir SNMP desde la red de administracion"
      },
    {
      from_port   = 161
      to_port     = 161
      protocol    = "tcp"
      cidr_blocks = ["172.100.2.0/24"]
      description = "Permitir SNMP desde la red de administracion"
    },
  ]
}
# 2. Búsqueda de una AMI de Amazon Linux 2023 (opcional pero recomendado)
data "aws_ami" "amazon_linux" {
  provider    = aws.app
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# 3. Invocacion del nuevo modulo EC2
module "ec2_linux" {
  source = "./modules/ec2"
  providers = {
    aws = aws.app
  }

  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  # Usamos el output que expone el modulo VPC
  subnet_id     = module.vpc.public_subnet_id 
  
  #SG mgmt
  vpc_security_group_ids = [module.sg_mgmt_app.security_group_id]

  tags = {
    Name = "EC2-App-Linux"
    Env  = "Desarrollo"
  }
}

# 4. Invocacion modulo EC2 para 2da instancia
module "ec2_linux_mgmt" {
  source = "./modules/ec2"
  providers = {
    aws = aws.app
  }

  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  # Usamos el output que expone el modulo VPC
  subnet_id     = module.vpc.mgmt_subnet_id 

  #SG mgmt y admin
  vpc_security_group_ids = [
    module.sg_mgmt_app.security_group_id,
    module.sg_mgmt_admin.security_group_id]
  tags = {
    Name = "EC2-MGMT-Linux"
    Env  = "Desarrollo"
  }
}
#-----
#
