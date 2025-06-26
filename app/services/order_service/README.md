# Order Service

The Order Service is responsible for managing pharmacy orders, including creation, status updates, cancellation, and retrieval of order information.

## Domain Model

### Order

An order represents a customer's purchase of medications or pharmacy products. It contains:

- Order ID: Unique identifier for the order
- User ID: Customer who placed the order
- Status: Current status of the order (PENDING, CONFIRMED, COMPLETED, CANCELLED)
- Items: List of products ordered, including quantity and price
- Total Amount: Total cost of the order
- Notes: Additional information about the order
- Timestamps: Created, updated, and completed dates

### Order Item

An order item represents a specific product in an order. It contains:

- Product ID: Reference to the product
- Quantity: Number of units ordered
- Price: Unit price at the time of order

## Status Transitions

Orders follow a specific state machine:

- PENDING → CONFIRMED or CANCELLED
- CONFIRMED → COMPLETED or CANCELLED
- COMPLETED → (no further transitions)
- CANCELLED → (no further transitions)

## API Endpoints

- **GET /order/orders**: List all orders
- **POST /order/orders**: Create a new order
- **GET /order/orders/{order_id}**: Get order details
- **PUT /order/orders/{order_id}**: Update order status
- **DELETE /order/orders/{order_id}**: Cancel an order
- **GET /order/user/orders**: Get current user's orders

## Integration with Other Services

The Order Service integrates with:

- **Inventory Service**: To check product availability and adjust stock levels
- **Authentication Service**: To validate user identities and permissions
- **Product Service**: To retrieve product information

## Event Handling

The service publishes and listens for events:

- **OrderCreatedEvent**: When a new order is created
- **OrderStatusChangedEvent**: When order status changes
- **OrderCancelledEvent**: When an order is cancelled
- **OrderCompletedEvent**: When an order is marked as completed

It also listens for:

- **inventory.stock_release_processed**: To update order status after stock changes

## Implementation Notes

The service follows a domain-driven design with:

- Commands for operations (create, update, cancel)
- DTOs for data transfer and API responses
- Domain entities for business logic
- Repository pattern for data access
- Use cases for business operations 