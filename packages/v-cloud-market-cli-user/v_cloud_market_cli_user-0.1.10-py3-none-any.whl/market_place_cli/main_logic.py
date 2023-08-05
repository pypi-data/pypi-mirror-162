import os, sys
sys.path.append(os.getcwd())

import click
from enum import Enum
from rich.console import Console

from market_place_cli.v_cloud_market_cli_common.service_display.main_interface import MainInterface
from market_place_cli.service_interface_logic import Logics


class ServiceState(Enum):
    MainService = 0
    MarketService = 1
    OrderService = 2
    WalletService = 3
    UserService = 4
    CartService = 5
    UpperLevelService = 6


@click.command()
@click.option('-t', '--testnet', is_flag=True, help='Specify net type')
def start(testnet):
    console = Console()
    curState = ServiceState.MainService
    Logics.container['Wallet Initialize'].StartLogic(console, testnet)
    Logics.container.pop('Wallet Initialize', None)
    Logics.container[ServiceState.CartService.name].init_cart(console, testnet)
    while True:
        try:
            state = int(service_execution(console, curState, testnet))
            if state == ServiceState.UpperLevelService.value:
                curState = ServiceState.MainService
            elif state == ServiceState.MarketService.value:
                curState = ServiceState.MarketService
            elif state == ServiceState.OrderService.value:
                curState = ServiceState.OrderService
            elif state == ServiceState.WalletService.value:
                curState = ServiceState.WalletService
            elif state == ServiceState.UserService.value:
                curState = ServiceState.UserService
            elif state == ServiceState.CartService.value:
                curState = ServiceState.CartService
            else:
                print('You should not be here...')
        except Exception:
            pass


def service_execution(console: Console, state: ServiceState, isTestnet: bool) -> str:
    if state == ServiceState.MainService:
        newState = MainInterface.display_service_choice(console, "Main Services", Logics.container.keys())
        if newState == '' or int(newState) > ServiceState.UpperLevelService.value or int(newState) < ServiceState.MainService.value:
            return service_execution(console, state, isTestnet)
        return newState
    elif state == ServiceState.MarketService:
        Logics.container[ServiceState.MarketService.name].StartLogic(console, isTestnet)
        return str(ServiceState.UpperLevelService.value)
    elif state == ServiceState.OrderService:
        Logics.container[ServiceState.OrderService.name].StartLogic(console, isTestnet)
        return str(ServiceState.UpperLevelService.value)
    elif state == ServiceState.WalletService:
        Logics.container[ServiceState.WalletService.name].StartLogic(console, isTestnet)
        return str(ServiceState.UpperLevelService.value)
    elif state == ServiceState.UserService:
        Logics.container[ServiceState.UserService.name].StartLogic(console, isTestnet)
        return str(ServiceState.UpperLevelService.value)
    elif state == ServiceState.CartService:
        Logics.container[ServiceState.CartService.name].StartLogic(console, isTestnet)
        return str(ServiceState.UpperLevelService.value)
    else:
        console.input('You should not be here...')
