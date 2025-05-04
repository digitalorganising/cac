resource "aws_ecs_service" "search" {
  name            = "search-service"
  cluster         = aws_ecs_cluster.search.id
  task_definition = "${aws_ecs_task_definition.search.family}:${aws_ecs_task_definition.search.revision}"
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.search.name
    weight            = 1
  }
}

resource "aws_secretsmanager_secret" "opensearch_admin_password" {
  name = "opensearch-admin-password"
}

resource "aws_cloudwatch_log_group" "opensearch" {
  name = "awslogs-opensearch"
}

resource "aws_ecs_task_definition" "search" {
  family             = "search-task-definition"
  network_mode       = "host"
  execution_role_arn = aws_iam_role.search_service_execution_role.arn

  container_definitions = jsonencode([
    {
      name              = "opensearch"
      image             = "${aws_ecrpublic_repository.opensearch.repository_uri}:latest",
      essential         = true,
      memoryReservation = 768,
      mountPoints = [
        {
          sourceVolume  = "opensearch-data"
          containerPath = "/usr/share/opensearch/data"
        }
      ],
      portMappings = [
        {
          containerPort = 9200,
          hostPort      = 9200,
          protocol      = "tcp"
        }
      ],
      ulimits = [
        {
          name      = "nofile"
          hardLimit = 65536
          softLimit = 65536
        },
        {
          name      = "memlock"
          hardLimit = -1
          softLimit = -1
        }
      ],
      environment = [
        {
          name  = "discovery.type"
          value = "single-node"
        },
        {
          name  = "bootstrap.memory_lock"
          value = "true"
        },
        {
          name  = "http.compression"
          value = "true"
        },
        {
          name  = "OPENSEARCH_JAVA_OPTS"
          value = "-Xms512m -Xmx512m"
        }
      ],
      secrets = [
        {
          name      = "OPENSEARCH_INITIAL_ADMIN_PASSWORD"
          valueFrom = aws_secretsmanager_secret.opensearch_admin_password.arn
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.opensearch.name
          awslogs-region        = "eu-west-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  volume {
    configure_at_launch = false
    name                = "opensearch-data"
  }
}
