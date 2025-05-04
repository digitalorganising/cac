locals {
  instance_type       = "t4g.small"
  instance_ami_family = "amzn2-ami-ecs-hvm-*-arm64-ebs"
}

resource "aws_ecs_cluster" "search" {
  name = "search-cluster"
}

resource "aws_ecs_cluster_capacity_providers" "search" {
  cluster_name       = aws_ecs_cluster.search.name
  capacity_providers = [aws_ecs_capacity_provider.search.name]
}

resource "aws_ecs_capacity_provider" "search" {
  name = "search-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.search.arn

    managed_scaling {
      status                    = "ENABLED"
      maximum_scaling_step_size = 1
      target_capacity           = 100
    }
  }
}

resource "aws_autoscaling_group" "search" {
  name                = "search-cluster-asg"
  max_size            = 1
  default_cooldown    = 180
  vpc_zone_identifier = aws_subnet.public_subnets[*].id
  force_delete        = true

  min_size                  = 0
  health_check_type         = "EC2"
  health_check_grace_period = 180

  launch_template {
    id      = aws_launch_template.launch_template.id
    version = aws_launch_template.launch_template.latest_version
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 0
    }
  }

  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupPendingInstances",
    "GroupStandbyInstances",
    "GroupTerminatingInstances",
    "GroupTotalInstances"
  ]

  tag {
    key                 = "Name"
    value               = "search-cluster-instance"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    propagate_at_launch = true
    value               = ""
  }
}

locals {
  open_ports = [9200]
}

resource "aws_security_group" "search_instance_sg" {
  name   = "search-instance-sg"
  vpc_id = aws_vpc.digitalorganising_cac_vpc.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  dynamic "ingress" {
    for_each = local.open_ports

    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "ingress" {
    for_each = local.open_ports

    content {
      from_port        = ingress.value
      to_port          = ingress.value
      protocol         = "tcp"
      ipv6_cidr_blocks = ["::/0"]
    }
  }
}

resource "aws_launch_template" "launch_template" {
  name                   = "search-cluster-launch-template"
  instance_type          = local.instance_type
  image_id               = data.aws_ami.ecs_optimized.id
  user_data              = base64encode(local.user_data)
  update_default_version = true

  ebs_optimized = true


  network_interfaces {
    ipv6_address_count          = 1
    ipv4_address_count          = 1
    security_groups             = [aws_security_group.search_instance_sg.id]
    delete_on_termination       = true
    associate_public_ip_address = true
  }

  iam_instance_profile {
    arn = aws_iam_instance_profile.search.arn
  }
}

data "aws_ami" "ecs_optimized" {
  owners      = ["amazon"]
  most_recent = true

  filter {
    name   = "name"
    values = [local.instance_ami_family]
  }
}

locals {
  user_data = templatefile(
    "${path.module}/templates/user_data.tpl",
    {
      cluster_name = aws_ecs_cluster.search.name
    }
  )
}
