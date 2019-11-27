from main import order_lines, orders, customers, items

ins = customers.insert().values(
    first_name='John',
    last_name='Green',
    username='johngreen',
    email='johngreen@gmail.com',
    address='ha noi, Vietnam',
    town='Ha Noi',
)

print(str(ins))
print(ins.compile().params)
