#!/bin/bash
echo "ECS_CLUSTER=${cluster_name}" >> /etc/ecs/ecs.config

# https://docs.opensearch.org/docs/latest/install-and-configure/install-opensearch/docker/#linux-settings
# Disable swapping
sudo swapoff -a

# Increase mmap count
echo vm.max_map_count=262144 >> /etc/sysctl.conf
sysctl -w vm.max_map_count=262144