# Domain Model

## Project

### Purpose

### Attributes

### Relationships

### Future Notes

## Marketplace

### Purpose

### Attributes

### Relationships

### Future Notes

## Marketplace Listing

### Purpose

Represents a specific product listing on a marketplace.

A Marketplace Listing is not the product itself.

Different marketplaces may contain different listings for the same product.

Listings store marketplace-specific information while Products represent the normalized business entity.

### Attributes

- ID
- Marketplace ID
- Product ID
- Listing URL
- Marketplace Product ID
- Title
- Price
- Currency
- Seller
- Rating
- Review Count
- Sales Estimate
- Availability
- Created At
- Updated At

### Relationships

Each Marketplace Listing belongs to:

- One Marketplace
- One Product

A Product may have multiple Marketplace Listings.

### Future Notes

Marketplace Listings will be used for competitor analysis, pricing analysis, trend detection, and opportunity discovery.

## Micro Niche

### Purpose

### Attributes

### Relationships

### Future Notes

## Product

### Purpose

### Attributes

### Relationships

### Future Notes

## Supply Source

### Purpose

### Attributes

### Relationships

### Future Notes

## Analysis

### Purpose

### Attributes

### Relationships

### Future Notes

## Trend

### Purpose

### Attributes

### Relationships

### Future Notes

## Opportunity

### Purpose

Represents a business opportunity identified through analytical evaluation of one or more products, suppliers, marketplaces, trends, and business metrics.

An Opportunity is the primary business outcome produced by the platform.

Products are inputs.

Analyses are evidence.

Recommendations are outputs.

The Opportunity connects them into a single investment decision.

### Attributes

- ID
- Title
- Description
- Status
- Opportunity Score
- Confidence Score
- Risk Level
- Estimated Profitability
- Created At
- Updated At

### Relationships

An Opportunity may reference:

- Multiple Products
- Multiple Marketplace Listings
- Multiple Suppliers
- Multiple Analyses
- Multiple Trends
- One Project

### Future Notes

The Opportunity will become the central entity for reports, AI recommendations, dashboards, notifications, automation, and future investment scoring.

## Supplier

### Purpose

### Attributes

### Relationships

### Future Notes

## Brand

### Purpose

### Attributes

### Relationships

### Future Notes

## Country

### Purpose

### Attributes

### Relationships

### Future Notes
