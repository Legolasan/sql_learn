"""
Static dataset for MySQL visualization.
Extended schema for comprehensive SQL learning:
- employees (with manager_id for self-joins)
- departments
- customers
- products
- orders (customer orders)
- order_items (many-to-many: orders <-> products)

Includes strategic NULL values for NULL trap demonstrations.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional
from decimal import Decimal


@dataclass
class Employee:
    id: int
    name: str
    department_id: int
    manager_id: Optional[int]  # NULL for top-level managers (self-join demo)
    salary: float
    hire_date: date
    email: Optional[str]  # Some NULL for NULL trap demos
    phone: Optional[str]  # Some NULL for NULL trap demos


@dataclass
class Department:
    id: int
    name: str
    budget: float
    location: Optional[str]  # Some NULL


@dataclass
class Customer:
    id: int
    name: str
    email: str
    city: Optional[str]  # Some NULL for NULL demos
    country: str
    credit_limit: Optional[float]  # Some NULL
    created_at: datetime


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    stock_quantity: int
    weight: Optional[float]  # Some NULL (digital products have no weight)
    is_active: bool


@dataclass
class Order:
    id: int
    customer_id: int
    employee_id: int  # Sales rep who made the sale
    order_date: date
    shipped_date: Optional[date]  # NULL if not yet shipped
    status: str  # 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    notes: Optional[str]


@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float  # Price at time of order (may differ from product.price)
    discount: Optional[float]  # NULL means no discount


class Dataset:
    """Static dataset containing all tables."""

    def __init__(self):
        self.departments = self._create_departments()
        self.employees = self._create_employees()
        self.customers = self._create_customers()
        self.products = self._create_products()
        self.orders = self._create_orders()
        self.order_items = self._create_order_items()

        # Create indexes for visualization
        self.indexes = {
            'employees': {
                'PRIMARY': ('id', [e.id for e in self.employees]),
                'idx_salary': ('salary', sorted([e.salary for e in self.employees])),
                'idx_department': ('department_id', sorted([e.department_id for e in self.employees])),
                'idx_manager': ('manager_id', sorted([e.manager_id for e in self.employees if e.manager_id])),
            },
            'departments': {
                'PRIMARY': ('id', [d.id for d in self.departments]),
            },
            'customers': {
                'PRIMARY': ('id', [c.id for c in self.customers]),
                'idx_country': ('country', sorted([c.country for c in self.customers])),
            },
            'products': {
                'PRIMARY': ('id', [p.id for p in self.products]),
                'idx_category': ('category', sorted([p.category for p in self.products])),
            },
            'orders': {
                'PRIMARY': ('id', [o.id for o in self.orders]),
                'idx_customer': ('customer_id', sorted([o.customer_id for o in self.orders])),
                'idx_employee': ('employee_id', sorted([o.employee_id for o in self.orders])),
                'idx_status': ('status', sorted([o.status for o in self.orders])),
            },
            'order_items': {
                'PRIMARY': ('id', [oi.id for oi in self.order_items]),
                'idx_order': ('order_id', sorted([oi.order_id for oi in self.order_items])),
                'idx_product': ('product_id', sorted([oi.product_id for oi in self.order_items])),
            }
        }

    def _create_departments(self) -> list[Department]:
        return [
            Department(1, "Engineering", 500000, "Building A, Floor 3"),
            Department(2, "Sales", 300000, "Building B, Floor 1"),
            Department(3, "Marketing", 200000, "Building B, Floor 2"),
            Department(4, "HR", 150000, None),  # NULL location
            Department(5, "Finance", 250000, "Building A, Floor 1"),
            Department(6, "Research", 400000, None),  # NULL location - no employees yet
        ]

    def _create_employees(self) -> list[Employee]:
        return [
            # Engineering (dept 1) - Eva is the VP
            Employee(1, "Alice Chen", 1, 5, 95000, date(2020, 3, 15), "alice@company.com", "555-0101"),
            Employee(2, "Bob Smith", 1, 5, 85000, date(2021, 6, 1), "bob@company.com", "555-0102"),
            Employee(3, "Carol Davis", 1, 5, 110000, date(2019, 1, 10), "carol@company.com", None),  # NULL phone
            Employee(4, "David Lee", 1, 3, 75000, date(2022, 8, 20), "david@company.com", "555-0104"),
            Employee(5, "Eva Martinez", 1, None, 125000, date(2018, 5, 5), "eva@company.com", "555-0105"),  # VP - no manager

            # Sales (dept 2) - Ivy is manager
            Employee(6, "Frank Wilson", 2, 9, 65000, date(2021, 2, 14), "frank@company.com", "555-0106"),
            Employee(7, "Grace Kim", 2, 9, 72000, date(2020, 11, 30), "grace@company.com", "555-0107"),
            Employee(8, "Henry Brown", 2, 9, 58000, date(2022, 4, 18), None, "555-0108"),  # NULL email
            Employee(9, "Ivy Taylor", 2, None, 80000, date(2019, 9, 22), "ivy@company.com", "555-0109"),  # Manager - no manager
            Employee(10, "Jack Anderson", 2, 9, 68000, date(2021, 7, 7), "jack@company.com", None),  # NULL phone

            # Marketing (dept 3) - Maria is manager
            Employee(11, "Karen White", 3, 13, 62000, date(2020, 6, 12), "karen@company.com", "555-0111"),
            Employee(12, "Leo Garcia", 3, 13, 55000, date(2022, 1, 25), "leo@company.com", "555-0112"),
            Employee(13, "Maria Rodriguez", 3, None, 70000, date(2019, 4, 3), "maria@company.com", "555-0113"),  # Manager
            Employee(14, "Nathan Clark", 3, 13, 48000, date(2023, 2, 8), None, None),  # NULL email AND phone - new hire

            # HR (dept 4) - Olivia is manager
            Employee(15, "Olivia Moore", 4, None, 52000, date(2021, 10, 5), "olivia@company.com", "555-0115"),  # Manager
            Employee(16, "Peter Hall", 4, 15, 58000, date(2020, 8, 17), "peter@company.com", "555-0116"),
            Employee(17, "Quinn Adams", 4, 15, 45000, date(2022, 12, 1), "quinn@company.com", "555-0117"),

            # Finance (dept 5) - Tina is manager
            Employee(18, "Rachel Scott", 5, 20, 78000, date(2019, 7, 14), "rachel@company.com", "555-0118"),
            Employee(19, "Sam Turner", 5, 20, 85000, date(2020, 3, 28), "sam@company.com", "555-0119"),
            Employee(20, "Tina Phillips", 5, None, 92000, date(2018, 11, 9), "tina@company.com", "555-0120"),  # Manager
        ]

    def _create_customers(self) -> list[Customer]:
        return [
            Customer(1, "Acme Corp", "orders@acme.com", "New York", "USA", 50000, datetime(2022, 1, 15, 10, 30)),
            Customer(2, "TechStart Inc", "purchasing@techstart.io", "San Francisco", "USA", 25000, datetime(2022, 3, 22, 14, 45)),
            Customer(3, "Global Trade Ltd", "procurement@globaltrade.co.uk", "London", "UK", 75000, datetime(2021, 11, 8, 9, 0)),
            Customer(4, "DataDriven GmbH", "einkauf@datadriven.de", None, "Germany", 30000, datetime(2022, 6, 1, 11, 15)),  # NULL city
            Customer(5, "CloudNine Solutions", "admin@cloudnine.com", "Toronto", "Canada", None, datetime(2023, 2, 14, 16, 30)),  # NULL credit_limit
            Customer(6, "StartUp Ventures", "hello@startupventures.com", "Austin", "USA", 10000, datetime(2023, 5, 20, 8, 45)),
            Customer(7, "Enterprise Systems", "orders@enterprise-sys.com", None, "USA", 100000, datetime(2020, 8, 12, 13, 0)),  # NULL city
            Customer(8, "SmallBiz Co", "contact@smallbiz.com", "Chicago", "USA", None, datetime(2023, 7, 1, 10, 0)),  # NULL credit_limit
            Customer(9, "Innovation Labs", "procurement@innovlabs.com", "Seattle", "USA", 45000, datetime(2022, 9, 5, 15, 30)),
            Customer(10, "Mega Industries", "purchasing@megaind.com", "Detroit", "USA", 200000, datetime(2019, 4, 18, 9, 30)),
        ]

    def _create_products(self) -> list[Product]:
        return [
            # Software (digital - NULL weight)
            Product(1, "Basic License", "Software", 299.99, 1000, None, True),
            Product(2, "Professional License", "Software", 599.99, 500, None, True),
            Product(3, "Enterprise License", "Software", 1499.99, 200, None, True),
            Product(4, "Premium Add-on", "Software", 199.99, 800, None, True),
            Product(5, "Support Package (1yr)", "Service", 499.99, 999, None, True),

            # Hardware
            Product(6, "USB Security Key", "Hardware", 49.99, 500, 0.05, True),
            Product(7, "Hardware Token", "Hardware", 79.99, 300, 0.08, True),
            Product(8, "Server Appliance", "Hardware", 2999.99, 50, 15.5, True),

            # Training
            Product(9, "Training Bundle", "Training", 999.99, 100, None, True),  # Virtual training
            Product(10, "Certification Exam", "Training", 299.99, 999, None, True),

            # Discontinued
            Product(11, "Legacy Module", "Software", 199.99, 0, None, False),  # Inactive
            Product(12, "Old Hardware Key", "Hardware", 29.99, 25, 0.03, False),  # Inactive
        ]

    def _create_orders(self) -> list[Order]:
        return [
            # Mix of statuses, some NULL shipped_date
            Order(1, 1, 6, date(2023, 1, 15), date(2023, 1, 18), "delivered", None),
            Order(2, 2, 7, date(2023, 2, 20), date(2023, 2, 25), "delivered", "Rush order"),
            Order(3, 1, 9, date(2023, 3, 10), date(2023, 3, 15), "delivered", None),
            Order(4, 3, 6, date(2023, 3, 25), date(2023, 4, 1), "delivered", "International shipping"),
            Order(5, 4, 10, date(2023, 4, 5), date(2023, 4, 8), "delivered", None),
            Order(6, 5, 8, date(2023, 4, 18), date(2023, 4, 22), "delivered", None),
            Order(7, 2, 7, date(2023, 5, 8), date(2023, 5, 12), "shipped", None),
            Order(8, 6, 9, date(2023, 5, 22), None, "processing", "Pending payment verification"),  # NULL shipped_date
            Order(9, 7, 6, date(2023, 6, 3), date(2023, 6, 5), "delivered", None),
            Order(10, 1, 10, date(2023, 6, 15), date(2023, 6, 18), "delivered", "Repeat customer discount applied"),
            Order(11, 8, 7, date(2023, 7, 1), None, "pending", None),  # NULL shipped_date
            Order(12, 9, 8, date(2023, 7, 20), date(2023, 7, 25), "shipped", None),
            Order(13, 10, 9, date(2023, 8, 5), date(2023, 8, 8), "delivered", "VIP customer"),
            Order(14, 3, 6, date(2023, 8, 18), None, "cancelled", "Customer requested cancellation"),  # Cancelled
            Order(15, 4, 10, date(2023, 9, 2), None, "processing", None),  # NULL shipped_date
        ]

    def _create_order_items(self) -> list[OrderItem]:
        return [
            # Order 1 - Acme Corp
            OrderItem(1, 1, 3, 5, 1499.99, 0.10),  # 5 Enterprise Licenses with 10% discount
            OrderItem(2, 1, 5, 5, 499.99, None),    # 5 Support Packages, no discount

            # Order 2 - TechStart
            OrderItem(3, 2, 2, 10, 599.99, 0.05),   # 10 Professional
            OrderItem(4, 2, 9, 2, 999.99, None),    # 2 Training Bundles

            # Order 3 - Acme Corp (repeat)
            OrderItem(5, 3, 4, 5, 199.99, None),    # 5 Premium Add-ons

            # Order 4 - Global Trade
            OrderItem(6, 4, 3, 20, 1499.99, 0.15),  # 20 Enterprise with 15% discount
            OrderItem(7, 4, 8, 2, 2999.99, 0.10),   # 2 Server Appliances
            OrderItem(8, 4, 6, 100, 49.99, 0.20),   # 100 USB Keys with 20% discount

            # Order 5 - DataDriven
            OrderItem(9, 5, 1, 25, 299.99, 0.05),   # 25 Basic Licenses
            OrderItem(10, 5, 5, 10, 499.99, 0.05),  # 10 Support Packages

            # Order 6 - CloudNine
            OrderItem(11, 6, 2, 5, 599.99, None),   # 5 Professional

            # Order 7 - TechStart (repeat)
            OrderItem(12, 7, 4, 10, 199.99, 0.10),  # 10 Premium Add-ons
            OrderItem(13, 7, 7, 20, 79.99, None),   # 20 Hardware Tokens

            # Order 8 - StartUp Ventures
            OrderItem(14, 8, 1, 5, 299.99, None),   # 5 Basic Licenses

            # Order 9 - Enterprise Systems
            OrderItem(15, 9, 3, 50, 1499.99, 0.20), # 50 Enterprise with 20% discount
            OrderItem(16, 9, 5, 50, 499.99, 0.15), # 50 Support Packages
            OrderItem(17, 9, 8, 5, 2999.99, 0.10), # 5 Server Appliances

            # Order 10 - Acme Corp
            OrderItem(18, 10, 10, 10, 299.99, 0.10), # 10 Certification Exams

            # Order 11 - SmallBiz
            OrderItem(19, 11, 1, 3, 299.99, None),   # 3 Basic Licenses

            # Order 12 - Innovation Labs
            OrderItem(20, 12, 2, 15, 599.99, 0.10),  # 15 Professional
            OrderItem(21, 12, 6, 50, 49.99, 0.05),   # 50 USB Keys

            # Order 13 - Mega Industries (VIP)
            OrderItem(22, 13, 3, 100, 1499.99, 0.25), # 100 Enterprise with 25% discount
            OrderItem(23, 13, 8, 10, 2999.99, 0.15),  # 10 Server Appliances
            OrderItem(24, 13, 5, 100, 499.99, 0.20),  # 100 Support Packages

            # Order 14 - Global Trade (cancelled - still has items for demo)
            OrderItem(25, 14, 3, 5, 1499.99, None),

            # Order 15 - DataDriven
            OrderItem(26, 15, 4, 20, 199.99, 0.10),   # 20 Premium Add-ons
        ]

    def get_table(self, name: str) -> list[Any]:
        """Get a table by name."""
        tables = {
            'employees': self.employees,
            'departments': self.departments,
            'customers': self.customers,
            'products': self.products,
            'orders': self.orders,
            'order_items': self.order_items,
        }
        return tables.get(name.lower(), [])

    def get_table_columns(self, name: str) -> list[str]:
        """Get column names for a table."""
        columns = {
            'employees': ['id', 'name', 'department_id', 'manager_id', 'salary', 'hire_date', 'email', 'phone'],
            'departments': ['id', 'name', 'budget', 'location'],
            'customers': ['id', 'name', 'email', 'city', 'country', 'credit_limit', 'created_at'],
            'products': ['id', 'name', 'category', 'price', 'stock_quantity', 'weight', 'is_active'],
            'orders': ['id', 'customer_id', 'employee_id', 'order_date', 'shipped_date', 'status', 'notes'],
            'order_items': ['id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount'],
        }
        return columns.get(name.lower(), [])

    def get_schema_info(self) -> dict:
        """Get schema information for documentation."""
        return {
            'tables': {
                'employees': {
                    'description': 'Company employees with department and manager references',
                    'columns': self.get_table_columns('employees'),
                    'pk': 'id',
                    'fk': {'department_id': 'departments.id', 'manager_id': 'employees.id'},
                    'row_count': len(self.employees)
                },
                'departments': {
                    'description': 'Company departments',
                    'columns': self.get_table_columns('departments'),
                    'pk': 'id',
                    'fk': {},
                    'row_count': len(self.departments)
                },
                'customers': {
                    'description': 'Customer accounts',
                    'columns': self.get_table_columns('customers'),
                    'pk': 'id',
                    'fk': {},
                    'row_count': len(self.customers)
                },
                'products': {
                    'description': 'Products and services catalog',
                    'columns': self.get_table_columns('products'),
                    'pk': 'id',
                    'fk': {},
                    'row_count': len(self.products)
                },
                'orders': {
                    'description': 'Customer orders',
                    'columns': self.get_table_columns('orders'),
                    'pk': 'id',
                    'fk': {'customer_id': 'customers.id', 'employee_id': 'employees.id'},
                    'row_count': len(self.orders)
                },
                'order_items': {
                    'description': 'Line items for each order (many-to-many)',
                    'columns': self.get_table_columns('order_items'),
                    'pk': 'id',
                    'fk': {'order_id': 'orders.id', 'product_id': 'products.id'},
                    'row_count': len(self.order_items)
                },
            },
            'relationships': [
                {'type': 'one-to-many', 'from': 'departments', 'to': 'employees', 'via': 'department_id'},
                {'type': 'one-to-many', 'from': 'employees', 'to': 'employees', 'via': 'manager_id', 'note': 'Self-join for hierarchy'},
                {'type': 'one-to-many', 'from': 'customers', 'to': 'orders', 'via': 'customer_id'},
                {'type': 'one-to-many', 'from': 'employees', 'to': 'orders', 'via': 'employee_id'},
                {'type': 'many-to-many', 'from': 'orders', 'to': 'products', 'via': 'order_items'},
            ]
        }


# Singleton dataset
_dataset: Dataset | None = None


def get_dataset() -> Dataset:
    """Get the global dataset instance."""
    global _dataset
    if _dataset is None:
        _dataset = Dataset()
    return _dataset
