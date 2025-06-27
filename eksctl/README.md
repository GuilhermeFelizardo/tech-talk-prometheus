# EKS Cluster Configuration

This document provides a detailed explanation of the configuration file `production-cluster.yaml` for creating an Amazon Elastic Kubernetes Service (EKS) cluster using eksctl.

## Overview

The `production-cluster.yaml` file defines the configuration for an EKS cluster named "production-cluster" in the `us-east-1` region.


### Cluster Metadata

- **name**: The name of the EKS cluster.
- **region**: The AWS region where the cluster will be deployed.
- **version**: The version of Kubernetes to use for the cluster.
- **tags**: Additional metadata tags for the cluster.

### VPC Configuration

- **id**: The ID of the VPC where the cluster will be deployed. (Replace with your VPC ID)
- **securityGroup**: The ID of the security group associated with the cluster. (Replace with your security group ID)
- **subnets**: Subnet IDs for the public subnets in different availability zones. (Replace with your subnet IDs)

### IAM Configuration

- **withOIDC**: Indicates whether to create an IAM OIDC identity provider for the cluster.

### Add-ons

- List of add-ons to include in the cluster, such as VPC CNI, CoreDNS, kube-proxy, and AWS EBS CSI driver.

### Managed Node Groups

A managed node group is a group of Amazon EC2 instances that are managed by AWS and the Amazon EKS service. Unlike traditional self-managed node groups, managed node groups are fully managed by AWS, including provisioning, scaling, and updates.

- **name**: The name of the managed node group.
- **instanceTypes**: List of EC2 instance types to use for the nodes.
- **spot**: Indicates whether to use spot instances for the nodes.
- **minSize**: Minimum number of nodes.
- **maxSize**: Maximum number of nodes.
- **desiredCapacity**: Desired number of nodes.
- **volumeSize**: Size of the EBS volume attached to each node.
- **availabilityZones**: Availability zones for the nodes.
- **iam.attachPolicyARNs**: List of IAM policy ARNs to attach to the node IAM role.

## Pre-requisites

Before applying the `production-cluster.yaml` configuration file using eksctl, ensure that the `nodes-policy` IAM policy is created. Additionally, replace the VPC ID, security group ID, and subnet IDs with your own AWS resources.

## Usage

Apply the configuration using the following command:

```bash
eksctl create cluster -f production-cluster.yaml
```

Replace `production-cluster.yaml` with the path to your configuration file.

## Conclusion

By following this document and applying the provided configuration, you can easily create and configure an EKS cluster in your AWS environment.