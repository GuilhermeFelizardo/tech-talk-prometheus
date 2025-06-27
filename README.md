# Prometheus Project - Kubernetes Monitoring

This project implements a complete monitoring solution using Prometheus and Grafana on an AWS EKS Kubernetes cluster, including a demo application with custom metrics.

## Overview

The project consists of:

- **Demo Application** (`app-1/`): Flask application with custom Prometheus metrics
- **EKS Cluster** (`eksctl/`): Kubernetes cluster configuration on AWS
- **Monitoring** (`kube-prometheus/`): Complete Prometheus + Grafana + AlertManager stack
- **SSL Certificates** (`cert-manager/`): Certificate automation with Let's Encrypt and Route53
- **Ingress** (`nginx-igress-controller/`): Ingress controller for service exposure
- **Reflector** (`reflector/`): Secret synchronization between namespaces

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │    │   Prometheus     │    │    Grafana      │
│   (Flask)       │───▶│   (Metrics)      │───▶│   (Dashboard)   │
│   Port: 5000    │    │   Port: 9090     │    │   Port: 3000    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  AlertManager   │
                    │    (Alerts)     │
                    │  Port: 9093     │
                    └─────────────────┘
```

## Quick Start

### ⚠️ Important Configurations

**BEFORE executing any command, you MUST review and customize the following files with your AWS account configurations:**

1. **VPC and Subnets** in `eksctl/production-cluster.yaml`:
   - Replace VPC ID: `vpc-0d73d2f5e07f9352c`
   - Replace Subnet IDs for zones us-east-1a, us-east-1b, us-east-1c
   - Adjust Account ID in policy ARNs: `022887457179`

2. **DNS Domain** in files:
   - `kube-prometheus/custom-values.yaml`: replace `guilhermefreis.com` with your domain
   - `cert-manager/custom-values.yaml`: adjust role ARN for your Account ID

3. **Route53 DNS Zone**:
   - `cert-manager/resources/cluster-issuer-route53.yaml`: replace with your Hosted Zone ID
   - `change-dns.sh`: replace Hosted Zone ID and domain

4. **AWS Account ID**:
   - `cert-manager/custom-values.yaml`: role ARN with correct Account ID
   - `eksctl/production-cluster.yaml`: policy ARNs with correct Account ID

5. **Docker Registry**:
   - `app-1/k8s/kubernetes.yaml`: replace image reference with your registry
   - Build and push the Docker image to your registry before deployment

### Prerequisites

- AWS CLI configured
- kubectl installed
- eksctl installed
- Helm 3 installed
- Domain configured in Route53

### 1. Create EKS Cluster

```bash
cd eksctl/
eksctl create cluster -f production-cluster.yaml
```

### 2. Configure Storage Class

```bash
kubectl apply -f eksctl/gp3-storage-class.yaml
```

### 3. Install Cert-Manager

```bash
cd cert-manager/
python install-cert-manager.py
```

### 4. Configure Route53 (if needed)

```bash
cd cert-manager/aws-route53-integration/
python cert-manager-iam-setup.py
```

### 5. Install NGINX Ingress Controller

```bash
cd nginx-igress-controller/
python install-nginx-ingress-controller.py
```

### 6. Install Reflector

```bash
cd reflector/
python install-reflector.py
```

### 7. Install Kube-Prometheus Stack

```bash
cd kube-prometheus/
python install-kube-prometheus.py
```

### 8. Build and Deploy Demo Application

#### Build and Push Docker Image

```bash
cd app-1/app/
# Build the Docker image
docker build -t YOUR_REGISTRY/app-1:latest .

# Push to your registry (Docker Hub, ECR, etc.)
docker push YOUR_REGISTRY/app-1:latest
```

#### Update Kubernetes Manifest

Edit `app-1/k8s/kubernetes.yaml` and replace the image reference:

```yaml
spec:
  containers:
  - name: app-1
    image: YOUR_REGISTRY/app-1:latest  # Replace with your registry
```

#### Deploy Application

```bash
cd app-1/k8s/
kubectl apply -f kubernetes.yaml
```

### 9. Configure DNS (final)

```bash
./change-dns.sh
```

## Demo Application

The Flask application (`app-1/app/app.py`) exposes several custom metrics:

### Available Endpoints

- `/` - Home page
- `/dashboard` - Application dashboard
- `/api/metrics-demo` - API that generates demo metrics
- `/simulate-load` - Simulates different types of load
- `/health` - Health check
- `/metrics` - Prometheus metrics endpoint

### Custom Metrics

```python
REQUEST_COUNT = Counter('darede_requests_total', 'Total requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('darede_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('darede_active_users', 'Active users at the moment')
MEMORY_USAGE = Gauge('darede_memory_usage_bytes', 'Application memory usage')
BUSINESS_METRICS = Counter('darede_business_events_total', 'Business events', ['event_type'])
```

### Run Locally

```bash
cd app-1/app/
pip install -r requirements.txt
python app.py
```

The application will be available at `http://localhost:5000`

## Monitoring

### Access Dashboards

After complete installation, dashboards will be available at:

- **Grafana**: https://grafana.guilhermefreis.com
  - User: `admin`
  - Password: `poc-grafana`
- **Prometheus**: https://prometheus.guilhermefreis.com
- **AlertManager**: https://alertmanager.guilhermefreis.com

### Custom Dashboards

The project includes custom dashboards in `kube-prometheus/grafana-dashboards/`:

- `app-1-dashboard.yaml` - Specific dashboard for the demo application

### Alert Rules

Custom alert rules in `kube-prometheus/prometheus-rules/`:

- `high-memory-usage-rules.yaml` - Memory usage alerts
- `pods-evicted-rules.yaml` - Pod eviction alerts
- `pods-restart-rules.yaml` - Pod restart alerts

## Load Testing

### K6 Load Testing

```bash
cd app-1/k6/
# Install K6 if needed
brew install k6  # macOS
# or
sudo apt install k6  # Ubuntu

# Run test
k6 run script.js
```

### Simulate Different Loads

```bash
# Normal load
curl http://your-app-url/simulate-load

# High load
curl http://your-app-url/simulate-load?type=high

# Simulate errors
curl http://your-app-url/simulate-load?type=error
```

## Configuration

### Required Configurations

**Before running any installation, customize the following files:**

#### 1. EKS Cluster Configuration (`eksctl/production-cluster.yaml`)

```yaml
vpc:
  id: "vpc-YOUR_VPC_ID_HERE"  # Replace with your VPC ID
  subnets:
    public:
        us-east-1a:
          id: "subnet-YOUR_SUBNET_ID_1A"  # Replace with your Subnet IDs
        us-east-1b:
          id: "subnet-YOUR_SUBNET_ID_1B"
        us-east-1c:
          id: "subnet-YOUR_SUBNET_ID_1C"
```

#### 2. DNS Configuration (`kube-prometheus/custom-values.yaml`)

```yaml
# Replace guilhermefreis.com with your domain
hosts:
  - prometheus.YOUR_DOMAIN.com
  - grafana.YOUR_DOMAIN.com
```

#### 3. Cert-Manager Configuration (`cert-manager/custom-values.yaml`)

```yaml
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::YOUR_ACCOUNT_ID:role/cert-manager-r53"
```

#### 4. DNS Zone Configuration (`cert-manager/resources/cluster-issuer-route53.yaml`)

```yaml
# Replace with your Route53 DNS zone
spec:
  acme:
    solvers:
    - dns01:
        route53:
          region: us-east-1
          hostedZoneID: YOUR_HOSTED_ZONE_ID  # Your Route53 zone ID
```

#### 5. DNS Script Configuration (`change-dns.sh`)

```bash
# Replace with your Hosted Zone ID and domain
aws --no-cli-pager route53 change-resource-record-sets --hosted-zone-id YOUR_HOSTED_ZONE_ID --change-batch "{
  \"Changes\": [{
    \"Action\": \"UPSERT\",
    \"ResourceRecordSet\": {
      \"Name\": \"*.YOUR_DOMAIN.com\",  # Replace with your domain
      \"Type\": \"CNAME\",
      \"TTL\": 300,
      \"ResourceRecords\": [{ \"Value\": \"$load_balancer_address\" }]
    }
  }]
}"
```

#### 6. Docker Registry Configuration (`app-1/k8s/kubernetes.yaml`)

```yaml
# Replace with your Docker registry
spec:
  containers:
  - name: app-1
    image: YOUR_REGISTRY/app-1:latest  # Examples:
    # Docker Hub: yourusername/app-1:latest
    # ECR: 123456789012.dkr.ecr.us-east-1.amazonaws.com/app-1:latest
    # GHCR: ghcr.io/yourusername/app-1:latest
```

### Customize Values

Edit the `custom-values.yaml` files in each directory to adjust configurations:

- `cert-manager/custom-values.yaml` - Cert-manager configurations
- `kube-prometheus/custom-values.yaml` - Prometheus/Grafana configurations
- `nginx-igress-controller/custom-values.yaml` - NGINX configurations

### Environment Variables

The following variables can be configured:

```bash
export AWS_REGION=us-east-1
export CLUSTER_NAME=production-cluster
export DOMAIN=YOUR_DOMAIN.com  # Replace with your domain
export AWS_ACCOUNT_ID=YOUR_ACCOUNT_ID  # Replace with your Account ID
export DOCKER_REGISTRY=YOUR_REGISTRY  # Replace with your Docker registry
```

## Project Structure

```
prometheus/
├── app-1/                          # Flask demo application
│   ├── app/                        # Application code
│   ├── k6/                         # Load testing scripts
│   └── k8s/                        # Kubernetes manifests
├── cert-manager/                   # SSL certificate configuration
├── eksctl/                         # EKS cluster configuration
├── kube-prometheus/                # Monitoring stack
├── nginx-igress-controller/        # Ingress controller
├── reflector/                      # Secret synchronization
└── change-dns.sh                   # DNS helper script
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -A
```

### Component Logs

```bash
# Prometheus logs
kubectl logs -n monitoring prometheus-kube-prometheus-prometheus-0

# Grafana logs
kubectl logs -n monitoring kube-prometheus-grafana-xxx

# Application logs
kubectl logs -n default app-1-xxx
```

### Check Certificates

```bash
kubectl get certificates -A
kubectl describe certificate certificate-tls -n monitoring
```
