# Stock Check Unit Tests

This document explains the unit tests implemented for the stock check functionality in the Pharmacy Management System.

## Overview

The stock check system validates product availability based on several criteria:
- Current stock quantity
- Minimum stock levels
- Product expiration date
- Product status (active/inactive)

The tests ensure that all validation scenarios are correctly handled and produce the expected results.

## Test Structure

### 1. TestStockValidation

Tests the direct validation logic in the `InventoryEntity.validate_stock_request` method:

- **test_validate_available_stock**: Product has sufficient stock with no warnings
- **test_validate_low_stock**: Stock would fall below minimum level after order
- **test_validate_insufficient_stock**: Requested quantity exceeds available stock
- **test_validate_out_of_stock**: Product has zero quantity
- **test_validate_expired_product**: Product is expired
- **test_validate_expiring_soon**: Product will expire within 90 days
- **test_validate_inactive_product**: Product is inactive
- **test_product_both_low_stock_and_expiring_soon**: Product has both low stock and expiring soon conditions

### 2. TestStockCheckUseCase

Tests the `StockCheckUseCase` which orchestrates the stock check process:

- **test_execute_with_available_product**: Checking available product works correctly
- **test_execute_with_insufficient_stock**: Correctly identifies insufficient stock
- **test_execute_with_nonexistent_product**: Properly handles nonexistent products
- **test_execute_with_multiple_items**: Handles multiple items with different statuses
- **test_low_stock_and_expiring_separately**: Verifies that low stock and expiring soon are reported as separate statuses in different products
- **test_product_both_low_stock_and_expiring_soon**: Tests a product with both low stock and expiring soon conditions

## Validation Logic

The stock validation logic checks various conditions in the following sequence:

1. **Product Status**: If product is inactive, return `INACTIVE` status
2. **Expiration Check**: If product is expired, return `EXPIRED` status
3. **Zero Stock**: If quantity is zero, return `OUT_OF_STOCK` status
4. **Insufficient Stock**: If requested quantity exceeds available stock, return `INSUFFICIENT_STOCK` status
5. **Low Stock Warning**: If remaining stock falls below minimum level, return `LOW_STOCK` status
6. **Expiring Soon Warning**: If product expires within 90 days, return `EXPIRING_SOON` status
7. **Available**: If none of the above, return `AVAILABLE` status

### Multiple Conditions Handling

When a product has multiple warning conditions (e.g., both low stock and expiring soon), the system prioritizes one status over the other based on the order of checks. The warnings for both conditions are still included in the response, so the user is aware of all potential issues.

In the current implementation:
- If a product is both low on stock and expiring soon, the status will be whichever check happens first in the validation sequence
- Both warning messages are included in the response
- No combined status is used or needed, as the warnings array provides full visibility of all issues

## Test Fixtures

The tests utilize several fixtures:

- **product_id**: Generates a unique UUID for testing
- **base_product**: Creates a standard product entity for testing
- **base_inventory**: Creates a standard inventory entity with 100 units of stock
- **mock_uow**: Creates a mock Unit of Work with the base product and inventory

## MockUnitOfWork

A simplified mock implementation of the Unit of Work pattern that:

1. Stores products and inventory items in dictionaries
2. Provides property access to product and inventory repositories
3. Implements the necessary methods used by the StockCheckUseCase

## Running the Tests

These tests can be run using pytest:

```bash
pytest app/services/inventory_service/tests/unit/test_stock_check.py -v
```

Add the `-v` flag for verbose output that shows each test name. 