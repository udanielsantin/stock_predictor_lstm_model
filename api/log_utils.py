"""
Utilities for logging prediction results
Supports local file storage and S3 upload
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
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
    """Logger for stock prediction results"""
    
    def __init__(self, log_dir: str = "logs", enable_s3: bool = False):
        """
        Initialize the logger
        
        Args:
            log_dir: Local directory to save logs
            enable_s3: Whether to enable S3 uploads
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_s3 = enable_s3
        
        # S3 configuration (from environment variables)
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_prefix = os.getenv("S3_LOG_PREFIX", "stock-predictions/")
        
        if self.enable_s3:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
            except Exception as e:
                print(f"⚠️  S3 client initialization failed: {e}")
                self.enable_s3 = False
    
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
    
    def save_local(self, log_entry: Dict[str, Any]) -> str:
        """
        Save log entry to local file
        
        Args:
            log_entry: Log dictionary
            
        Returns:
            Path to saved file
        """
        # Create filename with timestamp and ticker
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        ticker = log_entry["request"]["ticker"]
        filename = f"prediction_{ticker}_{timestamp}.json"
        filepath = self.log_dir / filename
        
        # Save to file with NumpyEncoder
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        
        return str(filepath)
    
    def upload_to_s3(self, log_entry: Dict[str, Any]) -> bool:
        """
        Upload log entry to S3
        
        Args:
            log_entry: Log dictionary
            
        Returns:
            Success status
        """
        if not self.enable_s3 or not self.s3_bucket:
            return False
        
        try:
            # Create S3 key
            timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
            ticker = log_entry["request"]["ticker"]
            s3_key = f"{self.s3_prefix}{timestamp}_{ticker}.json"
            
            # Upload to S3 with NumpyEncoder
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(log_entry, ensure_ascii=False, cls=NumpyEncoder),
                ContentType='application/json'
            )
            
            print(f"✅ Log uploaded to S3: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to upload to S3: {e}")
            return False
    
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
        Log a prediction (saves locally and optionally to S3)
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date of analysis
            end_date: End date of analysis
            result: Prediction result dictionary
            duration: Execution time in seconds
            success: Whether prediction was successful
            error: Error message if failed
            
        Returns:
            Dictionary with file paths/status
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
        
        # Save locally
        local_path = self.save_local(log_entry)
        print(f"📝 Log saved: {local_path}")
        
        # Upload to S3 if enabled
        s3_uploaded = False
        if self.enable_s3:
            s3_uploaded = self.upload_to_s3(log_entry)
        
        return {
            "local_path": local_path,
            "s3_uploaded": s3_uploaded,
            "timestamp": log_entry["timestamp"]
        }
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Get recent log files
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        log_files = sorted(self.log_dir.glob("prediction_*.json"), reverse=True)[:limit]
        
        logs = []
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs.append(json.load(f))
        
        return logs
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged predictions
        
        Returns:
            Statistics dictionary
        """
        log_files = list(self.log_dir.glob("prediction_*.json"))
        
        total_predictions = len(log_files)
        successful = 0
        failed = 0
        tickers = set()
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                if log_data["execution"]["success"]:
                    successful += 1
                else:
                    failed += 1
                tickers.add(log_data["request"]["ticker"])
        
        return {
            "total_predictions": total_predictions,
            "successful": successful,
            "failed": failed,
            "unique_tickers": len(tickers),
            "tickers": sorted(list(tickers))
        }
