# Deployment Guide: FinancialAssist Telegram Bot

**Created**: 2025-01-27  
**Purpose**: Production deployment procedures and best practices

---

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (version 12+)
- Redis server (version 6+)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- OpenAI API Key (or alternative AI service)
- Domain/Server with public IP (for webhook mode)

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Best for**: Single server deployments, development, staging

#### Steps

1. **Clone repository**:

   ```bash
   git clone <repository-url>
   cd financialassist
   ```

2. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Set environment variables**:

   ```bash

export TELEGRAM_BOT_TOKEN="your_production_token"  # pragma: allowlist secret
export OPENAI_API_KEY="your_openai_key"  # pragma: allowlist secret
export DATABASE_URL="postgresql://user:pass@db:5432/financialassist"  # pragma: allowlist secret
   export REDIS_URL="redis://redis:6379/0"
   export ENVIRONMENT="production"
   export LOG_LEVEL="INFO"

   ```

4. **Start services**:

   ```bash
   docker-compose up -d
   ```

1. **Run migrations**:

   ```bash
   docker-compose exec bot alembic upgrade head
   ```

2. **Seed categories**:

   ```bash
   docker-compose exec bot python scripts/seed_categories.py
   ```

3. **Verify deployment**:

   ```bash
   docker-compose logs -f bot
   ```

#### Docker Compose Configuration

The `docker-compose.yml` includes:

- **bot**: Main application container
- **postgres**: PostgreSQL database
- **redis**: Redis cache/session store

### Option 2: Kubernetes (Production Scale)

**Best for**: High availability, auto-scaling, multi-region

#### Steps

1. **Create namespace**:

   ```bash
   kubectl create namespace financialassist
   ```

2. **Create secrets**:

   ```bash
   kubectl create secret generic bot-secrets \
     --from-literal=telegram-bot-token="your_token" \
     --from-literal=openai-api-key="your_key" \
     --from-literal=database-url="postgresql://..." \
     -n financialassist
   ```

3. **Deploy PostgreSQL**:

   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/postgres-service.yaml
   ```

4. **Deploy Redis**:

   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/redis-service.yaml
   ```

5. **Deploy bot**:

   ```bash
   kubectl apply -f k8s/bot-deployment.yaml
   kubectl apply -f k8s/bot-service.yaml
   ```

6. **Configure ingress** (for webhook mode):

   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

### Option 3: Systemd Service (Traditional Linux)

**Best for**: Single server, system-level service

#### Steps

1. **Create systemd service file** (`/etc/systemd/system/financialassist.service`):

   ```ini
   [Unit]
   Description=FinancialAssist Telegram Bot
   After=network.target postgresql.service redis.service

   [Service]
   Type=simple
   User=botuser
   WorkingDirectory=/opt/financialassist
   Environment="PATH=/opt/financialassist/venv/bin"
   ExecStart=/opt/financialassist/venv/bin/python -m src.bot.main
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service**:

   ```bash
   sudo systemctl enable financialassist
   sudo systemctl start financialassist
   sudo systemctl status financialassist
   ```

---

## Webhook vs Polling

### Polling Mode (Default)

**Pros**: Simple setup, no public endpoint needed  
**Cons**: Higher latency, less efficient

**Configuration**: No additional setup required

### Webhook Mode (Production Recommended)

**Pros**: Lower latency, more efficient, better for scale  
**Cons**: Requires public HTTPS endpoint

#### Setup Webhook

1. **Configure webhook URL**:

   ```python
   from telegram import Update
   from telegram.ext import Application

   application = Application.builder().token(token).build()
   await application.bot.set_webhook(
       url="https://yourdomain.com/webhook",
       secret_token="your_webhook_secret"  # pragma: allowlist secret
   )
   ```

2. **Create webhook endpoint** (Flask/FastAPI example):

   ```python
   @app.post("/webhook")
   async def webhook(request: Request):
       update = Update.de_json(await request.json(), application.bot)
       await application.process_update(update)
       return {"ok": True}
   ```

3. **Verify webhook**:

   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```

---

## Environment Configuration

### Required Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN="your_bot_token"  # pragma: allowlist secret

# AI Service
OPENAI_API_KEY="your_openai_key"  # pragma: allowlist secret
AI_RESPONSE_TIMEOUT=3

# Database
DATABASE_URL="postgresql://user:pass@host:5432/dbname"  # pragma: allowlist secret

# Redis
REDIS_URL="redis://host:6379/0"
CACHE_TTL=300

# Application
ENVIRONMENT="production"
LOG_LEVEL="INFO"
BOT_RESPONSE_TIMEOUT=2
```

### Production Recommendations

- Use **strong passwords** for database
- Enable **SSL/TLS** for database connections
- Use **Redis password** authentication
- Set `ENVIRONMENT=production` for production logging
- Use `LOG_LEVEL=WARNING` or `ERROR` in production (reduce noise)

---

## Database Setup

### Initial Setup

1. **Create database**:

   ```sql
   CREATE DATABASE financialassist;
   CREATE USER botuser WITH PASSWORD 'secure_password';  # pragma: allowlist secret
   GRANT ALL PRIVILEGES ON DATABASE financialassist TO botuser;
   ```

2. **Run migrations**:

   ```bash
   alembic upgrade head
   ```

3. **Seed default categories**:

   ```bash
   python scripts/seed_categories.py
   ```

### Backup Strategy

See [operations.md](./operations.md) for backup and recovery procedures.

---

## Monitoring

### Health Checks

The bot includes a health check endpoint (if webhook mode):

```bash
curl https://yourdomain.com/health
```

Response:

```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "uptime": 3600
}
```

### Logging

Structured JSON logs are written to stdout:

```json
{
  "timestamp": "2025-01-27 10:00:00",
  "level": "INFO",
  "name": "src.bot.handlers.transaction",
  "message": "Transaction recorded successfully"
}
```

### Metrics to Monitor

- **Response time**: Should be < 2 seconds (95th percentile)
- **Error rate**: Should be < 1%
- **Database connection pool**: Monitor pool size and wait times
- **Redis memory usage**: Monitor cache hit rate
- **Rate limiting**: Track rate limit violations

---

## Security Checklist

- [ ] Environment variables stored securely (not in code)
- [ ] Database credentials rotated regularly
- [ ] API keys stored in secret management system
- [ ] HTTPS enabled for webhook endpoints
- [ ] Rate limiting enabled (30 messages/second)
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (using parameterized queries)
- [ ] Error messages don't leak sensitive information
- [ ] Logs don't contain sensitive data (PII, tokens)
- [ ] Regular security updates applied

---

## Scaling

### Horizontal Scaling

For high traffic, run multiple bot instances:

1. **Use webhook mode** (required for multiple instances)
2. **Shared Redis** for session state
3. **Load balancer** to distribute webhook requests
4. **Database connection pooling** (already configured)

### Vertical Scaling

- Increase database connection pool size
- Increase Redis memory allocation
- Add more CPU/memory to bot container

---

## Troubleshooting

### Bot Not Responding

1. Check logs: `docker-compose logs bot`
2. Verify bot token is correct
3. Check Telegram API status
4. Verify database connectivity

### Database Errors

1. Check database is running: `docker-compose ps postgres`
2. Verify connection string
3. Check database logs: `docker-compose logs postgres`
4. Run migrations: `alembic upgrade head`

### Redis Errors

1. Check Redis is running: `docker-compose ps redis`
2. Verify Redis URL
3. Check Redis memory: `redis-cli INFO memory`

### Performance Issues

1. Check database query performance
2. Monitor Redis cache hit rate
3. Review slow query logs
4. Check for N+1 query problems

---

## Rollback Procedure

1. **Stop current deployment**:

   ```bash
   docker-compose down
   # or
   kubectl scale deployment bot --replicas=0
   ```

2. **Revert to previous version**:

   ```bash
   git checkout <previous-tag>
   docker-compose up -d
   ```

3. **Verify rollback**:

   ```bash
   docker-compose logs -f bot
   ```

---

## Maintenance

### Regular Tasks

- **Weekly**: Review error logs
- **Monthly**: Database backup verification
- **Quarterly**: Security audit
- **As needed**: Dependency updates

### Updates

1. Pull latest code: `git pull`
2. Run tests: `pytest`
3. Run migrations: `alembic upgrade head`
4. Restart services: `docker-compose restart bot`

---

**Status**: ✅ Complete - Deployment guide with Docker, Kubernetes, and systemd options
