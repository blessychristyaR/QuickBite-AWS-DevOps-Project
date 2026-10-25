import json
import boto3
from datetime import datetime, timezone
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("QuickBiteOrders")

ALLOWED_STATUSES = {
    "RECEIVED",
    "CONFIRMED",
    "PREPARING",
    "READY",
    "OUT_FOR_DELIVERY",
    "DELIVERED",
    "FAILED",
    "CANCELLED"
}


def decimal_to_number(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {key: decimal_to_number(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_to_number(item) for item in value]
    return value


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,OPTIONS",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        path_parameters = event.get("pathParameters") or {}
        order_id = (path_parameters.get("orderId") or "").strip()
        

        if not order_id:
            return response(400, {"message": "Order ID is required"})

        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        new_status = str(body.get("status", "")).strip().upper()

        if new_status not in ALLOWED_STATUSES:
            return response(400, {
                "message": "Invalid status",
                "allowedStatuses": sorted(ALLOWED_STATUSES)
            })

        result = table.update_item(
            Key={"orderId": order_id},
            UpdateExpression="SET #status = :status, updatedAt = :updatedAt",
            ConditionExpression="attribute_exists(orderId)",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": new_status,
                ":updatedAt": datetime.now(timezone.utc).isoformat()
            },
            ReturnValues="ALL_NEW"
        )

        return response(200, {
            "message": "Order status updated successfully",
            "order": decimal_to_number(result["Attributes"])
        })

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return response(404, {"message": "Order not found"})

    except Exception as error:
        print(f"Error updating order status: {error}")
        return response(500, {"message": "Unable to update order status"})

