resource "aws_vpc" "poc_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "genai-poc-vpc"
  }
}

resource "aws_internet_gateway" "poc_igw" {
  vpc_id = aws_vpc.poc_vpc.id
}

resource "aws_route_table" "poc_public_rt" {
  vpc_id = aws_vpc.poc_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.poc_igw.id
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "poc_subnet_1" {
  vpc_id                  = aws_vpc.poc_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
}

resource "aws_subnet" "poc_subnet_2" {
  vpc_id                  = aws_vpc.poc_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
}

resource "aws_route_table_association" "poc_rta_1" {
  subnet_id      = aws_subnet.poc_subnet_1.id
  route_table_id = aws_route_table.poc_public_rt.id
}

resource "aws_route_table_association" "poc_rta_2" {
  subnet_id      = aws_subnet.poc_subnet_2.id
  route_table_id = aws_route_table.poc_public_rt.id
}

resource "aws_db_subnet_group" "poc_db_subnet_group" {
  name       = "genai-poc-db-subnet-group"
  subnet_ids = [aws_subnet.poc_subnet_1.id, aws_subnet.poc_subnet_2.id]
}

resource "aws_security_group" "rds_sg" {
  name        = "learningdb-rds-sg"
  description = "Security group for learningdb RDS instance"
  vpc_id      = aws_vpc.poc_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_rds_cluster" "learningdb" {
  cluster_identifier      = "trainingdb-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4" # Aurora PostgreSQL 15 is highly stable for Serverless v2
  database_name           = "trainingdb"
  master_username         = var.db_username
  master_password         = var.db_password
  skip_final_snapshot     = true
  db_subnet_group_name    = aws_db_subnet_group.poc_db_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]

  serverlessv2_scaling_configuration {
    max_capacity = 2.0
    min_capacity = 0.5
  }

  depends_on = [
    aws_route_table_association.poc_rta_1,
    aws_route_table_association.poc_rta_2
  ]
}

resource "aws_rds_cluster_instance" "learningdb_instance" {
  identifier          = "trainingdb-instance-1"
  cluster_identifier  = aws_rds_cluster.learningdb.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.learningdb.engine
  engine_version      = aws_rds_cluster.learningdb.engine_version
  publicly_accessible = true
}
