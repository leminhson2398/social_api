from sqlalchemy import create_engine, MetaData, Table, String, Column, \
    Text, DateTime, Integer, Numeric, CheckConstraint, ForeignKey, \
    insert as dbInsert, select
from datetime import datetime
from sqlalchemy.engine import Engine, Connection, ResultProxy
import typing


# create database engine:
engine: Engine = create_engine(
    "postgresql+psycopg2://minh:anhyeuem98@localhost/social_api"
)

# create metadata, used to hold table information, manage tables.
metadata = MetaData()

# create table:
customers: Table = Table(
    'customers',
    metadata,
    Column('id', Integer(), primary_key=True),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('username', String(50), nullable=False),
    Column('email', String(200), nullable=False),
    Column('address', String(50), nullable=False),
    Column('town', String(50), nullable=False),
    Column('created_on', DateTime(), default=datetime.utcnow),
    Column('updated_on', DateTime(),
           default=datetime.utcnow, onupdate=datetime.utcnow)
)

items: Table = Table(
    'items',
    metadata,
    Column('id', Integer(), primary_key=True),
    Column('name', String(200), nullable=False),
    Column('cost_price', Numeric(10, 2), nullable=False),
    Column('selling_price', Numeric(10, 2), nullable=False),
    Column('quantity', Integer(), nullable=False),
    CheckConstraint('quantity > 0', name='quantity_check')
)

orders: Table = Table(
    'orders',
    metadata,
    Column('id', Integer(), primary_key=True),
    Column('customer_id', ForeignKey('customers.id')),
    Column('date_placed', DateTime(), default=datetime.utcnow),
    Column('date_shipped', DateTime())
)

order_lines: Table = Table(
    'order_lines',
    metadata,
    Column('id', Integer(), primary_key=True),
    Column('order_id', ForeignKey('orders.id')),
    Column('item_id', ForeignKey('items.id')),
    Column('quantity', Integer())
)


def create_all() -> None:
    if not metadata.is_bound():
        metadata.create_all(bind=engine)


def insert(insert) -> ResultProxy:
    result = con.execute(insert)
    return result


if __name__ == "__main__":
    create_all()

    con: Connection = engine.connect()

    item_ins = dbInsert(items)
    order_line_ins = dbInsert(order_lines)
    order_ins = dbInsert(orders)

    item_list: typing.List[dict] = [
        {
            "name": "Chair",
            "cost_price": 9.21,
            "selling_price": 10.81,
            "quantity": 5
        },
        {
            "name": "Pen",
            "cost_price": 3.45,
            "selling_price": 4.51,
            "quantity": 3
        },
        {
            "name": "Headphone",
            "cost_price": 15.52,
            "selling_price": 16.81,
            "quantity": 50
        },
        {
            "name": "Travel Bag",
            "cost_price": 20.1,
            "selling_price": 24.21,
            "quantity": 50
        },
        {
            "name": "Keyboard",
            "cost_price": 20.12,
            "selling_price": 22.11,
            "quantity": 50
        },
        {
            "name": "Monitor",
            "cost_price": 200.14,
            "selling_price": 212.89,
            "quantity": 50
        },
        {
            "name": "Watch",
            "cost_price": 100.58,
            "selling_price": 104.41,
            "quantity": 50
        },
        {
            "name": "Water Bottle",
            "cost_price": 20.89,
            "selling_price": 25.00,
            "quantity": 50
        },
    ]

    order_list: typing.List[dict] = [
        {
            "customer_id": 1
        },
        {
            "customer_id": 1
        }
    ]

    order_line_list: typing.List[dict] = [
        {
            "order_id": 1,
            "item_id": 1,
            "quantity": 5
        },
        {
            "order_id": 1,
            "item_id": 2,
            "quantity": 2
        },
        {
            "order_id": 1,
            "item_id": 3,
            "quantity": 1
        },
        {
            "order_id": 2,
            "item_id": 1,
            "quantity": 5
        },
        {
            "order_id": 2,
            "item_id": 2,
            "quantity": 5
        },
    ]

    s = select([
        items.c.name,
        items.c.quantity,
        (items.c.selling_price * 5).label('price')
    ]).where(
        items.c.quantity == 50
    )

    print(s)

    r: ResultProxy = con.execute(s)

    # print(r.keys())

    for row in r:
        print(row.price)
