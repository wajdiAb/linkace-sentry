import boto3
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, topic_arn: str, aws_region: str = 'us-east-1'):
        """
        Initialize the notification service with AWS SNS.
        
        Args:
            topic_arn: The ARN of the SNS topic to publish to
            aws_region: AWS region where the SNS topic is located
        """
        self.topic_arn = topic_arn
        self.sns = boto3.client('sns', region_name=aws_region)
    
    async def notify_dead_link(self, link_data: Dict[str, Any], check_result: Dict[str, Any]) -> None:
        """
        Send a notification about a dead link.
        
        Args:
            link_data: Information about the link from LinkAce
            check_result: Results from the link check
        """
        try:
            message = {
                "type": "dead_link",
                "link": {
                    "id": link_data.get("id"),
                    "url": link_data.get("url"),
                    "title": link_data.get("title"),
                    "last_checked": link_data.get("last_checked_at")
                },
                "check_result": {
                    "error": check_result.get("error"),
                    "status_code": check_result.get("status_code"),
                    "response_time": check_result.get("response_time")
                }
            }
            
            # Send the notification
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f"Dead Link Found: {link_data.get('title', link_data.get('url'))}"
            )
            
            logger.info("Sent notification for dead link: %s", link_data.get("url"))
            
        except Exception as e:
            logger.error("Failed to send notification: %s", str(e))
    
    async def notify_restored_link(self, link_data: Dict[str, Any]) -> None:
        """
        Send a notification about a previously dead link that is now working.
        
        Args:
            link_data: Information about the link from LinkAce
        """
        try:
            message = {
                "type": "restored_link",
                "link": {
                    "id": link_data.get("id"),
                    "url": link_data.get("url"),
                    "title": link_data.get("title"),
                    "last_checked": link_data.get("last_checked_at")
                }
            }
            
            # Send the notification
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f"Link Restored: {link_data.get('title', link_data.get('url'))}"
            )
            
            logger.info("Sent notification for restored link: %s", link_data.get("url"))
            
        except Exception as e:
            logger.error("Failed to send notification: %s", str(e))
            raise

    async def notify_working_link(self, link_data: Dict[str, Any], check_result: Dict[str, Any]) -> None:
        """
        Send a notification about a working link.
        
        Args:
            link_data: Information about the link from LinkAce
            check_result: Results from the link check
        """
        try:
            message = {
                "type": "working_link",
                "link": {
                    "id": link_data.get("id"),
                    "url": link_data.get("url"),
                    "title": link_data.get("title"),
                    "last_checked": link_data.get("last_checked_at")
                },
                "check_result": {
                    "status_code": check_result.get("status_code"),
                    "response_time": check_result.get("response_time"),
                    "final_url": check_result.get("final_url")
                }
            }
            
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f"Link Check Successful: {link_data.get('title', link_data.get('url'))}"
            )
            
            logger.info("Sent notification for working link: %s", link_data.get("url"))
            
        except Exception as e:
            logger.error("Failed to send working link notification: %s", str(e))
            raise