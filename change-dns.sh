#!/bin/bash

# Get the Load Balancer address from NGINX Ingress Controller
load_balancer_address=$(kubectl get svc -n nginx-ingress -o yaml | awk '/hostname/{print $3}')

# Check if the address is retrieved
if [ -z "$load_balancer_address" ]; then
    echo "Load Balancer address not found."
    exit 1
fi

# Execute the AWS CLI command with the Load Balancer address
aws --no-cli-pager route53 change-resource-record-sets --hosted-zone-id Z06942553H9NBQ4TIUM5T --change-batch "{
  \"Changes\": [{
    \"Action\": \"UPSERT\",
    \"ResourceRecordSet\": {
      \"Name\": \"*.guilhermefreis.com\",
      \"Type\": \"CNAME\",
      \"TTL\": 300,
      \"ResourceRecords\": [{ \"Value\": \"$load_balancer_address\" }]
    }
  }]
}"