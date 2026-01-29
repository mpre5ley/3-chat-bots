# 3Chatbots — An interface to test multiple LLMs
The web application allows users to input a single prompt and receive a single response 
from multiple language models via Hugging Face APIs.

## Features:
- Run a single prompt through multiple LLMs
- Select 1-3 models to get simultaneous responses
- Django frontend with a clean UI
- Django backend with a RESTful API
- Docker Compose used to orchestrate multiple containers

## Full Deployment Guide (EC2 + Docker Compose)

This document contains steps to deploy the 3Chatbots application on an AWS EC2 instance, 
using AWS CLI, SSH, and Docker Compose.

---
## Application Overview

The application runs entirely on a single Ubuntu EC2 instance using Docker Compose.

**Docker Containers:**
- proxy — nginx reverse proxy (ports 80 / 443)
- frontend — Django frontend (auth + UI)
- backend — Django REST API

---
## Prerequisites (Local Machine)

- AWS CLI v2 installed and configured
- SSH client
- `scp`
- Terminal access

**Verify AWS access:**

```bash
aws sts get-caller-identity
```

**Set region (example: Frankfurt):**

```bash
export AWS_REGION=eu-central-1
```

**Set your IP**
```bash
export MY_IP=$(curl -s https://checkip.amazonaws.com)
```

---
## 1. Create SSH Key Pair

```bash
aws ec2 create-key-pair \
  --region "$AWS_REGION" \
  --key-name chatbots-sys-key \
  --query "KeyMaterial" \
  --output text > chatbots-sys-key.pem

chmod 400 chatbots-sys-key.pem
```

---
## 2. Create Security Group

### 2.1 Get Default VPC

```bash
VPC_ID=$(aws ec2 describe-vpcs --region "$AWS_REGION" \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" --output text)
```

### 2.2 Create Security Group

```bash
SG_ID=$(aws ec2 create-security-group --region "$AWS_REGION" \
  --group-name chatbots-sg \
  --description "3chatbots security group" \
  --vpc-id "$VPC_ID" \
  --query "GroupId" --output text)
```

### 2.3 Allow HTTP and HTTPS

```bash
aws ec2 authorize-security-group-ingress --region "$AWS_REGION" \
  --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --region "$AWS_REGION" \
  --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0
```

### 2.4 Allow SSH from Your IP Only

```bash
aws ec2 authorize-security-group-ingress --region "$AWS_REGION" \
  --group-id "$SG_ID" --protocol tcp --port 22 --cidr "${MY_IP}/32"
```

---
## 3. Launch an Ubuntu EC2 Instance

### 3.1 Find Latest Ubuntu 22.04 AMI

```bash
AMI_ID=$(aws ec2 describe-images --region "$AWS_REGION" \
  --owners 099720109477 \
  --filters \
    "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    "Name=state,Values=available" \
  --query "sort_by(Images, &CreationDate)[-1].ImageId" \
  --output text)
```

### 3.2 Choose Subnet

```bash
SUBNET_ID=$(aws ec2 describe-subnets --region "$AWS_REGION" \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query "Subnets[0].SubnetId" --output text)
```

### 3.3 Launch Instance

```bash
INSTANCE_ID=$(aws ec2 run-instances --region "$AWS_REGION" \
  --image-id "$AMI_ID" \
  --instance-type t3.small \
  --key-name 3chatbots-sys-key \
  --security-group-ids "$SG_ID" \
  --subnet-id "$SUBNET_ID" \
  --associate-public-ip-address \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=3chatbots-host}]" \
  --query "Instances[0].InstanceId" --output text)
```

**Wait until running:**

```bash
aws ec2 wait instance-running --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
```

**Get public IP:**

```bash
PUBLIC_IP=$(aws ec2 describe-instances --region "$AWS_REGION" \
  --instance-ids "$INSTANCE_ID" \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
```

---
## 4. Attach an Elastic IP

```bash
ALLOC_ID=$(aws ec2 allocate-address --region "$AWS_REGION" \
  --domain vpc --query "AllocationId" --output text)

aws ec2 associate-address --region "$AWS_REGION" \
  --instance-id "$INSTANCE_ID" \
  --allocation-id "$ALLOC_ID"
```

---
## 5. SSH Into the Server

```bash
ssh -i 3chatbots-sys-key.pem ubuntu@"$PUBLIC_IP"
```

---
## 6. Install Docker and Docker Compose (On EC2)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg unzip

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo usermod -aG docker ubuntu
newgrp docker
```

---
## 7. Upload Project Zip

**From local machine:**

```bash
scp -i 3chatbots-sys-key.pem ./3-chat-bots.zip ubuntu@"$PUBLIC_IP":/home/ubuntu/
```

**On EC2:**

```bash
cd ~
unzip -o 3-chat-bots.zip
cd 3-chat-bots
```

---
## 8. Create Root `.env` File

```env
DEBUG=false
SECRET_KEY=REPLACE_WITH_RANDOM_SECRET
ALLOWED_HOSTS=localhost,127.0.0.1,backend,frontend
BACKEND_API_URL=http://backend:8001/api
HUGGING_FACE_API_TOKEN=REPLACE_ME
```
---
## 9. Build and Start Containers

```bash
docker compose up -d --build
```

**Verify containers are running:**

```bash
docker compose ps
```

---
## 10. Initialize Database and Admin User

```bash
docker compose exec frontend python manage.py migrate
docker compose exec frontend python manage.py createsuperuser
```

---
## 11. Verify Deployment

**On EC2:**

```bash
curl -I http://localhost/
curl -i http://localhost/api/health/
```

**From local machine:**

```bash
curl -I http://PUBLIC_IP/
curl -i http://PUBLIC_IP/api/health/
```

----------
## Tear Down Guide 

## 1. Set environment variables

```bash
export AWS_REGION=eu-central-1
```

## 2. Delete the Application Load Balancer listeners and target groups

```bash
aws elbv2 describe-listeners --region $AWS_REGION \
  --load-balancer-arn arn:aws:elasticloadbalancing:eu-central-1:249760238290:loadbalancer/app/alb-3chatbots/ba45d1ea32c8a324 \
  --query "Listeners[].ListenerArn" --output text
```

**For each ALB listener listed**

```bash
aws elbv2 delete-listener --region $AWS_REGION --listener-arn <listener-arn>
```

**Get the target groups, copy the output to delete after the ALB**

```bash
aws elbv2 describe-target-groups --region $AWS_REGION \
  --load-balancer-arn arn:aws:elasticloadbalancing:eu-central-1:249760238290:loadbalancer/app/alb-3chatbots/ba45d1ea32c8a324 \
  --query "TargetGroups[].TargetGroupArn" --output text
```

**Delete the ALB**

```bash
aws elbv2 delete-load-balancer --region $AWS_REGION \
  --load-balancer-arn arn:aws:elasticloadbalancing:eu-central-1:249760238290:loadbalancer/app/alb-3chatbots/ba45d1ea32c8a324
```

**Delete the target groups (if available)**

```bash
aws ec2 delete-nat-gateway --region $AWS_REGION \
  --nat-gateway-id nat-0924d5f1fe403efc0
```

## 3. Delete Network Address Translation (NAT) Gateway

**Delete NAT gateway**

```bash
aws ec2 delete-nat-gateway --region $AWS_REGION \
  --nat-gateway-id nat-0924d5f1fe403efc0
```

**Confirm NAT run-state is "deleted"**

```bash
aws ec2 describe-nat-gateways --region $AWS_REGION \
  --nat-gateway-ids nat-0924d5f1fe403efc0 \
  --query "NatGateways[0].State" --output text
```

**Release the NAT EIP**

```bash
aws ec2 release-address --region $AWS_REGION \
  --allocation-id eipalloc-0fe6f5f051b110324
```

## 4. Delete RDS Postgres

```bash
aws rds delete-db-instance --region $AWS_REGION \
  --db-instance-identifier chatbots-db \
  --skip-final-snapshot \
  --delete-automated-backups
```

**If deletion is rejected due to deletion protection, disable it**

```bash 
aws rds modify-db-instance --region $AWS_REGION \
  --db-instance-identifier chatbots-db \
  --no-deletion-protection \
  --apply-immediately
```

**Delete any manual snapshots**

```bash
aws rds describe-db-snapshots --region $AWS_REGION \
  --query "DBSnapshots[?DBInstanceIdentifier=='chatbots-db'].[DBSnapshotIdentifier,SnapshotType,SnapshotCreateTime]" \
  --output table
```

**Manually delete each snapshot using the snapshot id**

```bash
aws rds delete-db-snapshot --region $AWS_REGION --db-snapshot-identifier <snapshot-id>
```

## 5. Terminate EC2

```bash
aws ec2 terminate-instances --region $AWS_REGION \
  --instance-ids i-0b59b6e1620a8a517
```


**Stop containers on EC2:**

```bash
docker compose down
```

**Stop EC2 instance on local machine:**

```bash
aws ec2 stop-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
```


