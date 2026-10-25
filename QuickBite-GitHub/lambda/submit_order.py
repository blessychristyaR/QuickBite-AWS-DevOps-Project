import json
import logging
import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")

QUEUE_URL = "https://sqs.us-west-2.amazonaws.com/163918295759/order-processing-queue"


def lambda_handler(event, context):
    try:
        # Read order data from API Gateway or a direct Lambda test
        if "body" in event:
            body = event["body"]

            if isinstance(body, str):
                order = json.loads(body)
            elif isinstance(body, dict):
                order = body
            else:
                raise ValueError("Invalid request body")
        else:
            order = event

        # Support customer details sent as either flat fields or a nested object
        customer = order.get("customer", {})
        if not isinstance(customer, dict):
            customer = {}

        customer_name = str(
            order.get("customerName") or customer.get("name", "")
        ).strip()

        customer_email = str(
            order.get("customerEmail") or customer.get("email", "")
        ).strip()

        customer_phone = str(
            order.get("customerPhone")
            or order.get("phone")
            or customer.get("phone", "")
        ).strip()

        customer_address = str(
            order.get("customerAddress")
            or order.get("address")
            or customer.get("address", "")
        ).strip()

        items = order.get("items", [])

        if not customer_name:
            raise ValueError("customerName is required")

        if not customer_email or "@" not in customer_email:
            raise ValueError("A valid customerEmail is required")

        if not customer_phone:
            raise ValueError("customerPhone is required")

        if not customer_address:
            raise ValueError("customerAddress is required")

        if not isinstance(items, list) or not items:
            raise ValueError("At least one item is required")

        total = Decimal("0")

        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each item must be an object")

            name = str(item.get("name", "")).strip()
            quantity = int(item.get("quantity", 0))
            price = Decimal(str(item.get("price", 0)))

            if not name or quantity < 1 or price < 0:
                raise ValueError("Invalid item name, quantity, or price")

            total += price * quantity

        order_id = "QB-" + uuid.uuid4().hex[:8].upper()
        timestamp = datetime.now(timezone.utc).isoformat()

        order_message = {
            "orderId": order_id,
            "status": "RECEIVED",
            "customerName": customer_name,
            "customerEmail": customer_email,
            "customerPhone": customer_phone,
            "customerAddress": customer_address,
            "items": items,
            "total": float(total),
            "paymentMethod": str(
                order.get("paymentMethod", "Cash on Delivery")
            ),
            "createdAt": timestamp
        }

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order_message)
        )

        logger.info("Order %s sent to SQS", order_id)

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Order submitted successfully",
                "orderId": order_id,
                "status": "RECEIVED",
                "total": float(total)
            })
        }

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        logger.warning("Invalid order request: %s", str(error))

        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(error)})
        }

    except Exception:
        logger.exception("Unexpected error while submitting order")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Unable to submit order"})
        }

