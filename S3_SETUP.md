# S3 Configuration Guide

## Bucket Name Recommendation

**Bucket Name:** `stock-predictor-logs-yyyymmdd`

Example: `stock-predictor-logs-20251226`

**Note:** S3 bucket names must be globally unique. Replace `yyyymmdd` with today's date or add a unique suffix to ensure uniqueness.

---

## Bucket Structure

```
s3://stock-predictor-logs-yyyymmdd/
└── logs/
    ├── 2025/01/15/123045_ABEV3.json
    ├── 2025/01/15/123120_VALE3.json
    ├── 2025/01/15/123200_PETR4.json
    └── ...
```

**Prefix:** `logs/` (organized by date and timestamp)

---

## Environment Variables Required

Configure these environment variables on your EC2 instance:

```bash
export S3_BUCKET_NAME="stock-predictor-logs-yyyymmdd"
export S3_LOG_PREFIX="logs/"
export AWS_REGION="us-east-1"  # or your preferred region
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

Or create a `.env` file in the API directory:

```env
S3_BUCKET_NAME=stock-predictor-logs-yyyymmdd
S3_LOG_PREFIX=logs/
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

---

## AWS Setup Steps

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://stock-predictor-logs-yyyymmdd --region us-east-1
   ```

2. **Set Bucket Permissions (Optional but recommended):**
   ```bash
   # Block public access
   aws s3api put-public-access-block \
     --bucket stock-predictor-logs-yyyymmdd \
     --public-access-block-configuration \
     "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
   ```

3. **Create IAM User** (if you don't have AWS credentials yet):
   - Go to IAM Console → Users → Create User
   - Attach policy: `AmazonS3FullAccess` (or create custom policy below)

4. **Custom IAM Policy** (More restrictive):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::stock-predictor-logs-yyyymmdd",
           "arn:aws:s3:::stock-predictor-logs-yyyymmdd/*"
         ]
       }
     ]
   }
   ```

---

## What Changed in the Code

### ✅ Removed
- GitHub Actions workflow (`.github/workflows/deploy.yml`)
- Local log directory saving (`api/logs/`)
- `enable_s3` parameter from `PredictionLogger`

### ✅ Updated
- **log_utils.py**: Now S3-only, all logs uploaded directly
- **app.py**: Initialize logger with S3 config, removed local log_dir parameter
- **dashboard_utils.py**: Reads logs from S3 instead of local files
- **upload_logs_to_s3.py**: Kept as-is (can be deleted if not needed)

---

## How to Deploy on EC2

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd stock_predictor_lstm_model/api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # Create .env file or set in your shell
   export S3_BUCKET_NAME="stock-predictor-logs-yyyymmdd"
   export AWS_ACCESS_KEY_ID="..."
   export AWS_SECRET_ACCESS_KEY="..."
   ```

4. **Run API:**
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```

---

## Testing

After deployment, test with:

```bash
# Test prediction endpoint
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker": "ABEV3", "start_date": "2024-01-01", "end_date": "2024-12-31"}'

# Check recent logs (from S3)
curl http://localhost:8000/api/logs/recent?limit=5

# Check stats
curl http://localhost:8000/api/logs/stats

# View dashboard
curl http://localhost:8000/dashboard
```

---

## Logs Format

Each log file in S3 contains:

```json
{
  "timestamp": "2025-01-15T12:30:45.123Z",
  "request": {
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "execution": {
    "duration_seconds": 2.345,
    "success": true
  },
  "result": {
    "last_close": 15.50,
    "next_price": 16.20,
    "price_change": 0.70,
    "price_change_pct": 4.52,
    "data_points": 252,
    "metrics": {
      "R2": 0.8765
    }
  }
}
```

Or if there's an error:

```json
{
  "timestamp": "2025-01-15T12:30:45.123Z",
  "request": {
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "execution": {
    "duration_seconds": 0.123,
    "success": false
  },
  "error": "Error message here"
}
```

---

## Notes

- All logs are now stored **ONLY in S3** - no local backup
- The API requires S3 configuration to run
- Logs are organized by date in S3 for easy navigation and cleanup
- Dashboard and API endpoints read directly from S3
- Consider setting S3 bucket lifecycle policies to archive old logs if needed

