import boto3
import json
import time
import random
from datetime import datetime

# -------------------------
# Configurations
# -------------------------
REGION_NAME = "ap-south-1"
STREAM_NAME = "stock-data-stream"
STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]

# Initialize boto3 client
kinesis_client = boto3.client("kinesis", region_name=REGION_NAME)

# Simulated starting prices
prices = {ticker: random.uniform(2000, 3000) for ticker in STOCKS}

def get_fake_price(ticker):
    """Simulate price change with random walk"""
    change = random.uniform(-10, 10)
    prices[ticker] += change
    return round(prices[ticker], 2)

def send_stock_data():
    """Send simulated stock price data to Kinesis"""
    while True:
        for ticker in STOCKS:
            price = get_fake_price(ticker)

            record = {
                "ticker": ticker,
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            }

            try:
                response = kinesis_client.put_record(
                    StreamName=STREAM_NAME,
                    Data=json.dumps(record),
                    PartitionKey=ticker
                )
                print(f"[SUCCESS] Sent {record} | ShardId: {response['ShardId']}")
            except Exception as e:
                print(f"[ERROR] Failed to put record for {ticker}: {e}")

        time.sleep(5)  # every 5 seconds

if __name__ == "__main__":
    print("🚀 Starting Simulated Stock Price Producer for Kinesis...")
    send_stock_data()
