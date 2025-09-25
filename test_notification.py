import asyncio
from src.services.notification_service import NotificationService
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_notification():
    # Get AWS configuration from environment
    aws_region = os.getenv('AWS_REGION', 'eu-west-1')
    sns_topic_arn = os.getenv('AWS_SNS_TOPIC_ARN')

    if not sns_topic_arn:
        raise ValueError("AWS_SNS_TOPIC_ARN must be set")
        
    # Test AWS credentials
    print("Testing AWS credentials...")
    try:
        boto3.client('sts').get_caller_identity()
        print("AWS credentials are valid!")
    except Exception as e:
        print(f"AWS credentials error: {str(e)}")

    # Create notification service
    notifier = NotificationService(sns_topic_arn, aws_region)
    
    print(f"Using SNS Topic ARN: {sns_topic_arn}")
    print(f"Using AWS Region: {aws_region}")

    # Test data
    test_link = {
        "id": 999,
        "url": "https://test.example.com",
        "title": "Test Link",
        "last_checked_at": "2025-09-22T12:00:00Z"
    }

    test_result = {
        "error": "Test notification for dead link detection",
        "status_code": 404,
        "response_time": 0
    }

    # Send test notification
    print("Sending test notification...")
    try:
        response = await notifier.notify_dead_link(test_link, test_result)
        print(f"Test notification sent successfully!")
        print(f"SNS Response: {response}")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_notification())