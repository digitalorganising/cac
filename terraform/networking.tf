resource "aws_vpc" "digitalorganising_cac_vpc" {
  cidr_block                       = "10.0.0.0/16"
  assign_generated_ipv6_cidr_block = true

  tags = {
    Name = "digitalorganising-cac-vpc"
  }
}

resource "aws_internet_gateway" "digitalorganising_cac_igw" {
  vpc_id = aws_vpc.digitalorganising_cac_vpc.id

  tags = {
    Name = "digitalorganising-cac-igw"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.digitalorganising_cac_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.digitalorganising_cac_igw.id
  }

  route {
    ipv6_cidr_block = "::/0"
    gateway_id      = aws_internet_gateway.digitalorganising_cac_igw.id
  }

  tags = {
    Name = "digitalorganising-cac-public-ipv4-route-table"
  }
}

resource "aws_subnet" "public_subnets" {
  count = 3

  vpc_id          = aws_vpc.digitalorganising_cac_vpc.id
  cidr_block      = cidrsubnet(aws_vpc.digitalorganising_cac_vpc.cidr_block, 8, count.index)
  ipv6_cidr_block = cidrsubnet(aws_vpc.digitalorganising_cac_vpc.ipv6_cidr_block, 8, count.index)

  tags = {
    Name = "public-${count.index}"
  }
}

resource "aws_subnet" "private_subnets" {
  count = 3

  vpc_id          = aws_vpc.digitalorganising_cac_vpc.id
  cidr_block      = cidrsubnet(aws_vpc.digitalorganising_cac_vpc.cidr_block, 8, count.index + length(aws_subnet.public_subnets))
  ipv6_cidr_block = cidrsubnet(aws_vpc.digitalorganising_cac_vpc.ipv6_cidr_block, 8, count.index + length(aws_subnet.public_subnets))

  tags = {
    Name = "private-${count.index}"
  }
}

resource "aws_route_table_association" "public_route_table_associations" {
  for_each       = { for index, subnet in aws_subnet.public_subnets : index => subnet.id }
  subnet_id      = each.value
  route_table_id = aws_route_table.public_route_table.id
}

