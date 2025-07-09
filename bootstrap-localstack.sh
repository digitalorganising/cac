#!/usr/bin/env bash

AWS_DEFAULT_REGION=eu-west-1 uvx --from awscli-local \
  awslocal sqs create-queue \
   --queue-name test-queue.fifo \
   --attributes FifoQueue=true,ContentBasedDeduplication=true