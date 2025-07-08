#!/usr/bin/env bash

export AWS_ENDPOINT_URL=http://localhost:4566

TFLOCAL=(uvx --from terraform-local tflocal)

"${TFLOCAL[@]}" init -reconfigure
"${TFLOCAL[@]}" apply -auto-approve -target=aws_sqs_queue.scraped_items