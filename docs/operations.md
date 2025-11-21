# Operations Guide: FinancialAssist Telegram Bot

**Created**: 2025-01-27  
**Purpose**: Database backup, recovery, and operational procedures

---

## Database Backup Procedures

### Automated Backups

#### PostgreSQL (Production)

**Daily Backup Script** (`scripts/backup_database.sh`):

```bash
#!/bin/bash
# Daily database backup script

BACKUP_DIR="/var/backups/financialassist"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="financialassist"
DB_USER="botuser"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Job Setup**:

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * /opt/financialassist/scripts/backup_database.sh >> /var/log/financialassist/backup.log 2>&1
```

#### SQLite (Development)

**Backup Script** (`scripts/backup_sqlite.sh`):

```bash
#!/bin/bash
# SQLite backup script

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="financialassist.db"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.db"

mkdir -p $BACKUP_DIR

# SQLite backup
sqlite3 $DB_FILE ".backup $BACKUP_FILE"

# Compress
gzip $BACKUP_FILE

echo "Backup completed: $BACKUP_FILE.gz"
```

### Manual Backup

#### PostgreSQL

```bash
# Full database backup
pg_dump -U botuser -h localhost financialassist > backup.sql

# Compressed backup
pg_dump -U botuser -h localhost financialassist | gzip > backup.sql.gz

# Backup specific tables only
pg_dump -U botuser -h localhost -t transactions financialassist > transactions_backup.sql
```

#### SQLite

```bash
# Copy database file
cp financialassist.db backups/financialassist_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 financialassist.db ".backup backups/backup.db"
```

---

## Database Recovery Procedures

### Full Database Restore

#### PostgreSQL

```bash
# Stop bot service
sudo systemctl stop financialassist

# Drop existing database (CAUTION: This deletes all data)
dropdb -U botuser financialassist

# Create new database
createdb -U botuser financialassist

# Restore from backup
gunzip -c backup.sql.gz | psql -U botuser -d financialassist

# Or from uncompressed backup
psql -U botuser -d financialassist < backup.sql

# Restart bot service
sudo systemctl start financialassist
```

#### SQLite

```bash
# Stop bot service
sudo systemctl stop financialassist

# Replace database file
cp backups/backup.db financialassist.db

# Restart bot service
sudo systemctl start financialassist
```

### Partial Recovery (Single Table)

#### PostgreSQL

```bash
# Restore only transactions table
psql -U botuser -d financialassist -c "DROP TABLE IF EXISTS transactions CASCADE;"
psql -U botuser -d financialassist < transactions_backup.sql
```

### Point-in-Time Recovery

#### PostgreSQL (with WAL archiving)

1. **Enable WAL archiving** in `postgresql.conf`:

   ```conf
   wal_level = replica
   archive_mode = on
   archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
   ```

2. **Restore to specific time**:

   ```bash
   # Restore base backup
   pg_basebackup -D /var/lib/postgresql/data -Ft -z -P

   # Recover to specific timestamp
   echo "recovery_target_time = '2025-01-27 10:00:00'" >> postgresql.conf
   touch /var/lib/postgresql/data/recovery.signal
   ```

---

## Redis Backup

### Backup Redis Data

```bash
# Create Redis backup
redis-cli --rdb /var/backups/redis/dump_$(date +%Y%m%d).rdb

# Or use BGSAVE (non-blocking)
redis-cli BGSAVE
# Wait for completion, then copy dump.rdb
cp /var/lib/redis/dump.rdb /var/backups/redis/dump_$(date +%Y%m%d).rdb
```

### Restore Redis Data

```bash
# Stop Redis
sudo systemctl stop redis

# Replace dump file
cp /var/backups/redis/dump_20250127.rdb /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis
```

---

## Disaster Recovery Plan

### Scenario 1: Database Corruption

**Symptoms**: Database errors, transaction failures

**Recovery Steps**:

1. **Stop bot service**:

   ```bash
   sudo systemctl stop financialassist
   ```

2. **Verify backup exists**:

   ```bash
   ls -lh /var/backups/financialassist/
   ```

3. **Restore from most recent backup**:

   ```bash
   # PostgreSQL
   pg_dump restore procedure (see above)

   # SQLite
   cp backups/latest.db financialassist.db
   ```

4. **Verify data integrity**:

   ```bash
   # Check transaction count
   psql -U botuser -d financialassist -c "SELECT COUNT(*) FROM transactions;"

   # Check user count
   psql -U botuser -d financialassist -c "SELECT COUNT(*) FROM users;"
   ```

5. **Restart bot service**:

   ```bash
   sudo systemctl start financialassist
   ```

6. **Monitor logs**:

   ```bash
   journalctl -u financialassist -f
   ```

### Scenario 2: Complete Server Failure

**Recovery Steps**:

1. **Provision new server** (same OS, PostgreSQL version)

2. **Restore database**:

   ```bash
   # Copy backup files
   scp backup.sql.gz new-server:/tmp/

   # Restore database
   gunzip -c /tmp/backup.sql.gz | psql -U botuser -d financialassist
   ```

3. **Restore Redis** (if using persistent storage):

   ```bash
   scp redis_dump.rdb new-server:/var/lib/redis/
   ```

4. **Deploy bot application**:

   ```bash
   git clone <repository>
   cd financialassist
   pip install -r requirements.txt
   alembic upgrade head
   ```

5. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit with production values
   ```

6. **Start services**:

   ```bash
   docker-compose up -d
   # or
   sudo systemctl start financialassist
   ```

### Scenario 3: Data Loss (Accidental Deletion)

**Recovery Steps**:

1. **Stop bot service** (prevent further writes)

2. **Identify last good backup**:

   ```bash
   ls -lt /var/backups/financialassist/
   ```

3. **Restore specific tables**:

   ```bash
   # Restore transactions table only
   psql -U botuser -d financialassist < transactions_backup.sql
   ```

4. **Verify restored data**:

   ```bash
   psql -U botuser -d financialassist -c "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;"
   ```

5. **Restart bot service**

---

## Backup Verification

### Automated Verification Script

```bash
#!/bin/bash
# Verify backup integrity

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Test restore to temporary database
TEST_DB="financialassist_test_$(date +%s)"
createdb -U botuser $TEST_DB

# Restore backup
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | psql -U botuser -d $TEST_DB
else
    psql -U botuser -d $TEST_DB < $BACKUP_FILE
fi

# Verify tables exist
TABLE_COUNT=$(psql -U botuser -d $TEST_DB -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLE_COUNT" -ge 3 ]; then
    echo "✓ Backup verification successful: $TABLE_COUNT tables found"
    # Cleanup
    dropdb -U botuser $TEST_DB
    exit 0
else
    echo "✗ Backup verification failed: Only $TABLE_COUNT tables found"
    dropdb -U botuser $TEST_DB
    exit 1
fi
```

### Manual Verification

```bash
# Check backup file size (should be > 0)
ls -lh backup.sql.gz

# Check backup contains expected tables
gunzip -c backup.sql.gz | grep -i "CREATE TABLE" | wc -l

# Verify backup date
stat -c %y backup.sql.gz
```

---

## Backup Retention Policy

### Recommended Retention

- **Daily backups**: Keep for 30 days
- **Weekly backups**: Keep for 12 weeks (3 months)
- **Monthly backups**: Keep for 12 months (1 year)
- **Yearly backups**: Keep indefinitely

### Cleanup Script

```bash
#!/bin/bash
# Cleanup old backups

BACKUP_DIR="/var/backups/financialassist"

# Remove backups older than 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

# Keep monthly backups (first backup of each month)
# This requires more sophisticated logic - see backup script above
```

---

## Monitoring Backups

### Health Check Script

```bash
#!/bin/bash
# Check backup health

BACKUP_DIR="/var/backups/financialassist"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/db_backup_*.sql.gz | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No backups found"
    exit 1
fi

BACKUP_AGE=$(($(date +%s) - $(stat -c %Y "$LATEST_BACKUP")))
MAX_AGE=86400  # 24 hours

if [ $BACKUP_AGE -gt $MAX_AGE ]; then
    echo "WARNING: Latest backup is older than 24 hours"
    exit 1
fi

echo "OK: Latest backup is recent"
exit 0
```

### Alerting

Set up monitoring to alert if:

- Backup fails
- Backup is older than 24 hours
- Backup file size is suspiciously small
- Backup verification fails

---

## Best Practices

1. **Test backups regularly**: Restore to test environment monthly
2. **Store backups off-site**: Use cloud storage (S3, GCS, Azure Blob)
3. **Encrypt backups**: Use GPG or similar for sensitive data
4. **Document recovery procedures**: Keep this guide updated
5. **Automate everything**: Use cron jobs and scripts
6. **Monitor backup success**: Set up alerts for failures
7. **Version control**: Tag backups with version numbers
8. **Regular drills**: Practice recovery procedures quarterly

---

## Cloud Backup Options

### AWS S3

```bash
# Upload backup to S3
aws s3 cp backup.sql.gz s3://financialassist-backups/db_backup_$(date +%Y%m%d).sql.gz

# Download from S3
aws s3 cp s3://financialassist-backups/db_backup_20250127.sql.gz ./restore.sql.gz
```

### Google Cloud Storage

```bash
# Upload backup
gsutil cp backup.sql.gz gs://financialassist-backups/db_backup_$(date +%Y%m%d).sql.gz

# Download
gsutil cp gs://financialassist-backups/db_backup_20250127.sql.gz ./restore.sql.gz
```

---

**Status**: ✅ Complete - Comprehensive backup and recovery procedures
