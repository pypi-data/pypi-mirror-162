import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from market_place_cli.v_cloud_market_cli_common.service.market_service import MarketService
from market_place_cli.v_cloud_market_cli_common.service.order_service import OrderService
from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service_display.order_service_display import OrderServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_request.order_service_request import OrderRequest
from market_place_cli.service_interface_request.common_request import get_table_choice


class OrderServiceLogic:

    def __init__(self):
        self.title = 'OrderService'
        self.console = None
        self.od = None  # order display instance
        self.net_type = 'M'
        self.wr = None
        self.nonce = 0
        self.order_req = None
        self.order_service = None
        self.main_functions = ['Show Pending Order', 'Show Paid Order', 'Show Filed Order',
                               'Show Order Detail', 'Pay An Order']
        self.password = None

    @property
    def Name(self):
        return self.title

    def StartLogic(self, console: Console, is_testnet: bool):
        self.console = console
        self.wr = WalletRequest(self.console)
        self.order_req = OrderRequest(self.console)
        self.net_type = get_net(is_testnet)
        self.od = OrderServiceDisplay(self.console)
        self.nonce = self.wr.get_payment_address()
        if wallet_has_password(self.net_type):
            self.password = self.wr.get_password()
        self.order_service = OrderService(self.net_type, self.password, self.nonce)
        console.clear()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                self.show_pending_order_logic()
            elif choice == '2':
                self.show_paid_order_logic()
            elif choice == '3':
                self.show_filed_order_logic()
            elif choice == '4':
                self.show_order_detail_logic()
            elif choice == '5':
                self.pay_order_logic()
            elif choice.lower() == 'b':
                break

    def show_pending_order_logic(self):
        self.show_order_page(status='OrderPending')

    def show_paid_order_logic(self):
        self.show_order_page(status='OrderPaid')

    def show_filed_order_logic(self):
        self.show_order_page(status='OrderFiled')

    def show_order_detail_logic(self, order_id: str = ''):
        if not order_id:
            order_id = self.order_req.get_order_id()
        try:
            info = self.order_service.query_order_info(order_id)
            self.od.display_order_info(info)
        except Exception as e:
            self.console.print(e)
            self.console.input('Press ENTER to continue...')

    def show_order_page(self, status: str):
        cur = 1
        page_size = 10

        title = self._construct_page_title(status)
        extra = self._construct_page_button(status)
        while True:
            try:
                display_result = self._construct_order_page_data(self.order_service, cur, status)
            except Exception as e:
                self.console.print(e)
                self.console.input('Press ENTER to continue...')
                return
            w = self.od.display_order_page(title, display_result)
            order_list = display_result['list']
            has_next = len(order_list) >= page_size or len(order_list) >= page_size

            choice = get_table_choice(self.console, w, has_next, extra=extra)
            # consider that order status takes some time to update, add refresh option
            if choice == 'r':
                continue
            if choice == 'p' and cur > 1:
                cur -= 1
            elif choice == 'n' and has_next:
                cur += 1
            elif choice == 's':
                target_order_id = self.get_id_by_index(order_list)
                if target_order_id:
                    self.show_order_detail_logic(target_order_id)
            elif choice == 'm' and status == 'OrderPending' :
                target_order_id = self.get_id_by_index(order_list)
                if target_order_id:
                    self.pay_order_logic(target_order_id)
            elif choice == 'e':
                break
    
    def get_id_by_index(self, order_list: list = []): 
        while len(order_list) > 0:
            index = IntPrompt.ask('[bright_green]Please enter the Order INDEX')
            if index < 0 or index > len(order_list) - 1:
                self.console.print('[bright_red]Index out of range.')
                continue
            order_id = order_list[index]['id']
            return order_id

    def pay_order_logic(self, order_id: str = ''):
        if not order_id:
            order_id = self.order_req.get_order_id()
        amt = self.wr.get_amount()
        if amt < 0:
            self.console.print('[bright_red]!!! Invalid Amount !!!')
            self.console.input('Press ENTER to exit...')
            return
        try:
            wsd = WalletServiceDisplay(self.console)
            ws = WalletService(wsd, self.net_type, self.password)
            pubKey = ws.fetch_wallet_info(self.nonce, 'pub')
            order_info = self.order_service.query_order_info(order_id)
            recipient = order_info['recipient']
            amt = self._overpay_protection(order_info, amt)
            if not amt:
                return
            ws.account_pay(self.nonce, recipient, amt, order_id + ';' + pubKey)
        except Exception as e:
            self.console.print(e)
            self.console.input('[bright_red]Failed to pay for order !!!')
        # mock payment code for local testing
        # resp = order_service.mock_order_payment(order_id, recipient, pubKey, amt)
        # self.console.print(Panel.fit(resp["content"]))

    def _construct_order_page_data(self, o: OrderService, cur_page: int, order_status: str):
        display_result = {
            'pagination': {}
        }
        display_result = o.get_order_info_page(current=cur_page, status=order_status)
        return display_result

    def _construct_page_title(self, order_status: str):
        title = 'Order Information Table'
        if order_status == 'OrderPending':
            title = 'Pending ' + title
        elif order_status == 'OrderPaid':
            title = 'Paid ' + title
        elif order_status == 'OrderFiled':
            title = 'Filed ' + title
        return title

    def _construct_page_button(self, order_status: str):
        if order_status == 'OrderPending':
            extra = {'r': '[R]Refresh', 's': '[S]Show Order Detail', 'm': '[M]Pay An Order'}
        else:
            extra = {'r': '[R]Refresh', 's': '[S]Show Order Detail'}
        return extra

    def _overpay_protection(self, order_info: dict, amt: int):
        check_amt = order_info['amountPaid'] + amt
        remain_amt = order_info['amount'] > order_info['amountPaid']
        if order_info['status'] == 'OrderPending':
            if check_amt > order_info['amount'] and remain_amt > 0:
                self.console.print('[bright_red]The input amount is larger than remaining order amount !!!')
                choice = self.console.input('[bright_green]Continue the payment with remaining amount (default Y)[Y/n]: ')
                if choice.lower() == 'n':
                    return amt
                else:
                    amt = order_info['amount'] - order_info['amountPaid']
                    self.console.print('')
                    self.console.print(f'[bright_green]The payment amount will be: {amt}')
                    self.console.print('')
                    self.console.input('Press ENTER to continue...')
                    return amt
            return amt
        else:
            self.console.print(f'[bright_green]Order is already paid with status - {order_info["status"]}')
            self.console.input('Press ENTER to continue...')
            return 0
