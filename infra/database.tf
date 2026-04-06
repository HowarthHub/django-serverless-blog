# RDS PostgreSQL — Managed database, same as our local Docker Postgres
# Sits in private subnets so only Lambda can reach it

# Subnet group tells RDS which subnets it can use (needs at least 2 AZs)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = { Name = "${var.project_name}-db-subnet" }
}

# The actual PostgreSQL database instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"  # Name in AWS console
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = "db.t3.micro"             # Free tier eligible

  allocated_storage = 20                      # 20GB storage (free tier = up to 20GB)
  storage_type      = "gp3"                   # General purpose SSD

  db_name  = var.db_name                      # Creates this database on startup
  username = var.db_username                  # Master username
  password = var.db_password                  # Master password (from tfvars/secrets)

  db_subnet_group_name   = aws_db_subnet_group.main.name  # Which subnets to use
  vpc_security_group_ids = [aws_security_group.rds.id]     # Firewall rules

  skip_final_snapshot = true                  # Don't create backup on destroy (fine for dev)
  publicly_accessible = false                 # Not reachable from the internet

  tags = { Name = "${var.project_name}-db" }
}
