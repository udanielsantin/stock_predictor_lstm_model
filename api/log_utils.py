import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle NumPy types"""
    def default(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class PredictionLogger:
    def __init__(self):
        """
        Initialize the logger with S3 configuration
        
        All logs are stored in S3 only.
        Requires environment variables:
        - S3_BUCKET_NAME: Name of the S3 bucket
        - AWS_ACCESS_KEY_ID: AWS access key
        - AWS_SECRET_ACCESS_KEY: AWS secret key
        - AWS_REGION: AWS region (default: us-east-1)
        - S3_LOG_PREFIX: S3 prefix for logs (default: logs/)
        """
        # S3 configuration (from environment variables)
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_prefix = os.getenv("S3_LOG_PREFIX", "logs/")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        if not self.s3_bucket:
            raise ValueError(
                "S3_BUCKET_NAME environment variable is required. "
                "Please configure it before running the application."
            )
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.aws_region
            )
            print(f"✅ S3 Logger initialized with bucket: {self.s3_bucket}")
        except Exception as e:
            raise ValueError(f"Failed to initialize S3 client: {e}")
    
    def create_log_entry(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        result: Dict[str, Any],
        duration: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a structured log entry
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date of analysis
            end_date: End date of analysis
            result: Prediction result dictionary
            duration: Execution time in seconds
            success: Whether prediction was successful
            error: Error message if failed
            
        Returns:
            Structured log dictionary
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        log_entry = {
            "timestamp": timestamp,
            "request": {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date
            },
            "execution": {
                "duration_seconds": round(duration, 3),
                "success": success
            }
        }
        
        if success and result:
            log_entry["result"] = {
                "last_close": result.get("last_close"),
                "next_price": result.get("next_price"),
                "price_change": result.get("price_change"),
                "price_change_pct": result.get("price_change_pct"),
                "data_points": result.get("data_points"),
                "metrics": result.get("metrics", {})
            }
        elif error:
            log_entry["error"] = error
        
        return log_entry
    
    def log_prediction(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        result: Dict[str, Any],
        duration: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Log a prediction directly to S3
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date of analysis
            end_date: End date of analysis
            result: Prediction result dictionary
            duration: Execution time in seconds
            success: Whether prediction was successful
            error: Error message if failed
            
        Returns:
            Dictionary with S3 path and timestamp
        """
        # Create log entry
        log_entry = self.create_log_entry(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            result=result,
            duration=duration,
            success=success,
            error=error
        )
        
        # Upload to S3
        try:
            timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
            s3_key = f"{self.s3_prefix}{timestamp}_{ticker}.json"
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(log_entry, ensure_ascii=False, cls=NumpyEncoder),
                ContentType='application/json'
            )
            
            print(f"📝 Log uploaded to S3: s3://{self.s3_bucket}/{s3_key}")
            
            return {
                "s3_path": f"s3://{self.s3_bucket}/{s3_key}",
                "s3_key": s3_key,
                "timestamp": log_entry["timestamp"]
            }
        except ClientError as e:
            print(f"❌ Failed to upload log to S3: {e}")
            raise
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent log files from S3
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries from S3
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix,
                MaxKeys=limit
            )
            
            logs = []
            
            if 'Contents' not in response:
                return logs
            
            # Sort by last modified, most recent first
            objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            
            for obj in objects[:limit]:
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.s3_bucket,
                        Key=obj['Key']
                    )
                    content = json.loads(response['Body'].read().decode('utf-8'))
                    logs.append(content)
                except Exception as e:
                    print(f"⚠️  Failed to read log {obj['Key']}: {e}")
                    continue
            
            return logs
            
        except ClientError as e:
            print(f"❌ Failed to retrieve logs from S3: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged predictions from S3
        
        Returns:
            Statistics dictionary
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix
            )
            
            total_predictions = 0
            successful = 0
            failed = 0
            tickers = set()
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_predictions += 1
                    try:
                        log_response = self.s3_client.get_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        log_data = json.loads(log_response['Body'].read().decode('utf-8'))
                        
                        if log_data["execution"]["success"]:
                            successful += 1
                        else:
                            failed += 1
                        
                        tickers.add(log_data["request"]["ticker"])
                    except Exception as e:
                        print(f"⚠️  Failed to parse log {obj['Key']}: {e}")
                        continue
            
            return {
                "total_predictions": total_predictions,
                "successful": successful,
                "failed": failed,
                "unique_tickers": len(tickers),
                "tickers": sorted(list(tickers))
            }
            
        except ClientError as e:
            print(f"❌ Failed to retrieve stats from S3: {e}")
            return {
                "total_predictions": 0,
                "successful": 0,
                "failed": 0,
                "unique_tickers": 0,
                "tickers": []
            }
