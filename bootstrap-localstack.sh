#!/usr/bin/env bash

export AWS_DEFAULT_REGION=eu-west-1
export AWS_ENDPOINT_URL=http://localstack:4566

awslocal sqs create-queue \
   --queue-name test-queue.fifo \
   --attributes FifoQueue=true,ContentBasedDeduplication=true