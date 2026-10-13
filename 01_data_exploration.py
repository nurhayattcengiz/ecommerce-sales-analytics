
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Project directory
project_dir = Path(__file__).resolve().parent


# Load orders dataset
orders = pd.read_csv(
    project_dir / "data" / "olist_orders_dataset.csv"
)

print("\nORDERS DATASET")
print(orders.head())
print("Dataset shape:", orders.shape)


# Data quality checks
print("\nCOLUMN INFORMATION")
orders.info()

print("\nMISSING VALUES")
print(orders.isnull().sum())

print("\nDUPLICATE ROWS")
print(orders.duplicated().sum())


# Order status analysis
print("\nORDER STATUS DISTRIBUTION")
print(orders["order_status"].value_counts())


# Missing delivery dates by order status
missing_delivery = orders[
    orders["order_delivered_customer_date"].isna()
]

print("\nMISSING DELIVERY DATES BY STATUS")
print(missing_delivery["order_status"].value_counts())


# Convert date columns
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column], errors="coerce"
    )


# Filter delivered orders
delivered_orders = orders[
    orders["order_status"] == "delivered"
].copy()

print("\nDELIVERED ORDERS")
print("Total delivered orders:", len(delivered_orders))

print(
    "Missing delivery dates:",
    delivered_orders["order_delivered_customer_date"].isna().sum()
)


# Load order items dataset
order_items = pd.read_csv(
    project_dir / "data" / "olist_order_items_dataset.csv"
)

print("\nORDER ITEMS DATASET")
print(order_items.head())
print("Dataset shape:", order_items.shape)


# Product price summary
print("\nPRICE SUMMARY")
print(order_items["price"].describe())


# Merge delivered orders with order items
sales = pd.merge(
    delivered_orders,
    order_items,
    on="order_id",
    how="inner",
    validate="one_to_many"
)

print("\nMERGED SALES DATASET")
print("Total item rows:", len(sales))
print("Unique orders:", sales["order_id"].nunique())

print("\nFIRST FIVE ROWS")
print(sales[["order_id", "price", "freight_value"]].head())


# Calculate sales KPIs
total_sales = sales["price"].sum()
total_orders = sales["order_id"].nunique()
average_order_value = total_sales / total_orders

print("\nSALES KPIs")
print(f"Total Product Sales: R$ {total_sales:,.2f}")
print(f"Total Orders: {total_orders:,}")
print(f"Average Order Value: R$ {average_order_value:,.2f}")


# Monthly product sales
sales["order_month"] = (
    sales["order_purchase_timestamp"].dt.to_period("M")
)

monthly_sales = (
    sales.groupby("order_month")["price"]
    .sum()
    .sort_index()
)

print("\nMONTHLY PRODUCT SALES")
print(monthly_sales)


# Create output directory
output_dir = project_dir / "outputs"
output_dir.mkdir(exist_ok=True)


# Monthly sales chart
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    monthly_sales.index.astype(str),
    monthly_sales.values,
    marker="o",
    linewidth=2
)

ax.set_title("Monthly Product Sales", fontsize=15)
ax.set_xlabel("Order Month")
ax.set_ylabel("Product Sales (BRL)")

ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()


# Save chart
plt.savefig(
    output_dir / "monthly_sales.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# Load customer data
customers = pd.read_csv(
    project_dir / "data" / "olist_customers_dataset.csv"
)

print("\nCUSTOMERS DATASET")
print(customers.shape)
print(customers.head())


# Merge sales with customer locations
sales_customers = pd.merge(
    sales,
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left",
    validate="many_to_one"
)

print("\nMISSING CUSTOMER STATES")
print(sales_customers["customer_state"].isna().sum())


# Product sales by customer state
state_sales = (
    sales_customers.groupby("customer_state")["price"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTOP 10 STATES BY PRODUCT SALES")
print(state_sales.head(10))



# Top 10 states by product sales
top_states = state_sales.head(10).sort_values()

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    top_states.index,
    top_states.values,
    color="#2563A6"
)

ax.set_title("Top 10 States by Product Sales", fontsize=15)
ax.set_xlabel("Product Sales (BRL)")
ax.set_ylabel("Customer State")

ax.grid(axis="x", alpha=0.2)
ax.set_axisbelow(True)

ax.bar_label(
    bars,
    labels=[f"{value / 1_000_000:.2f}M" for value in top_states.values],
    padding=4,
    fontsize=9
)

ax.set_xlim(0, top_states.max() * 1.15)

plt.tight_layout()

plt.savefig(
    output_dir / "top_10_states.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()



# Load product information
products = pd.read_csv(
    project_dir / "data" / "olist_products_dataset.csv"
)

categories = pd.read_csv(
    project_dir / "data" / "product_category_name_translation.csv"
)


# Add product categories to sales data
sales_products = sales.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left",
    validate="many_to_one"
)


# Translate category names into English
sales_products = sales_products.merge(
    categories,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)


# Sales by product category
category_sales = (
    sales_products.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTOP 10 PRODUCT CATEGORIES")
print(category_sales.head(10))

print("\nMISSING CATEGORY LABELS")
print(sales_products["product_category_name_english"].isna().sum())


# Include products without category labels
sales_products["category"] = (
    sales_products["product_category_name_english"]
    .fillna("Unknown")
)

category_sales_complete = (
    sales_products.groupby("category")["price"]
    .sum()
    .sort_values(ascending=False)
)

# Top 10 product categories
top_categories = (
    category_sales_complete.head(10).sort_values()
)

fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.barh(
    top_categories.index,
    top_categories.values,
    color="#2563A6"
)

ax.set_title("Top 10 Product Categories by Sales", fontsize=15)
ax.set_xlabel("Product Sales (BRL)")
ax.set_ylabel("Product Category")
ax.grid(axis="x", alpha=0.2)
ax.set_axisbelow(True)

ax.bar_label(
    bars,
    labels=[f"{v / 1_000_000:.2f}M" for v in top_categories.values],
    padding=4
)

ax.set_xlim(0, top_categories.max() * 1.15)

plt.tight_layout()

plt.savefig(
    output_dir / "top_10_categories.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
