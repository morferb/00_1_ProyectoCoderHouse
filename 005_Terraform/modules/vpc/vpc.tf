# 1. Creación de la VPC existente
resource "aws_vpc" "Laboratorio" {
  cidr_block = "10.100.0.0/16"
  tags = {
    Name = "Laboratorio"
  }
}

# 2. Subred Pública (asigna IP pública automáticamente a las instancias)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.Laboratorio.id
  cidr_block              = "10.100.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "Laboratorio-Public-Subnet"
  }
}

# 3. Subred Privada (sin IP pública automática)
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.Laboratorio.id
  cidr_block        = "10.100.2.0/24"
  tags = {
    Name = "Laboratorio-Private-Subnet"
  }
}

# 4. Internet Gateway para permitir el tráfico de internet en la subred pública
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.Laboratorio.id
  tags = {
    Name = "Laboratorio-IGW"
  }
}

# 5. Tabla de enrutamiento pública
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.Laboratorio.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "Laboratorio-Public-RT"
  }
}

# 5.B Tabla de enrutamiento privada
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.Laboratorio.id

  tags = {
    Name = "Laboratorio-private-RT"
  }
}
# 6. Asociación de la tabla de enrutamiento con la subred pública
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}