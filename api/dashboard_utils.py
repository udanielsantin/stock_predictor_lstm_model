"""
Utilities for generating dashboard visualizations
"""

import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
import io
import base64
from typing import Dict, List, Any
import numpy as np


def get_dashboard_data(log_dir: str = "logs") -> Dict[str, Any]:
    """
    Process all logs and return dashboard data
    
    Args:
        log_dir: Directory containing log files
        
    Returns:
        Dictionary with processed dashboard data
    """
    log_path = Path(log_dir)
    
    if not log_path.exists():
        return {
            "total_predictions": 0,
            "successful": 0,
            "failed": 0,
            "logs": []
        }
    
    log_files = sorted(log_path.glob("prediction_*.json"))
    
    logs = []
    successful = 0
    failed = 0
    tickers_count = {}
    daily_predictions = {}
    execution_times = []
    r2_scores = []
    prediction_changes = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                logs.append(log_data)
                
                # Count success/failure
                if log_data["execution"]["success"]:
                    successful += 1
                    
                    # Collect metrics
                    if "result" in log_data and log_data["result"]:
                        r2 = log_data["result"].get("metrics", {}).get("R2")
                        if r2 is not None:
                            r2_scores.append(r2)
                        
                        change_pct = log_data["result"].get("price_change_pct")
                        if change_pct is not None:
                            prediction_changes.append(change_pct)
                else:
                    failed += 1
                
                # Count by ticker
                ticker = log_data["request"]["ticker"]
                tickers_count[ticker] = tickers_count.get(ticker, 0) + 1
                
                # Count by day
                timestamp = log_data["timestamp"]
                day = timestamp.split("T")[0]
                daily_predictions[day] = daily_predictions.get(day, 0) + 1
                
                # Execution times
                exec_time = log_data["execution"]["duration_seconds"]
                execution_times.append(exec_time)
        
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
    
    return {
        "total_predictions": len(logs),
        "successful": successful,
        "failed": failed,
        "logs": sorted(logs, key=lambda x: x["timestamp"], reverse=True),
        "tickers_count": tickers_count,
        "daily_predictions": daily_predictions,
        "execution_times": execution_times,
        "r2_scores": r2_scores,
        "prediction_changes": prediction_changes
    }


def create_ticker_distribution_chart(data: Dict[str, Any]) -> str:
    """Create bar chart of predictions by ticker"""
    tickers_count = data["tickers_count"]
    
    if not tickers_count:
        return ""
    
    # Sort by count
    sorted_tickers = sorted(tickers_count.items(), key=lambda x: x[1], reverse=True)[:10]
    tickers = [t[0] for t in sorted_tickers]
    counts = [t[1] for t in sorted_tickers]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(tickers, counts, color='#667eea', alpha=0.8)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Ticker', fontsize=12, fontweight='bold')
    ax.set_ylabel('Número de Previsões', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Ações Mais Previstas', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_daily_predictions_chart(data: Dict[str, Any]) -> str:
    """Create line chart of daily predictions"""
    daily_data = data["daily_predictions"]
    
    if not daily_data:
        return ""
    
    # Sort by date
    sorted_days = sorted(daily_data.items())
    dates = [datetime.fromisoformat(d[0]) for d in sorted_days]
    counts = [d[1] for d in sorted_days]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, counts, marker='o', linewidth=2, markersize=8, 
            color='#667eea', markerfacecolor='#764ba2')
    ax.fill_between(dates, counts, alpha=0.3, color='#667eea')
    
    ax.set_xlabel('Data', fontsize=12, fontweight='bold')
    ax.set_ylabel('Número de Previsões', fontsize=12, fontweight='bold')
    ax.set_title('Previsões por Dia', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_execution_time_chart(data: Dict[str, Any]) -> str:
    """Create histogram of execution times"""
    exec_times = data["execution_times"]
    
    if not exec_times:
        return ""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    n, bins, patches = ax.hist(exec_times, bins=20, color='#667eea', alpha=0.7, edgecolor='black')
    
    # Color the bars with a gradient
    cm = plt.cm.get_cmap('viridis')
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    col = bin_centers - min(bin_centers)
    col /= max(col)
    
    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', cm(c))
    
    ax.set_xlabel('Tempo de Execução (segundos)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax.set_title('Distribuição de Tempo de Execução', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    # Add statistics
    avg_time = np.mean(exec_times)
    ax.axvline(avg_time, color='red', linestyle='--', linewidth=2, label=f'Média: {avg_time:.2f}s')
    ax.legend()
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_r2_distribution_chart(data: Dict[str, Any]) -> str:
    """Create histogram of R² scores"""
    r2_scores = data["r2_scores"]
    
    if not r2_scores:
        return ""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    n, bins, patches = ax.hist(r2_scores, bins=15, color='#51cf66', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('R² Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax.set_title('Distribuição de R² Score (Qualidade das Previsões)', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    # Add statistics
    avg_r2 = np.mean(r2_scores)
    ax.axvline(avg_r2, color='red', linestyle='--', linewidth=2, label=f'Média: {avg_r2:.4f}')
    ax.legend()
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"
