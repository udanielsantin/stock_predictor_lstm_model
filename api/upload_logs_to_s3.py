"""
Script para fazer upload de logs para o S3
Execute este script para enviar logs locais para o S3
"""

import os
import sys
from pathlib import Path
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Configurações do S3 (defina suas variáveis de ambiente ou modifique aqui)
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "your-bucket-name")
S3_PREFIX = os.getenv("S3_LOG_PREFIX", "stock-predictions/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOG_DIR = "logs"


def upload_logs_to_s3(dry_run=False):
    """
    Upload all local logs to S3
    
    Args:
        dry_run: If True, only shows what would be uploaded without actually uploading
    """
    
    # Initialize S3 client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=AWS_REGION
        )
    except Exception as e:
        print(f"❌ Failed to initialize S3 client: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - S3_BUCKET_NAME")
        return False
    
    # Get all log files
    log_dir = Path(LOG_DIR)
    if not log_dir.exists():
        print(f"❌ Log directory not found: {LOG_DIR}")
        return False
    
    log_files = list(log_dir.glob("prediction_*.json"))
    
    if not log_files:
        print(f"📭 No log files found in {LOG_DIR}")
        return True
    
    print(f"📊 Found {len(log_files)} log files")
    print(f"🪣 Target S3 bucket: {S3_BUCKET}")
    print(f"📁 S3 prefix: {S3_PREFIX}")
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be uploaded\n")
    
    uploaded = 0
    failed = 0
    
    for log_file in log_files:
        try:
            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Extract info for S3 key
            ticker = log_data["request"]["ticker"]
            timestamp = log_data["timestamp"].replace(":", "").replace("-", "").replace("Z", "")
            
            # Create S3 key with organized structure: prefix/YYYY/MM/DD/timestamp_ticker.json
            dt = datetime.fromisoformat(log_data["timestamp"].replace("Z", "+00:00"))
            s3_key = f"{S3_PREFIX}{dt.year}/{dt.month:02d}/{dt.day:02d}/{timestamp}_{ticker}.json"
            
            if dry_run:
                print(f"📝 Would upload: {log_file.name} -> s3://{S3_BUCKET}/{s3_key}")
                uploaded += 1
            else:
                # Upload to S3
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Body=json.dumps(log_data, ensure_ascii=False, indent=2),
                    ContentType='application/json',
                    Metadata={
                        'ticker': ticker,
                        'timestamp': log_data["timestamp"],
                        'success': str(log_data["execution"]["success"])
                    }
                )
                
                print(f"✅ Uploaded: {log_file.name} -> s3://{S3_BUCKET}/{s3_key}")
                uploaded += 1
        
        except ClientError as e:
            print(f"❌ Failed to upload {log_file.name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Error processing {log_file.name}: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Total files: {len(log_files)}")
    print(f"   ✅ Uploaded: {uploaded}")
    if failed > 0:
        print(f"   ❌ Failed: {failed}")
    print("=" * 60)
    
    return failed == 0


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload prediction logs to S3")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📤 Stock Prediction Logs - S3 Uploader")
    print("=" * 60)
    print()
    
    success = upload_logs_to_s3(dry_run=args.dry_run)
    
    if success:
        print("\n✅ Upload completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Upload failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
