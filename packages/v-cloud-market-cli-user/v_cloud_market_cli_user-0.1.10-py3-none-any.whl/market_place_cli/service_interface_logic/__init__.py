from .market_service_logic import MarketServiceLogic
from .order_service_logic import OrderServiceLogic
from .wallet_service_logic import WalletServiceLogic
from .user_service_logic import UserServiceLogic
from .initialization_logic import InitializationLogic
from .cart_service_logic import cart


class ServiceLogicContainer:

    def __init__(self):
        self.container = {}

    def register(self, serviceLogic):
        self.container[serviceLogic.Name] = serviceLogic


il = InitializationLogic()
ml = MarketServiceLogic()
ol = OrderServiceLogic()
wl = WalletServiceLogic()
ul = UserServiceLogic()

Logics = ServiceLogicContainer()
Logics.register(il)
Logics.register(ml)
Logics.register(ol)
Logics.register(wl)
Logics.register(ul)
Logics.register(cart)
