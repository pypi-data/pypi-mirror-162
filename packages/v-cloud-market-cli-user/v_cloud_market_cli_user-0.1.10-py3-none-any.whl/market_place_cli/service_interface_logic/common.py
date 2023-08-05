import math

from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.utils.service_error import WalletStorageLoadingException


def get_net(is_testnet) -> str:
    return 'T' if is_testnet else 'M'


def wallet_has_password(net_type: str) -> bool:
    try:
        ws = WalletService(None, net_type, "", show_err=False)
        return ws.wallet_data is None
    except WalletStorageLoadingException:
        return True

def calculate_amount(price_set: dict, duration: int) -> int:
    discount = 1
    time_units = sorted(price_set['duration'].keys(), key=int)
    for dur in time_units:
        if duration >= int(dur):
            discount = price_set['duration'][dur]
    amt = price_set['price'] * discount * duration
    return amt  
