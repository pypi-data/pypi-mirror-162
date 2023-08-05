from rich.console import Console
from rich.prompt import IntPrompt

from market_place_cli.v_cloud_market_cli_common.service_display.market_service_display import MarketServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.v_cloud_market_cli_common.service_display.cart_service_display import CartServiceDisplay
from market_place_cli.v_cloud_market_cli_common.service.cart_service import CartService
from market_place_cli.v_cloud_market_cli_common.service.market_service import MarketService
from market_place_cli.service_interface_request.wallet_service_request import WalletRequest
from market_place_cli.service_interface_request.common_request import get_table_choice
from market_place_cli.service_interface_logic.common import get_net, wallet_has_password, calculate_amount
from market_place_cli.v_cloud_market_cli_common.utils.service_error import HttpNotFoundException

class CartServiceLogic:

    

    def __init__(self):
        self.title = "CartService"
        self.console = None
        self.cart_display = None
        self.wr = None
        self.net_type = 'M'
        self.nonce = 0
        self.password = ''
        self.main_functions = ['Show cart list']
        self.cart_service = CartService()
        # load cart data from cache file
        self.cart_data = self.cart_service.load_cart_from_file()

    @property
    def Name(self):
        return self.title

    def get_cart_list(self):
        return self.cart_data

    def init_cart(self, console: Console, isTestnet: bool):
        self.console = console
        self.net_type = get_net(isTestnet)
        self.md = MarketServiceDisplay(self.console)
        self.display = CartServiceDisplay(self.console)
        

    def init_wallet(self):
        # avoid repeat init
        if not self.wr:
            self.wr = WalletRequest(self.console)
            self.nonce = self.wr.get_payment_address()
            if wallet_has_password(self.net_type):
                self.password = self.wr.get_password()
            self.ms = MarketService(self.net_type, self.password, self.nonce)

    def StartLogic(self, console: Console, isTestnet: bool):
        console.clear()
        while True:
            choice = MainInterface.display_service_choice(console, self.title, self.main_functions, True)
            if choice == '1':
                self.show_cart_list()
            elif choice.lower() == 'b':
                break
    
    def add_order(self, amount: float, options: dict, duration: int, expired_date: str, service_info: dict):
        provider_name = service_info['provider']
        if provider_name not in self.cart_data:
            self.cart_data[provider_name] = []
        order = {
            'amount': amount,
            'options': options,
            'duration': duration,
            'expired_date': expired_date,
            'service_info': service_info
        }
        self.cart_data[provider_name].append(order)
        self.cart_service.save_cart_to_file(self.cart_data)
        self.console.input('Success. Press ENTER to continue...')

    def remove_order(self, target : int = 0):
        index = 0
        for provider_name, orders in self.cart_data.items():
            for order in orders:
                if target == index:
                    orders.remove(order)
                    self.cart_service.save_cart_to_file(self.cart_data)
                    self.console.print('Success')
                    return
                index += 1
        self.console.input('[bright_red]Index out of range. Press ENTER to continue...')

    def show_cart_list(self):
        while True:
            index = 0
            total_amount = 0
            cart_list = []
            for provider_name, orders in self.cart_data.items():
                for order in orders:
                    service_info =  order['service_info']
                    item = {
                        'index': index,
                        'id': service_info['id'],
                        'provider': service_info['provider'],
                        'name': service_info['name'],
                        'options': order['options'],
                        'duration': order['duration'] or '-',
                        'expired_date': order['expired_date'] or '-',
                        'amount': order['amount']
                    }
                    total_amount += order['amount']
                    cart_list.append(item)
                    index += 1
            if len(cart_list) != 0:
                total = {
                    'index': 'total',
                    'amount': total_amount
                }
                cart_list.append(total)

            headers = [
                {"text": "Index", "value": 'index'},
                {"text": "Service ID", "value": 'id'},
                {"text": "Service Provider", "value": 'provider'},
                {"text": "Service Name", "value": "name"},
                {"text": "Service Options", "value": "options"},
                {"text": "Duration", "value": "duration"},
                {"text": "Expired Date", "value": "expired_date"},
                {"text": "Amount", "value": "amount"},
            ]
            w = self.display.display_cart_table(headers, cart_list)
            choice = get_table_choice(self.console, w, False, {'o': '[O]Make Order from Cart', 'r': '[R]Remove Order by Choosing Index', 'b': '[B]Back to Top Menu'})
            if choice == 'o':
                self.make_order()
            elif choice == 'r':
                target_index = IntPrompt.ask("[bright_green]Please enter the order INDEX: ")
                self.remove_order(target_index)
            elif choice == 'e':
                break
            elif choice == 'b':
                return True

    def make_order(self):
        try:
            # init wallet corresponding attributes
            self.init_wallet()
            payload_dict = {}
            amount = 0
            for provider_name, orders in self.cart_data.items():
                payload = {
                    'userServices': []
                }
                for order in orders:
                    item = {
                        'serviceID': order['service_info']['id'],
                        'duration': order['duration'],
                        'serviceOptions': order['options'],
                    }
                    if order['expired_date']:
                        item['expiredDate'] = order['expired_date']
                    payload['userServices'].append(item)
                    amount += order['amount']
                payload_dict[provider_name] = payload

            if not self.ms.enough_balance(amount):
                self.console.print(f'[bright_red]Your balance in address index {self.nonce + 1} is not enough.')
                self.console.input('[bright_red]Order Creation Aborted...')
                return

            for provider_name, payload in payload_dict.items():
                order_brief = self.ms.make_orders(payload)
                # delete cart order if make order success
                self.cart_data.pop(provider_name, None)
                self.cart_service.save_cart_to_file(self.cart_data)
                self.md.display_order_brief(order_brief)
        except Exception as e:
            print(e)


cart = CartServiceLogic()
