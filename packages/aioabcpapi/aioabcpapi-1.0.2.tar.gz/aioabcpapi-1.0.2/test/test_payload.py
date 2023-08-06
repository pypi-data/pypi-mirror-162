import asyncio
import logging

from reference_payload import check_reference_payload
from examples.loader import api

logger = logging.getLogger(__name__)


async def test_cp_orders():
    # 1
    data = await api.cp.admin.orders.get_orders_list()
    check_reference_payload(data, 'cp.admin.orders.get_orders_list')

    # 2
    data = await api.cp.admin.orders.get_order(internal_number=1)
    check_reference_payload(data, 'cp.admin.orders.get_order')

    # 3
    data = await api.cp.admin.orders.status_history(1)
    check_reference_payload(data, 'cp.admin.orders.status_history')

    # 4
    # data = await api.cp.admin.orders.create_or_edit_order(internal_number=1,
    #                                                       order_positions={'brand': 'LuK', 'number': '602000600'})
    # check_reference_payload(data, 'cp.admin.orders.create_or_edit_order')
    # # print('Success')
    # # Будем считать, что окей

    # 5
    data = await api.cp.admin.orders.get_online_order_params(position_ids=1)
    check_reference_payload(data, 'cp.admin.orders.get_online_order_params')

    # 6
    data = await api.cp.admin.orders.send_online_order(
        order_params={'comment': 'd', 'shipmentAddress': 'Хуево'},
        positions={'id': 1})
    check_reference_payload(data, 'cp.admin.orders.send_online_order')
    await api.close()


async def test_cp_finance():
    # 1
    data = await api.cp.admin.finance.update_balance(user_id=1, balance=200)
    check_reference_payload(data, 'cp.admin.finance.update_balance')

    # 2
    data = await api.cp.admin.finance.update_credit_limit(user_id=1, credit_limit=200)
    check_reference_payload(data, 'cp.admin.finance.update_credit_limit')

    # 3  update_finance_info
    data = await api.cp.admin.finance.update_finance_info(user_id=1, credit_limit=200)
    check_reference_payload(data, 'cp.admin.finance.update_finance_info')

    # 4 get_payments_info
    data = await api.cp.admin.finance.get_payments_info(user_id=1, payment_number=200)
    check_reference_payload(data, 'cp.admin.finance.get_payments_info')

    # 5 get_payment_links
    data = await api.cp.admin.finance.get_payment_links(user_id=1)
    check_reference_payload(data, 'cp.admin.finance.get_payment_links')

    # 6 get_online_payments
    data = await api.cp.admin.finance.get_online_payments(status_ids=1)
    check_reference_payload(data, 'cp.admin.finance.get_online_payments')

    # 7 add_multiple_payments
    data = await api.cp.admin.finance.add_multiple_payments(payments={'userId': 'd'}, link_payments=False)
    check_reference_payload(data, 'cp.admin.finance.add_multiple_payments')

    # 8 add_single_payment
    data = await api.cp.admin.finance.add_single_payment(
        user_id=1, payment_type_id=1, amount=1, link_payments=False)
    check_reference_payload(data, 'cp.admin.finance.add_single_payment')

    # 9  delete_link_payment
    data = await api.cp.admin.finance.delete_link_payment(payment_link_id=1)
    check_reference_payload(data, 'cp.admin.finance.delete_link_payment')

    # 10  link_existing_payment
    data = await api.cp.admin.finance.link_existing_payment(order_id=1, payment_id=1, amount=1)
    check_reference_payload(data, 'cp.admin.finance.link_existing_payment')

    # 11  refund_payment
    data = await api.cp.admin.finance.refund_payment(refund_amount=1, refund_payment_id=1)
    check_reference_payload(data, 'cp.admin.finance.refund_payment')

    # 12  get_receipts
    data = await api.cp.admin.finance.get_receipts()
    check_reference_payload(data, 'cp.admin.finance.get_receipts')

    # 13  get_payments_methods
    data = await api.cp.admin.finance.get_payments_methods()
    check_reference_payload(data, 'cp.admin.finance.get_payments_methods')

    await api.close()


async def test_cp_users():
    # 1 get_users
    data = await api.cp.admin.users.get_users()
    check_reference_payload(data, 'cp.admin.users.get_users')

    # 2 create
    data = await api.cp.admin.users.create(1, 1, 1, 1)
    check_reference_payload(data, 'cp.admin.users.create')

    # 3 get_profiles
    data = await api.cp.admin.users.get_profiles()
    check_reference_payload(data, 'cp.admin.users.get_profiles')

    # 4 edit_profile
    data = await api.cp.admin.users.edit_profile(1, '1')
    check_reference_payload(data, 'cp.admin.users.edit_profile')

    # 5 edit
    data = await api.cp.admin.users.edit(1)
    check_reference_payload(data, 'cp.admin.users.edit')

    # 6 get_user_shipment_address
    data = await api.cp.admin.users.get_user_shipment_address(1)
    check_reference_payload(data, 'cp.admin.users.get_user_shipment_address')

    # 7 get_updated_cars
    data = await api.cp.admin.users.get_updated_cars()
    check_reference_payload(data, 'cp.admin.users.get_updated_cars')

    # 8 get_sms_settings
    data = await api.cp.admin.users.get_sms_settings(1)
    check_reference_payload(data, 'cp.admin.users.get_sms_settings')


async def test_cp_distributors():
    # 1 get
    data = await api.cp.admin.distributors.get(True)
    check_reference_payload(data, 'cp.admin.distributors.get')

    # 2 edit_status
    data = await api.cp.admin.distributors.edit_status(1, True)
    check_reference_payload(data, 'cp.admin.distributors.edit_status')

    # 3 get_routes
    data = await api.cp.admin.distributors.get_routes(1)
    check_reference_payload(data, 'cp.admin.distributors.get_routes')

    # 4 edit_route
    data = await api.cp.admin.distributors.edit_route(1)
    check_reference_payload(data, 'cp.admin.distributors.edit_route')

    # 5 edit_route_status
    data = await api.cp.admin.distributors.edit_route_status(1, True)
    check_reference_payload(data, 'cp.admin.distributors.edit_route_status')

    # 6 delete_route
    data = await api.cp.admin.distributors.delete_route(1)
    check_reference_payload(data, 'cp.admin.distributors.delete_route')

    # 7  delete_route
    data = await api.cp.admin.distributors.connect_to_office(1, {'id': 1, 'deadline': 1})
    check_reference_payload(data, 'cp.admin.distributors.connect_to_office')

    # 7  delete_route
    data = await api.cp.admin.distributors.connect_to_office(1, {'id': 1, 'deadline': 1})
    check_reference_payload(data, 'cp.admin.distributors.connect_to_office')


async def test_cp_catalog():
    # 1 info
    data = await api.cp.admin.catalog.info('1')
    check_reference_payload(data, 'cp.admin.catalog.info')

    # 2 search
    data = await api.cp.admin.catalog.search('1', {'id': 1})
    check_reference_payload(data, 'cp.admin.catalog.search')
    # 3 info_batch
    data = await api.cp.admin.catalog.info_batch({'id': 1})
    check_reference_payload(data, 'cp.admin.catalog.info_batch')


async def test_client_search():
    # 1
    data = await api.cp.client.search.brands('1', True)
    check_reference_payload(data, 'cp.client.search.brands')

    # 2
    data = await api.cp.client.search.articles('1', 1)
    check_reference_payload(data, 'cp.client.search.articles')

    # 3
    data = await api.cp.client.search.batch({'brand': 0, 'number': 1}, 1)
    check_reference_payload(data, 'cp.client.search.batch')

    # 4
    data = await api.cp.client.search.tips(1, 'ru_RU')
    check_reference_payload(data, 'cp.client.search.tips')

    # 5
    data = await api.cp.client.search.advices(1, 1)
    check_reference_payload(data, 'cp.client.search.advices')

    # 6
    data = await api.cp.client.search.advices_batch(articles=[{"brand": "kyb", "number": "331009"},
                                                              {"brand": "Mobil", "number": "152566"}])
    check_reference_payload(data, 'cp.client.search.advices_batch')


async def test_client_basket():
    # 1
    data = await api.cp.client.basket.add({"brand": "kyb", "number": "331009"})
    check_reference_payload(data, 'cp.client.basket.add')

    # 2
    data = await api.cp.client.basket.clear(1)
    check_reference_payload(data, 'cp.client.basket.clear')

    # 3
    data = await api.cp.client.basket.content(1)
    check_reference_payload(data, 'cp.client.basket.content')

    # 4
    data = await api.cp.client.basket.shipment_offices()
    check_reference_payload(data, 'cp.client.basket.shipment_offices')

    # 5
    data = await api.cp.client.basket.shipment_dates(1, 1)
    check_reference_payload(data, 'cp.client.basket.shipment_dates')

    # 6
    data = await api.cp.client.basket.add_shipment_address('s')
    check_reference_payload(data, 'cp.client.basket.add_shipment_address')


async def test_client_orders():
    # 1
    data = await api.cp.client.orders.order_by_basket()
    check_reference_payload(data, 'cp.client.orders.order_by_basket')

    # 2
    data = await api.cp.client.orders.order_instant(positions={"brand": "kyb", "number": "331009"})
    check_reference_payload(data, 'cp.client.orders.order_instant')

    # 3
    data = await api.cp.client.orders.orders_list(1)
    check_reference_payload(data, 'cp.client.orders.orders_list')

    # 4
    data = await api.cp.client.orders.get_orders()
    check_reference_payload(data, 'cp.client.orders.get_orders')

    # 5
    data = await api.cp.client.orders.cancel_position(1)
    check_reference_payload(data, 'cp.client.orders.cancel_position')


async def test_client_user():
    # 1
    data = await api.cp.client.user.register(1, 2, 3, 4, 5, 6, 7, 8, 9)
    check_reference_payload(data, 'cp.client.user.register')

    # 2
    data = await api.cp.client.user.activate(1, 2)
    check_reference_payload(data, 'cp.client.user.activate')


async def test_client_articles():
    # 1
    data = await api.cp.client.articles.info(1, 1, 'bnhm', 'standard')


async def test_ts_admin_order_pickings():
    # 1
    data = await api.ts.admin.order_pickings.fast_get_out(1, 1, {'id': 1, 'itemCodes': [1, 2, 3]})
    check_reference_payload(data, 'ts.admin.order_pickings.fast_get_out')

    # 2
    data = await api.ts.admin.order_pickings.get()
    check_reference_payload(data, 'ts.admin.order_pickings.get')

    # 3
    data = await api.ts.admin.order_pickings.get_goods(1)
    check_reference_payload(data, 'ts.admin.order_pickings.get_goods')

    # 4
    data = await api.ts.admin.order_pickings.create_by_old_pos(1, 1, 1, 1)
    check_reference_payload(data, 'ts.admin.order_pickings.create_by_old_pos')

    # 5
    data = await api.ts.admin.order_pickings.change_status(1, 1, 1)
    check_reference_payload(data, 'ts.admin.order_pickings.change_status')

    # 6
    data = await api.ts.admin.order_pickings.update(1)
    check_reference_payload(data, 'ts.admin.order_pickings.update')

    # 7
    data = await api.ts.admin.order_pickings.delete(1)
    check_reference_payload(data, 'ts.admin.order_pickings.delete')


async def test_ts_admin_customer_complaints():
    # 1
    data = await api.ts.admin.customer_complaints.get(position_statuses=[1, 2, 3])
    check_reference_payload(data, 'ts.admin.customer_complaints.get')

    # 2
    data = await api.ts.admin.customer_complaints.get_positions(fields="item")
    check_reference_payload(data, 'ts.admin.customer_complaints.get_positions')

    # 3
    data = await api.ts.admin.customer_complaints.create(1, {'id': 1})
    check_reference_payload(data, 'ts.admin.customer_complaints.create')

    # 4
    data = await api.ts.admin.customer_complaints.create_position(1, 2, 4, 3, 5)
    check_reference_payload(data, 'ts.admin.customer_complaints.create_position')

    # 5
    data = await api.ts.admin.customer_complaints.update_position(1, 1)
    check_reference_payload(data, 'ts.admin.customer_complaints.update_position')

    # 6
    data = await api.ts.admin.customer_complaints.change_position_status(1, 1)
    check_reference_payload(data, 'ts.admin.customer_complaints.change_position_status')

    # 7
    data = await api.ts.admin.customer_complaints.update(1, 1)
    check_reference_payload(data, 'ts.admin.customer_complaints.update')


async def test_ts_admin_orders():
    # 1
    data = await api.ts.admin.orders.create(1, fields=["amounts", 'posInfo'])
    check_reference_payload(data, 'ts.admin.orders.create')

    # 2
    data = await api.ts.admin.orders.create_by_cart(client_id=1, agreement_id=1, positions=1, delivery_address='11',
                                                    delivery_person='Персона', delivery_contact='121')
    check_reference_payload(data, 'ts.admin.orders.create_by_cart')

    # 3
    data = await api.ts.admin.orders.orders_list()
    check_reference_payload(data, 'ts.admin.orders.orders_list')

    # 4
    data = await api.ts.admin.orders.get(1)
    check_reference_payload(data, 'ts.admin.orders.get')

    # 5
    data = await api.ts.admin.orders.refuse(1)
    check_reference_payload(data, 'ts.admin.orders.refuse')

    # 6
    data = await api.ts.admin.orders.update(1)
    check_reference_payload(data, 'ts.admin.orders.update')

    # 7
    data = await api.ts.admin.orders.merge(1, 1)
    check_reference_payload(data, 'ts.admin.orders.merge')

    # 8
    data = await api.ts.admin.orders.split(1, 1)
    check_reference_payload(data, 'ts.admin.orders.split')

    # 9
    data = await api.ts.admin.orders.reprice(1, 1)
    check_reference_payload(data, 'ts.admin.orders.reprice')


async def test_ts_admin_cart():
    # 1
    data = await api.ts.admin.cart.create(1, 1, 1, 1, 1, 1, '1')
    check_reference_payload(data, 'ts.admin.cart.create')

    # 2
    data = await api.ts.admin.cart.update(position_id=1, quantity=1, client_id=1)
    check_reference_payload(data, 'ts.admin.cart.update')

    # 3
    data = await api.ts.admin.cart.get_list(1)
    check_reference_payload(data, 'ts.admin.cart.get_list')

    # 4
    data = await api.ts.admin.cart.exist(1, 1, 1, 1)
    check_reference_payload(data, 'ts.admin.cart.exist')

    # 5
    data = await api.ts.admin.cart.summary(1)
    check_reference_payload(data, 'ts.admin.cart.summary')

    # 6
    data = await api.ts.admin.cart.clear(1, 1)
    check_reference_payload(data, 'ts.admin.cart.clear')

    # 7
    data = await api.ts.admin.cart.delete_positions([1, 1, 1], 1)
    check_reference_payload(data, 'ts.admin.cart.delete_positions')

    # 8
    data = await api.ts.admin.cart.transfer(1, 1)
    check_reference_payload(data, 'ts.admin.cart.transfer')


async def test_ts_admin_positions():
    # 1
    data = await api.ts.admin.positions.get(1, ["reserv", "product"])
    check_reference_payload(data, 'ts.admin.positions.get')

    # 2
    data = await api.ts.admin.positions.get_list(customer_complaint_position_ids=1,
                                                 so_position_ids=1,
                                                 route_ids=1,
                                                 distributor_ids=1, ids=1,
                                                 order_ids=1, product_ids=1)
    check_reference_payload(data, 'ts.admin.positions.get_list')

    data = await api.ts.admin.positions.change_status(1, "new")
    # check_reference_payload(data, 'ts.admin.positions.change_status')


async def test_ts_admin_good_receipts():
    # 1
    data = await api.ts.admin.good_receipts.create_position(1, 1, 1, '1', '1', 1, 1)
    check_reference_payload(data, 'ts.admin.good_receipts.create_position')

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    # loop.run_until_complete(test_cp_orders())
    loop.run_until_complete(test_ts_admin_good_receipts())
