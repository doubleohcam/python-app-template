# Logging with Loki and Grafana

This setup provides centralized logging with full-text search for your Django application.

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Django    │──HTTP──▶│    Loki     │◀─query──│   Grafana   │
│   (logs)    │         │  (storage)  │         │    (UI)     │
└─────────────┘         └─────────────┘         └─────────────┘
                              │                       │
                              ▼                       ▼
                        loki-data/              localhost:3000
                        (persisted)
```

- **Loki**: Receives and stores logs. Think of it as a database optimized for logs.
- **Grafana**: Web UI for searching, filtering, and visualizing logs.
- **Django**: Sends logs to Loki via HTTP using a logging handler.

## Quick Start

### 1. Start the logging stack

```bash
cd docker-setup
./dev.sh up logging
```

Or manually:
```bash
docker compose --profile logging up -d
```

### 2. Access Grafana

Open http://localhost:3000

- **Username**: `admin`
- **Password**: `admin` (change in `.env` with `GRAFANA_PASSWORD`)

### 3. Install the Python package

```bash
poetry add python-logging-loki
```

### 4. Configure Django

Copy the configuration from `logging/django_logging_config.py` to your Django settings:

```python
# settings.py or settings/base.py

LOKI_URL = os.environ.get("LOKI_URL", "http://localhost:3100/loki/api/v1/push")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "loki": {
            "class": "logging_loki.LokiHandler",
            "url": LOKI_URL,
            "tags": {"app": "django"},
            "version": "1",
        },
    },
    "root": {
        "handlers": ["console", "loki"],
        "level": "INFO",
    },
}
```

### 5. Add to your .env

```bash
# For local development (Django running on host)
LOKI_URL=http://localhost:3100/loki/api/v1/push

# For Docker (Django running in container)
LOKI_URL=http://loki:3100/loki/api/v1/push

# Optional: Grafana credentials
GRAFANA_USER=admin
GRAFANA_PASSWORD=your-secure-password
```

## Using the Logger in Django

### Basic Usage

```python
import logging

logger = logging.getLogger("app")

# Simple messages
logger.debug("Debug details here")
logger.info("Something happened")
logger.warning("This might be a problem")
logger.error("Something went wrong")
logger.critical("System is down!")

# With context (extra fields become searchable in Grafana)
logger.info("User action", extra={
    "user_id": 123,
    "action": "login",
    "ip_address": "192.168.1.1",
})
```

### In Views

```python
import logging
from django.http import JsonResponse

logger = logging.getLogger("app")

def create_order(request):
    user = request.user
    
    logger.info("Order creation started", extra={
        "user_id": user.id,
        "path": request.path,
    })
    
    try:
        order = Order.objects.create(user=user, ...)
        logger.info("Order created successfully", extra={
            "user_id": user.id,
            "order_id": order.id,
            "total": float(order.total),
        })
        return JsonResponse({"order_id": order.id})
    
    except Exception as e:
        logger.error("Order creation failed", extra={
            "user_id": user.id,
            "error": str(e),
        })
        raise
```

### In Management Commands

```python
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger("app")

class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("Starting nightly job")
        
        processed = 0
        for item in Item.objects.filter(pending=True):
            item.process()
            processed += 1
        
        logger.info("Nightly job completed", extra={
            "processed_count": processed,
        })
```

### In Celery Tasks

```python
import logging
from celery import shared_task

logger = logging.getLogger("app")

@shared_task
def send_email_task(user_id, template):
    logger.info("Sending email", extra={
        "user_id": user_id,
        "template": template,
        "task": "send_email_task",
    })
    
    # ... send email logic
    
    logger.info("Email sent", extra={"user_id": user_id})
```

## Searching Logs in Grafana

### Opening the Log Explorer

1. Go to http://localhost:3000
2. Click the **Explore** icon (compass) in the left sidebar
3. Make sure **Loki** is selected as the data source

### Basic Queries

```logql
# All logs from your Django app
{app="django"}

# Only errors
{app="django"} |= "error"
{app="django"} | logfmt | level="error"

# Search for specific text
{app="django"} |= "user_id"
{app="django"} |= "payment failed"

# Regex search
{app="django"} |~ "timeout|connection refused"

# Exclude patterns
{app="django"} != "health_check"
```

### Filtering by Fields

If you log with `extra={}` fields:

```logql
# Filter by user_id
{app="django"} | json | user_id="123"

# Filter by multiple fields
{app="django"} | json | level="error" | user_id="123"

# Numeric comparisons
{app="django"} | json | response_time > 1000
```

### Time-based Queries

Use the time picker in the top-right of Grafana to select:
- Last 5 minutes
- Last 1 hour
- Last 24 hours
- Custom range

### Useful Query Examples

```logql
# Errors in the last hour
{app="django"} |= "ERROR"

# All requests from a specific user
{app="django"} | json | user_id="456"

# Slow requests (assuming you log response_time)
{app="django"} | json | response_time > 2000

# Failed payments
{app="django"} |= "payment" |= "failed"

# Count errors by level
sum by (level) (count_over_time({app="django"} | json [5m]))
```

## Creating Dashboards

### Quick Dashboard Setup

1. Click **Dashboards** in the left sidebar
2. Click **New** → **New Dashboard**
3. Click **Add visualization**
4. Select **Loki** as data source
5. Enter a query like `{app="django"} |= "error"`
6. Choose visualization type (Logs, Time series, etc.)

### Useful Dashboard Panels

**Error count over time:**
```logql
count_over_time({app="django"} |= "ERROR" [1m])
```

**Requests by endpoint:**
```logql
sum by (path) (count_over_time({app="django"} | json [5m]))
```

**Average response time:**
```logql
avg_over_time({app="django"} | json | unwrap response_time [5m])
```

## Setting Up Alerts

1. Go to **Alerting** → **Alert rules** in Grafana
2. Click **New alert rule**
3. Configure a query, e.g., error rate > 10/minute
4. Set notification channels (email, Slack, etc.)

Example alert query:
```logql
count_over_time({app="django"} |= "ERROR" [5m]) > 10
```

## Commands Reference

```bash
# Start logging stack
./dev.sh up logging

# Stop logging stack
docker compose --profile logging down

# View Loki logs
docker logs -f myproject-loki

# View Grafana logs
docker logs -f myproject-grafana

# Clear all log data (start fresh)
docker compose --profile logging down -v

# Check Loki health
curl http://localhost:3100/ready
```

## Troubleshooting

### Logs not appearing in Grafana

1. **Check Loki is running:**
   ```bash
   curl http://localhost:3100/ready
   # Should return "ready"
   ```

2. **Check Django can reach Loki:**
   ```python
   # In Django shell
   import requests
   requests.get("http://localhost:3100/ready")
   ```

3. **Verify LOKI_URL in your environment:**
   - Local Django: `http://localhost:3100/loki/api/v1/push`
   - Dockerized Django: `http://loki:3100/loki/api/v1/push`

4. **Check for errors in Django logs:**
   ```bash
   # Look for connection errors to Loki
   ```

### "No data" in Grafana

- Make sure the time range includes when logs were sent
- Try a broader query: `{app="django"}`
- Check the label name matches your Django config

### Loki using too much disk

Edit `logging/loki-config.yml`:
```yaml
limits_config:
  retention_period: 168h  # Reduce to 7 days
```

Then restart:
```bash
docker compose --profile logging restart loki
```

## File Reference

```
docker-setup/logging/
├── loki-config.yml           # Loki configuration
├── grafana-datasources.yml   # Auto-configures Loki in Grafana
├── django_logging_config.py  # Example Django settings
└── README.md                 # This file
```

## Resources

- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/query/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [python-logging-loki](https://github.com/GreyZmeem/python-logging-loki)
