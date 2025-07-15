# 🚀 Deployment Guide

## 📋 **OVERVIEW**

This guide provides instructions for deploying the XOFlowers AI Agent to production environments, including local development, staging, and production deployments.

## 🏠 **LOCAL DEVELOPMENT**

### **Prerequisites**
- Python 3.8+
- Git
- Virtual environment tool (venv/conda)

### **Setup Steps**

#### **1. Clone Repository**
```bash
git clone https://github.com/Lucian-Adrian/flower-chat-agent.git
cd xoflowers-agent
```

#### **2. Create Virtual Environment**
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Using conda
conda create -n xoflowers python=3.9
conda activate xoflowers
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

#### **5. Initialize Database**
```bash
# Populate ChromaDB with products
python -m src.pipeline.populate_db
```

#### **6. Run Application**
```bash
# Instagram only
python main.py --platform instagram --debug

# Telegram only
python main.py --platform telegram --debug

# Both platforms
python main.py --platform both --debug
```

## 🌐 **PRODUCTION DEPLOYMENT**

### **Option 1: Docker Deployment**

#### **1. Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 xoflowers && chown -R xoflowers:xoflowers /app
USER xoflowers

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "main.py", "--platform", "both"]
```

#### **2. Create docker-compose.yml**
```yaml
version: '3.8'

services:
  xoflowers-agent:
    build: .
    ports:
      - "5001:5001"
    env_file:
      - .env
    volumes:
      - ./chroma_db_flowers:/app/chroma_db_flowers
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - xoflowers-agent
    restart: unless-stopped
```

#### **3. Deploy with Docker**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f xoflowers-agent

# Stop services
docker-compose down
```

### **Option 2: Cloud Deployment (AWS/GCP/Azure)**

#### **AWS Deployment with ECS**

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name xoflowers-cluster
```

2. **Push Docker Image to ECR**
```bash
# Create ECR repository
aws ecr create-repository --repository-name xoflowers-agent

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t xoflowers-agent .
docker tag xoflowers-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/xoflowers-agent:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/xoflowers-agent:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "xoflowers-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account-id:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "xoflowers-agent",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/xoflowers-agent:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:xoflowers-secrets"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/xoflowers-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### **GCP Deployment with Cloud Run**

1. **Build and Push to Container Registry**
```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/your-project-id/xoflowers-agent .
docker push gcr.io/your-project-id/xoflowers-agent
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy xoflowers-agent \
  --image gcr.io/your-project-id/xoflowers-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="FLASK_ENV=production" \
  --memory=1Gi \
  --cpu=1
```

### **Option 3: VPS Deployment (Ubuntu/CentOS)**

#### **1. Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash xoflowers
sudo usermod -aG sudo xoflowers
```

#### **2. Application Setup**
```bash
# Switch to application user
sudo -u xoflowers -i

# Clone repository
git clone https://github.com/Lucian-Adrian/flower-chat-agent.git
cd xoflowers-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Initialize database
python -m src.pipeline.populate_db
```

#### **3. Process Management with Systemd**
```bash
# Create systemd service
sudo nano /etc/systemd/system/xoflowers-agent.service
```

```ini
[Unit]
Description=XOFlowers AI Agent
After=network.target

[Service]
Type=simple
User=xoflowers
WorkingDirectory=/home/xoflowers/xoflowers-agent
Environment=PATH=/home/xoflowers/xoflowers-agent/venv/bin
ExecStart=/home/xoflowers/xoflowers-agent/venv/bin/python main.py --platform both
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable xoflowers-agent
sudo systemctl start xoflowers-agent

# Check status
sudo systemctl status xoflowers-agent
```

#### **4. Nginx Configuration**
```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/xoflowers-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Instagram webhook
    location /webhook {
        proxy_pass http://127.0.0.1:5001/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/xoflowers-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configure SSL
sudo certbot --nginx -d your-domain.com
```

## 🔐 **SECURITY CONSIDERATIONS**

### **1. Environment Variables**
```bash
# Use secrets management
# AWS Secrets Manager
# GCP Secret Manager
# Azure Key Vault
# HashiCorp Vault
```

### **2. Network Security**
```bash
# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Disable unnecessary services
sudo systemctl disable apache2
sudo systemctl disable mysql
```

### **3. SSL/TLS Configuration**
```bash
# Strong SSL configuration in nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
```

## 📊 **MONITORING & LOGGING**

### **1. Application Monitoring**
```python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('logs/xoflowers.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
```

### **2. System Monitoring**
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor processes
htop
ps aux | grep xoflowers

# Monitor logs
tail -f /var/log/syslog
journalctl -u xoflowers-agent -f
```

### **3. Health Checks**
```python
# Add health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

## 🔄 **CONTINUOUS DEPLOYMENT**

### **GitHub Actions Workflow**
```yaml
name: Deploy XOFlowers Agent

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Deploy to production
      run: |
        # Your deployment script here
        ssh user@your-server 'cd /home/xoflowers/xoflowers-agent && git pull && sudo systemctl restart xoflowers-agent'
```

## 🛠️ **TROUBLESHOOTING**

### **Common Issues**

1. **Port Already in Use**
```bash
sudo lsof -i :5001
sudo kill -9 <PID>
```

2. **Permission Denied**
```bash
sudo chown -R xoflowers:xoflowers /home/xoflowers/xoflowers-agent
```

3. **SSL Certificate Issues**
```bash
sudo certbot renew
sudo systemctl reload nginx
```

4. **Database Connection Issues**
```bash
# Check ChromaDB permissions
ls -la chroma_db_flowers/
sudo chown -R xoflowers:xoflowers chroma_db_flowers/
```

## 📋 **MAINTENANCE CHECKLIST**

### **Daily**
- [ ] Check application logs
- [ ] Monitor system resources
- [ ] Verify API endpoints

### **Weekly**
- [ ] Update dependencies
- [ ] Review security alerts
- [ ] Backup database

### **Monthly**
- [ ] SSL certificate renewal
- [ ] Performance optimization
- [ ] Security audit

---

**Last Updated:** January 2025  
**Version:** 1.0.0
