import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    print("Event:", event)

    # Get bucket + object from EventBridge detail
    bucket = event["detail"]["bucket"]["name"]
    key = event["detail"]["object"]["key"]

    # Only process PNG files
    if not key.lower().endswith(".png"):
        return {"status": "skipped", "file": key}

    # Add tag "Watermarked=ATS"
    s3.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={"TagSet": [{"Key": "Watermarked", "Value": "ATS"}]}
    )

    return {"status": "tagged", "bucket": bucket, "key": key}
