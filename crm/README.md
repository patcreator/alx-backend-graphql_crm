# CRM Application with Celery Task Scheduling

## Celery Setup for Weekly CRM Reports

This document outlines the setup process for Celery with Celery Beat to generate weekly CRM reports.

### Prerequisites

- Python 3.8+
- Redis Server
- Django 3.2+
- Virtual Environment (recommended)

### Installation Steps

#### 1. Install Redis

**On Ubuntu/Debian (WSL):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server