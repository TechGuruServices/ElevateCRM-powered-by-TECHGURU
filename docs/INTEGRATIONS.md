# ElevateCRM Integrations

This document provides an overview of the third-party integrations available in ElevateCRM.

## E-commerce

### Shopify
- **Authentication:** Full OAuth 2.0 flow for app installation and authentication.
- **Webhooks:** Handles `product/create`, `product/update`, `order/create`, and `order/update` webhooks with signature validation and idempotency keys.
- **Sync:** A background service to periodically synchronize products and orders between Shopify and ElevateCRM.

### WooCommerce
- **Authentication:** REST API key-based authentication.
- **Sync:** A pluggable integration module for syncing products and orders.

### Amazon
- **Authentication:** A placeholder adapter is provided with mocked authentication. See the integration's `README.md` for instructions on how to configure real credentials.
- **Sync:** A placeholder adapter with unit tests is available.

## Accounting

### QuickBooks & Xero
- **Authentication:** Stubs for the OAuth 2.0 flow are provided, including token refresh logic.
- **Sync:** Background jobs to push invoices and payments to the accounting platforms. Includes robust retry and idempotency mechanisms.

## Calendar & Email

### Google & Microsoft
- **Authentication:** OAuth 2.0 flow with token refresh logic.
- **Sync:** Webhook/push notification subscription pattern for syncing calendar events. Sample endpoints for sending emails via SMTP or the provider's API.

## Payment Gateways

### Stripe
- **Features:** Full integration with the Stripe SDK, including webhook verification and the Payment Intent flow.
- **Sandbox Mode:** A "sandbox mode" toggle is available for testing.

### PayPal
- **Features:** Integration via the PayPal REST SDK.
- **Sandbox Mode:** A "sandbox mode" toggle is available for testing.
