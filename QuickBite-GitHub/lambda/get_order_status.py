import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("QuickBiteOrders")


def decimal_to_number(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)

    if isinstance(value, dict):
        return {k: decimal_to_number(v) for k, v in value.items()}

    if isinstance(value, list):
        return [decimal_to_number(v) for v in value]

    return value


def lambda_handler(event, context):
    try:
        path_parameters = event.get("pathParameters") or {}
        order_id = path_parameters.get("orderId")

        if not order_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "message": "Order ID is required"
                })
            }

        response = table.get_item(
            Key={"orderId": order_id}
        )

        order = response.get("Item")

        if not order:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "message": "Order not found"
                })
            }

        order = decimal_to_number(order)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(order)
        }

    except Exception as error:
        print(f"Error retrieving order: {error}")

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Unable to retrieve order"
            })
        }

