# QuickBite Architecture Notes

## 1. Order submission and processing

1. The customer submits an order from the website.
2. The frontend sends a `POST /orders` request to API Gateway.
3. The `submit-order` Lambda handles the request and places a message onto the SQS order-processing queue.
4. SQS invokes the configured `process-order` Lambda through its event-source mapping.
5. The processing function stores order details/status in DynamoDB and publishes configured notifications through SNS.
6. Messages that repeatedly fail processing can be routed to the configured dead-letter queue according to the SQS redrive policy.

## 2. Order status lookup

1. The customer enters an order ID.
2. The website calls `GET /orders/{orderId}`.
3. The `get-order-status` Lambda retrieves the matching record from DynamoDB.
4. The response is rendered in the website's tracking panel.

## 3. Status update

1. The website's demonstration timer requests a new status using `PUT /orders/{orderId}`.
2. API Gateway invokes `update-order-status`.
3. The Lambda validates the requested status and updates the existing DynamoDB record.
4. The response is used to refresh the tracking display.

The website's three-second progression is for demonstration only. It is browser-driven, can stop when the browser closes, and is not a substitute for a server-side workflow in production.

## 4. Operational considerations

- Check CloudWatch logs when a Lambda invocation fails.
- Verify Lambda execution roles and least-privilege IAM policies.
- Verify API Gateway routes, integrations, deployments, and CORS configuration.
- Check the SQS event-source mapping, visibility timeout, redrive policy, and dead-letter queue.
- Review DynamoDB keys and item attributes against the code's expected schema.
- Avoid public unauthenticated write routes for production use.
