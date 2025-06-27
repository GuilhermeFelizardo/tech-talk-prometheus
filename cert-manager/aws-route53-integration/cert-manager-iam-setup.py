import boto3
import json
import subprocess

cluster_name = 'production-cluster'

namespace = "cert-manager"
service_account_name = "cert-manager"
role_name = "cert-manager-r53"


policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "route53:GetChange",
            "Resource": "arn:aws:route53:::change/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "route53:ChangeResourceRecordSets",
                "route53:ListResourceRecordSets"
            ],
            "Resource": "arn:aws:route53:::hostedzone/*"
        },
        {
            "Effect": "Allow",
            "Action": "route53:ListHostedZonesByName",
            "Resource": "*"
        }
    ]
}

def get_oidc_endpoint(cluster_name):
    eks_client = boto3.client('eks')
    try:
        cluster_info = eks_client.describe_cluster(name=cluster_name)
        oidc_issuer = cluster_info['cluster']['identity']['oidc']['issuer']
        oidc_issuer = oidc_issuer.replace("https://", "")
        return oidc_issuer
    except Exception as e:
        print(f"Error fetching OIDC endpoint: {e}")
        return None

def get_oidc_provider_arn(cluster_name):
    eks_client = boto3.client('eks')
    try:
        cluster_info = eks_client.describe_cluster(name=cluster_name)
        oidc_issuer = cluster_info['cluster']['identity']['oidc']['issuer']
        account_id = get_account_id()
        oidc_provider_arn = f"arn:aws:iam::{account_id}:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/{oidc_issuer.split('/')[-1]}"
        return oidc_provider_arn
    except Exception as e:
        print(f"Error fetching OIDC provider ARN: {e}")
        return None

def create_iam_policy_and_role(role_name, policy_document, cluster_name, namespace, service_account_name):
    iam_client = boto3.client('iam')
    policy_name = f"{role_name}-policy"

    # Attempt to create the policy
    try:
        iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Policy '{policy_name}' created successfully.")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Policy '{policy_name}' already exists.")

    # Get the OIDC Provider ARN
    oidc_provider_arn = get_oidc_provider_arn(cluster_name)
    oidc_provider = get_oidc_endpoint(cluster_name)
    if not oidc_provider_arn:
        return

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Principal": {
                    "Federated": oidc_provider_arn
                },
                "Condition": {
                    "StringEquals": {
                        f"{oidc_provider}:sub": f"system:serviceaccount:{namespace}:{service_account_name}"
                    }
                }
            }
        ]
    }

    try:
        iam_client.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists. Deleting and recreating.")
        delete_iam_role(role_name)
    except iam_client.exceptions.NoSuchEntityException:
        pass

    # Attempt to create the role
    try:
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for EKS OIDC integration"
        )
        print(f"Role '{role_name}' created successfully.")

    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role '{role_name}' already exists.")

    policy_arn = f"arn:aws:iam::{get_account_id()}:policy/{policy_name}"
        
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    print(f"Policy '{policy_name}' attached to role '{role_name}'.")

def get_account_id():
    sts_client = boto3.client('sts')
    return sts_client.get_caller_identity()["Account"]

def delete_iam_role(role_name):
    iam_client = boto3.client('iam')
    try:
        policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        for policy in policies:
            iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])

        iam_client.delete_role(RoleName=role_name)
        print(f"Role '{role_name}' deleted successfully.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Role '{role_name}' does not exist and cannot be deleted.")
    except Exception as e:
        print(f"Error deleting the role: {e}")

if __name__ == "__main__":
    role_name = "cert-manager-r53"


    aws_account_id = get_account_id()

    iam_role =  f'arn:aws:iam::{aws_account_id}:role/{role_name}'

    create_iam_policy_and_role(role_name, policy_document, cluster_name, namespace, service_account_name)
