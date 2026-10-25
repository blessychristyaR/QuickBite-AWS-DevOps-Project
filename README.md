# QuickBite — Event-Driven Order Processing and Failure Recovery System

QuickBite is a learning project that demonstrates a food-ordering frontend connected to AWS services for order submission, asynchronous processing, persistence, notifications, and order-status retrieval.

> **Project status:** The frontend and AWS integration have been tested for order placement, order processing, email notification, and order tracking. The automatic six-stage status progression is a **frontend demonstration feature** that updates the backend through an API. It is not a real restaurant preparation or delivery workflow.

## Project goals

- Host a static food-ordering interface.
- Expose backend operations through Amazon API Gateway.
- Demonstrate asynchronous order processing with AWS Lambda and Amazon SQS.
- Store order records in Amazon DynamoDB.
- Send configured order notifications using Amazon SNS.
- Retrieve and update order status through API endpoints.
- Practice IAM permissions, CloudWatch logs, API integration, CORS troubleshooting, and Git version control.

## Architecture

```text
Customer browser
      |
      v
Amazon S3 static website (frontend/index.html)
      |
      v
Amazon API Gateway (REST API)
      |
      +---- POST /orders ------------> submit-order Lambda
      |                                      |
      |                                      v
      |                              Amazon SQS queue
      |                                      |
      |                                      v
      |                              process-order Lambda
      |                                /            \
      |                               v              v
      |                     Amazon DynamoDB      Amazon SNS
      |
      +---- GET /orders/{orderId} --> get-order-status Lambda
      |                                      |
      |                                      v
      |                               Amazon DynamoDB
      |
      +---- PUT /orders/{orderId} --> update-order-status Lambda
                                             |
                                             v
                                      Amazon DynamoDB

CloudWatch: Lambda logs and troubleshooting
IAM: permissions between AWS resources
SQS dead-letter queue: configured for failed message handling
```

## AWS services

| Service | Role in this project |
|---|---|
| Amazon S3 | Hosts the static frontend website. |
| Amazon API Gateway (REST API) | Provides API routes used by the website. |
| AWS Lambda | Handles order submission, queued processing, status retrieval, and status updates. |
| Amazon SQS | Buffers order-processing messages asynchronously. |
| Amazon SQS dead-letter queue | Receives messages that cannot be processed according to queue redrive settings. |
| Amazon DynamoDB | Stores order records and status. |
| Amazon SNS | Sends configured email notifications. |
| Amazon CloudWatch | Stores Lambda logs for debugging and monitoring. |
| AWS IAM | Controls permissions for AWS resources and functions. |

## Main API routes

The deployed REST API uses these routes:

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/orders` | Submit a new order. |
| `GET` | `/orders/{orderId}` | Retrieve an order and its current status. |
| `PUT` | `/orders/{orderId}` | Update an existing order status. |

The live API endpoint is intentionally not repeated in this documentation. Configure your own endpoint in the frontend if you recreate the project in another AWS account or region.

## Frontend features

- Food-order form and order confirmation.
- Generated order ID and copy-ID action.
- Order tracking by order ID.
- Order progress display.
- Order cancellation and rating UI where supported by the order status.
- Automatic status progression for demonstration, using three-second intervals while the tracking page is open and the order begins in `RECEIVED` status.

### Demonstration status sequence

`RECEIVED → CONFIRMED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED`

This timer runs in the browser and is intended for demonstration only. It stops if the page/session closes and should not be treated as a production workflow or authoritative delivery estimate.

## Repository structure

```text
QuickBite/
├── README.md
├── .gitignore
├── frontend/
│   └── index.html
├── docs/
│   └── architecture.md
└── lambda/
    └── README.md
```

The Lambda folder currently contains instructions for adding the deployed function source. Add the actual source code for each function before presenting the repository as a complete source-code repository. Do not create placeholder Python files that imply they contain working implementations.

## Running locally

1. Clone or download this repository.
2. Open `frontend/index.html` in a browser to inspect the frontend.
3. To test AWS-connected features, ensure the API endpoint configured in `index.html` points to a deployed API with the expected routes, CORS settings, Lambda integrations, and permissions.
4. Do not assume that opening the HTML file locally will make every API feature work; the AWS backend must be available and configured correctly.

## Adding Lambda source code

The deployed Lambda source should be exported from the AWS Lambda console and added under `lambda/` using clear filenames, for example:

- `submit_order.py`
- `process_order.py`
- `get_order_status.py`
- `update_order_status.py`


## Security and cost notes

- Never commit AWS access keys, secret keys, passwords, `.env` files, or customer personal information.
- Review API authorization before exposing an endpoint publicly. A route configured with no authorization is not suitable for sensitive production operations.
- The project is for learning and demonstration, not production food delivery.
- AWS resources may incur charges. Check billing and remove resources that are no longer needed.

## Learning outcomes

This project provided hands-on practice with event-driven design, API Gateway, Lambda, SQS, DynamoDB, SNS, IAM, CloudWatch, CORS troubleshooting, and integrating frontend and backend services.

## Author

**Blessy Christya R** — Artificial Intelligence and Data Science Graduate; aspiring AWS Cloud / DevOps Engineer.
