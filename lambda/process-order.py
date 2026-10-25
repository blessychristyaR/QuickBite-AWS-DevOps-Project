import json
import logging
import boto3
from decimal import Decimal
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("QuickBiteOrders")

sns = boto3.client("sns", region_name="us-west-2")

SNS_TOPIC_ARN = (
    "arn:aws:sns:us-west-2:163918295759:"
    "QuickBiteOrderNotifications"
)


def lambda_handler(event, context):
    records = event.get("Records", [])
    batch_item_failures = []

    logger.info("Received %d SQS message(s)", len(records))

    for record in records:
        message_id = record.get("messageId", "unknown")

        try:
            body = json.loads(record["body"])

            # Support messages wrapped in an SNS notification
            if isinstance(body, dict) and "Message" in body:
                body = json.loads(body["Message"])

            order_id = body.get("orderId")
            if not order_id:
                raise ValueError("Missing required field: orderId")

            customer = body.get("customer", {})
            if not isinstance(customer, dict):
                customer = {}

            customer_name = str(
                body.get("customerName") or customer.get("name", "Not provided")
            )
            customer_email = str(
                body.get("customerEmail") or customer.get("email", "Not provided")
            )
            customer_phone = str(
                body.get("customerPhone") or customer.get("phone", "Not provided")
            )
            customer_address = str(
                body.get("customerAddress") or customer.get("address", "Not provided")
            )

            current_time = datetime.now(timezone.utc).isoformat()

            items = body.get("items", [])
            total = Decimal(str(body.get("total", 0)))
            status = str(body.get("status", "RECEIVED"))

            order = {
                "orderId": str(order_id),
                "status": status,
                "items": items,
                "customerName": customer_name,
                "customerEmail": customer_email,
                "customerPhone": customer_phone,
                "customerAddress": customer_address,
                "total": total,
                "paymentMethod": str(body.get("paymentMethod", "UNKNOWN")),
                "createdAt": str(body.get("createdAt", current_time)),
                "updatedAt": current_time
            }

            table.put_item(Item=order)

            logger.info("Successfully saved order %s", order_id)

            # SNS sends this notification to confirmed topic subscribers.
            message = (
                "A new order has been received on QuickBite!\n\n"
                f"Order ID: {order_id}\n"
                f"Order Status: {status}\n\n"
                "CUSTOMER DETAILS\n"
                f"Name: {customer_name}\n"
                f"Email: {customer_email}\n"
                f"Phone: {customer_phone}\n"
                f"Delivery Address: {customer_address}\n\n"
                "ORDER DETAILS\n"
                f"Items: {json.dumps(items, default=str)}\n"
                f"Total: {total}\n"
                f"Payment Method: {order['paymentMethod']}\n\n"
                "Please check the QuickBite admin dashboard "
                "to manage this order."
            )

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"QuickBite - New Order Received: {order_id}",
                Message=message
            )

            logger.info(
                "SNS admin notification published for order %s",
                order_id
            )

        except Exception:
            logger.exception(
                "Failed to process SQS message %s",
                message_id
            )

            batch_item_failures.append({
                "itemIdentifier": message_id
            })

    return {
        "batchItemFailures": batch_item_failures
    }

