# =============================================================================
# VPC — Your own isolated private network in AWS
# Everything we create lives inside this network
# =============================================================================
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16" # IP range: 10.0.0.0 - 10.0.255.255 (65,536 IPs)
  enable_dns_hostnames = true           # Allow resources to have DNS names
  enable_dns_support   = true

  tags = { Name = "${var.project_name}-vpc" }
}

# =============================================================================
# Subnets — Segments within the VPC
# Private = no direct internet access (secure, for DB and Lambda)
# Public  = has internet access (needed for NAT Gateway)
# RDS requires subnets in at least 2 availability zones (a and b)
# =============================================================================
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id      # Lives inside our VPC
  cidr_block        = "10.0.1.0/24"        # 256 IPs: 10.0.1.0 - 10.0.1.255
  availability_zone = "${var.aws_region}a"  # e.g. eu-west-2a

  tags = { Name = "${var.project_name}-private-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"        # Different IP range to avoid overlap
  availability_zone = "${var.aws_region}b"  # e.g. eu-west-2b (different data centre)

  tags = { Name = "${var.project_name}-private-b" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true # Resources here get public IPs

  tags = { Name = "${var.project_name}-public" }
}

# =============================================================================
# Internet Gateway — The front door connecting our VPC to the internet
# Without this, nothing in the VPC can reach the outside world
# =============================================================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "${var.project_name}-igw" }
}

# =============================================================================
# NAT Gateway — Lets private subnet resources make OUTBOUND internet calls
# without being directly exposed to the internet (one-way mirror)
# Lambda needs this to call external APIs, but nobody can call Lambda directly
# The Elastic IP (EIP) gives the NAT a fixed public IP address
# =============================================================================
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = { Name = "${var.project_name}-nat-eip" }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id    # Attach our fixed IP
  subnet_id     = aws_subnet.public.id # NAT sits in the public subnet

  tags = { Name = "${var.project_name}-nat" }
}

# =============================================================================
# Route Tables — Traffic signposts that tell subnets where to send traffic
# Public subnet  → routes through Internet Gateway (direct internet)
# Private subnet → routes through NAT Gateway (outbound only)
# =============================================================================

# Public route table: all traffic (0.0.0.0/0) goes to the internet gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"                  # All traffic
    gateway_id = aws_internet_gateway.main.id  # → Internet Gateway
  }

  tags = { Name = "${var.project_name}-public-rt" }
}

# Associate the public subnet with the public route table
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Private route table: all traffic goes through NAT (outbound only, no inbound)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"              # All traffic
    nat_gateway_id = aws_nat_gateway.main.id   # → NAT Gateway
  }

  tags = { Name = "${var.project_name}-private-rt" }
}

# Associate both private subnets with the private route table
resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}

# =============================================================================
# Security Groups — Firewalls that control what traffic is allowed in/out
# =============================================================================

# Lambda security group: can talk out to anything (needs to reach RDS + internet)
# No ingress rules = nothing can connect TO Lambda directly via the VPC
resource "aws_security_group" "lambda" {
  name_prefix = "${var.project_name}-lambda-"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0         # All ports
    to_port     = 0
    protocol    = "-1"      # All protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-lambda-sg" }
}

# RDS security group: ONLY accepts connections from Lambda, on port 5432 (Postgres)
# No egress rules needed — DB doesn't need to call out
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id] # Only Lambda can connect
  }

  tags = { Name = "${var.project_name}-rds-sg" }
}
