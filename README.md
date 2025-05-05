# Ayora Challenge - Food Ordering Service

A Python-based food ordering microservice that allows customers to place orders, restaurant staff to process them, and internal services to retrieve payments that need to be refunded.

## Overview

This service exposes a RESTful API for managing food orders in a simple restaurant system, built with Django and Django REST Framework. It follows the provided OpenAPI spec and is designed to have basic serverless compatibility. Orders transition through a finite state machine and are auto-rejected after 5 minutes via asynchronous tasks, with both one-off and scheduled mechanisms. While optimised for local development, the project includes notes on production-ready enhancements for serverless deployment, as well as CI/CD.

### Key Features

- **Order Management**: Place orders, add items to existing orders
- **Order Processing**: Accept or reject orders, view order lists with filtering
- **Auto-Rejection**: Stale orders automatically rejected after 5 minutes
- **Refund Management**: Endpoint for refund request tracking
- **Test Coverage**: Baseline testing for critical flows

## Getting Started

### Prerequisites

- Docker and Docker Compose (required)
- Make (optional, but recommended for convenience.)

### Setup with Docker Compose

Docker Compose is the expected way to run this service locally:

1. Clone this repository
2. Set up environment variables:
   ```
   cp .env.example .env
   # The default values should work fine for local development
   ```
3. Build and start the containers:
   ```
   make docker-build
   ```

Please note: if not using the `make` tool, please consult the commands in `Makefile` for what needs to be run with Docker to get the system running, ommitted for brevity.

This will start all services required for local development:

- Django application (Primary service)
- PostgreSQL database (Primary database)
- Redis (Message broker / Results backend for async tasks)
- Celery worker (Async task runner)
- Celery Beat scheduler (Cron service)
- Flower (Celery monitoring UI)

If you are unable to get the system running, please contact me by email: szzz66@proton.me

### Useful commands

The `Makefile` has some convenient commands for common operations:

```bash
# Build and start all containers
make docker-build

# Run tests
make test

# Run tests in parallel
make test-parallel

# Access the Django shell
make shell

# Generate the OpenAPI schema, the output will appear in the project root (./schema.yml)
make schema
```

Run `make help` to see all available commands.

## API Documentation

The API follows the OpenAPI specification provided in the challenge. You can access the Swagger UI to explore the API at `http://localhost:8000/schema/swagger-ui/` when running the service locally.

### Key Endpoints

- `POST http://localhost:8000/customers/{customerId}/orders` - Place a new order
- `PATCH http://localhost:8000/customers/{customerId}/orders/{orderId}` - Add items to an existing order
- `GET http://localhost:8000/restaurant/orders` - List all orders (with optional status filter)
  - Example: `GET http://localhost:8000/restaurant/orders?status=accepted` - List only accepted orders
  - Example: `GET http://localhost:8000/restaurant/orders?status=rejected` - List only rejected orders
- `PATCH http://localhost:8000/restaurant/orders/{orderId}` - Accept or reject an order
- `GET http://localhost:8000/internal/refunds` - List all refund requests

## Sample Flow

The system is designed with the following flow in mind:

1. Customer places an order (order status: "placed")
2. Within 5 minutes:
   - Restaurant staff can accept the order (changes status to "accepted")
   - Restaurant staff can reject the order (changes status to "rejected")
   - If no action is taken, the order is automatically rejected by async processes
3. For rejected orders, related refund requests (considered as all order payments linked to rejected orders) can be retrieved via the API by an internal service

To test this flow locally, you can:

1. Create an order with the POST endpoint.
2. Add some additional items (optional)
3. Either accept/reject it, or wait 5 minutes to see auto-rejection
4. Check the refunds endpoint to see refund requests

## Data Model

### Model Relationships

```
Order
│
├── id (PK)
├── customer_id
├── status (FSM field: placed, accepted, rejected)
├── accepted_at (nullable datetime)
├── rejected_at (nullable datetime)
├── created_at
└── updated_at
    │
    ├────────────────────┐
    ▼                    ▼
OrderItem             OrderPayment
│                     │
├── id (PK)           ├── id (PK)
├── order (FK)        ├── order (FK)
├── item_id           ├── payment_info_id
├── quantity          ├── created_at
├── created_at        └── updated_at
└── updated_at
```

The data model follows these key relationships:

- `Order` is the central entity with a unique ID and customer information
- `OrderItem` has a many-to-one relationship with `Order` (one order can have multiple items)
- `OrderPayment` has a many-to-one relationship with `Order` (one order can have multiple payments)
- Both `OrderItem` and `OrderPayment` include a foreign key constraint to `Order` with CASCADE deletion

The system enforces uniqueness constraints:

- Each `item_id` can only appear once per `Order` in the `OrderItem` table, as quantity should be incremented instead
- Each `payment_info_id` can only appear once per `Order` in the `OrderPayment` table

### Order State Machine

The Order model utilises a Finite State Machine (FSM) pattern through the `OrderFSM` mixin to manage order status transitions. The FSM ensures data integrity by controlling the allowed state transitions:

```
            ┌───────────┐
            │  PLACED   │
            └───────────┘
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
    ┌───────────┐   ┌───────────┐
    │  REJECTED │   │  ACCEPTED │
    └───────────┘   └───────────┘
```

Key FSM characteristics:

- All orders start in the `PLACED` state
- Orders can only transition from `PLACED` to either `ACCEPTED` or `REJECTED`
- Once an order reaches a terminal state (`ACCEPTED` or `REJECTED`), it cannot transition back to `PLACED`
- State transitions are strictly controlled through dedicated methods (`mark_as_accepted`, `mark_as_rejected`)
- Each transition records the timestamp of the action in corresponding fields (`accepted_at`, `rejected_at`)
- The FSM enforces validation through conditional methods (`can_mark_as_accepted`, `can_mark_as_rejected`)

This implementation ensures that order state changes follow a predictable, auditable pattern and prevents invalid state transitions, maintaining data integrity throughout the order lifecycle.

## Testing

A baseline of tests covering most of the critical paths have been implemented using a standard `pytest` setup, decoupling this from anything Django-specific. Use either `make test` or `make test-parallel` to run these, which will run the primary test suite found in `ayora/order/tests/`.

Adjust the `Makefile` accordingly to run specific tests.

## Auto-Rejection System

Orders in the "placed" state are automatically marked as rejected if they haven't been accepted by restaurant staff within 5 minutes. To ensure this, a one-time task is scheduled 5 minutes after each order is created. Additionally, a recurring cron-based task runs every minute as a fallback to catch any missed or delayed updates. In most real-world scenarios, this combination is likely sufficient, with the worst-case delay being up to one minute (assuming the cron schedule doesn't let us down). The suitability of this approach ultimately depends on the specific requirements of the use case.

Locally, this uses Celery, but the business logic pattern is designed to transition well to a serverless setup (e.g., Lambda + EventBridge) in production.

## Developer Tools

### Interactive Shell

You can use the Django shell to interact with objects:

```bash
make shell
```

Example queries:

```python
# Get all orders in the placed state
from order.models import Order
Order.objects.filter(status='placed')
```

### Viewing Background Tasks

For local development, you can monitor Celery tasks using Celery Flower:

Access the dashboard at: http://localhost:5555 (Username & password is `flower`)

### Generating OpenAPI Schema

To generate a fresh OpenAPI schema:

```bash
make schema
```

Please note: The schema includes some extra details beyond the task requirements, but the critical paths outlined in the spec should all be there and wired up as expected. Due to the typical setup I use, it would've been a poor use of time to unpick some additional details that get auto-generated from project dependencies, such as standardised error types, pagination, etc.

## Extra Comments

### Auto-Rejection Task Monitoring

When you create an order, you'll see that the auto-rejection task is scheduled with status 'RECEIVED', meaning it is waiting to be executed (+5 mins). You can monitor this in the Flower dashboard or by checking the Celery task queue. This is distinct from the automated stale order check which runs the same task each minute as part of a cron schedule, intended to align with the expected production-ready, cloud-native configuration with scheduled lambda execution with the same cadence.

### Payment Reference Uniqueness

When testing the API, make sure to use unique payment references for each payment. The system will throw a duplicate error if the same payment reference is used multiple times, simulating prevention of double payment issues. In a production system, this would be handled with idempotency keys and more graceful error handling.

### Code Annotations

Throughout the codebase, you'll find specially marked comments:

- `NOTE:` comments provide explanations about specific pieces of logic
- `TODO:` comments indicate areas planned for future refactoring

These annotations provide insight into the design decisions and future improvements.

### Admin Interface Omission

I have intentionally omitted Django admin paths and configuration to keep the solution lean and aligned with the microservice architecture. Instead, use the shell or API endpoints to interact with the system.

## Production Deployment Considerations

I've included a sample `serverless.yml` file to demonstrate how this Django project might be packaged for serverless deployment. If I had the time, I would've liked to try to bundle and deploy this project to actully validate it in a production-like, serverless environment, where my main experience is deploying in a more typical fashion with docker.

### Serverless Framework Configuration

To bridge the gap between Django and AWS Lambda, we'd need three essential plugins:

- `serverless-wsgi`: Handles the translation between API Gateway and Django's WSGI interface
- `serverless-python-requirements`: Takes care of packaging our Python dependencies correctly
- `serverless-dotenv-plugin`: Manages our environment variables seamlessly

### AWS Serverless Deployment Strategy

In a production environment, we would likely make use of these AWS services:

1. **API Gateway**: Routes incoming HTTP requests
2. **Lambda Functions**: Executes our Django application code
3. **DynamoDB or RDS/Aurora Serverless**: Stores our data
4. **EventBridge**: Manages our auto-rejection scheduling

### Static Files Strategy

For handling static files in production, we would:

1. Set up a dedicated S3 bucket with appropriate public access settings
2. Configure IAM roles allowing Lambda to manage these assets with least privileges principle
3. Use the serverless-wsgi plugin's capabilities to run Django's collectstatic command

### Cost Analysis of Auto-Rejection in Production

The recuring auto-rejection task could be implemented as with EventBridge to execute a Lambda function every minute to check for stale orders. The estimated monthly cost for this component would be low:

- Lambda invocations: ~43,800 per month (every minute) + scheduled invocations exactly 5 minutes after order is placed
- Total estimated cost: ~ less than $1 per month

This negligible cost provides great operational value in ensuring orders are processed in a timely manner. This assumes the service isn't handling a high volume of orders. In that cases, it may be better to remove the per-order scheduled task and rely on a well-tuned recurring job instead, perhaps more frequent that per-minute.

### Authorisation Strategy

All the service endpoints are currently public. Although not implemented in this prototype, production deployment would include:

1. **Token-based authentication** with role-based access control (provided by Django):

   - Customer: Access only to their own orders
   - Restaurant Staff: View all orders, accept/reject capabilities
   - Internal Service: Access to the refunds endpoint

2. **API Gateway custom authorisers** to validate auth tokens before requests reach Lambda functions

3. **VPC configuration** to ensure internal endpoints are not publicly accessible

## Continuous Integration/Deployment

While setting up CI/CD was outside the scope of this challenge, here's how I would approach it at a high level:

### Pipeline & DevOps Overview

1. **Build & Test**

   - Dependency installation (Python + Node.js for Serverless Framework)
   - Unit/integration tests, linting, security scans
   - Infrastructure validation (serverless.yml)

2. **Deploy**

   - Database migrations with rollback capability
   - Lambda deployment with versioning
   - Static assets to S3/CDN
   - Post-deployment health checks

3. **Environment Management**

   - Branch-based: develop → staging → main
   - Environment-specific configs in GitHub/GitLab variables
   - Distinct AWS account setup per environment

4. **Security & Monitoring**
   - IAM role-based deployments
   - Automated security scanning (dependencies, infrastructure)
   - Access and infrastructure logging

## Architectural Decisions

### Why Django?

Django was chosen for this prototype due to my familiarity with it and hence for rapid development. While I fully acknowledged it's not the optimal choice for serverless deployments due to its larger footprint, where libraries like FastAPI and Flask have seen much greater adoption in microservice architectures, it just allowed me to focus on the underlying service design and business logic implementation, and is therefore a more authentic reflection of how I currently build API services. The code patterns used (such as services, selectors, etc.) loosen the coupling with framework-specific code, helping to simplify transitioning to another framework if needed.

With sufficient test coverage covering each of the critical paths, and following TDD principles, we could swap out Django for one of these more lightweight web framework alternatives while ensuring that the service still respects the expected interface for clients, and making it more production-grade and maintainable for serverless, cloud-native deployment environments.

### Relational vs. NoSQL Database

While NoSQL databases like DynamoDB are common in serverless architectures, this application uses a relational database because:

1. Order management is inherently relational
2. Data integrity is critical for payment processing, certainly with order state and payments
3. The schema is well-defined, and in a realistic restaurant system scenario, would likely have a feature roadmap which would make relational data-modelling the more suitable option in the long-term.

## Assumptions Made

Based on the requirements, several assumptions were made during development:

1. There's no need to link specific order items to specific payments
2. An order is considered fully paid once placed, with no need to track payment state
3. Order items are priced and managed by external services
4. Customer and menu item data come from external services
5. The primary concern is functional correctness of the service, not high-scale optimisation, which can be explored as a follow-up
