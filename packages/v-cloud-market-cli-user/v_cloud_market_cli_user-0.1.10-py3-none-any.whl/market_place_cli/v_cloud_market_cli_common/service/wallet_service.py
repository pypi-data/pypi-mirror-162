from base58 import b58encode
from v_cloud_market_cli_common.service_display.wallet_service_display import WalletServiceDisplay

from v_cloud_market_cli_common.utils.wallet_storage import WalletStorage, WalletData, get_cache_file_path
from v_cloud_market_cli_common.utils.vsyschain.account import *
from v_cloud_market_cli_common.utils.vsyschain import testnet_chain
from v_cloud_market_cli_common.utils.vsyschain.contract_helper import (
    send_data_stack_generator,
    send_function_index
)
from v_cloud_market_cli_common.config.wallet_config import (
    WALLET_FILENAME,
    AGENT_STRING,
    ADDRESS_CSV_FILENAME,
    PAYMENT_METHOD,
    PAYMENT_UNITY
)
from v_cloud_market_cli_common.utils.vsyschain.contract import (
    token_id_from_contract_id
)

NO_DISPLAY = 0
DISPLAY_BALANCE = 1
DISPLAY_BALANCE_DETAIL = 2


class WalletService:

    def __init__(self, wsd: WalletServiceDisplay, net: str, password: str, walletFile=None, load_wallet=True, show_err=True):
        self.display = wsd
        self.accounts = []
        self.net = net
        self.password = password
        self.cipher = None if not password else WalletCipher(password)
        self.show_err = show_err
        if walletFile:
            self.walletFile = walletFile
        else:
            self.walletFile = get_cache_file_path(WALLET_FILENAME)
        if load_wallet:
            self.wallet_data = self.load_wallet_file()

    def load_wallet_file(self):
        wallet_storage = WalletStorage(self.walletFile)
        try:
            wallet_data = wallet_storage.load(self.cipher, show_err=self.show_err)
            if not wallet_data or len(wallet_data) == 0:
                return None
        except Exception as e:
            return None
        self._load_accounts(seed=wallet_data.seed, nonce=wallet_data.nonce)
        return wallet_data

    def save_wallet_file(self, walletData):
        wallet_path = get_cache_file_path(WALLET_FILENAME)
        wallet_storage = WalletStorage(wallet_path)
        wallet_storage.save(walletData, self.cipher)

    def set_wallet_cipher(self, new_password: str):
        self.cipher = None if not new_password else WalletCipher(new_password)

    def decrypt_wallet_file(self):
        data = self.load_wallet_file()
        if data:
            self.save_wallet_file(data)

    def show_address(self, toCSV, balanceFlag):
        if not self.wallet_data:
            self.display.console.print('[orange]No seed information or wallet data file.')
            return
        seed = self.wallet_data.seed
        accInfoList = []
        for i in range(0, len(self.wallet_data.accountSeeds)):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            if balanceFlag == DISPLAY_BALANCE:
                acc = self._load_account(seed, i)
                if PAYMENT_METHOD == "vsys":
                    accInfo['balance'] = acc.balance()
                else:
                    token_id = token_id_from_contract_id(PAYMENT_METHOD, 0)
                    accInfo['balance'] = acc.token_balance(token_id)
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            accInfoList.append(accInfo)
            if toCSV:
                accInfo['seed'] = self.wallet_data.seed
                self._save_to_csv(accInfo)
        self.display.show_address(accInfoList)

    def fetch_wallet_info(self, index: int, field: str):
        if not self.wallet_data:
            self.display.console.print('[orange]No seed information or wallet data file.')
            return
        account = self.accounts[index]

        pub = base58.b58decode(str2bytes(account.publicKey))
        # priv = base58.b58decode(str2bytes(account.privateKey))
        address = WalletCipher.generate_address(pub, self.net).decode('utf-8')
        if field == 'priv':
            return account.privateKey
        elif field == 'pub':
            return account.publicKey
        elif field == 'add':
            return address

    def recover_wallet(self, seed, count, toCSV, balanceFlag=DISPLAY_BALANCE_DETAIL):
        accSeeds = set()
        accInfoList = []
        for i in range(0, count):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            accInfo['seed'] = seed
            if balanceFlag == DISPLAY_BALANCE:
                accInfo['balance'] = self._load_account(seed, i).balance()
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            accInfoList.append(accInfo)
            accSeedDisplay = b58encode(accInfo['accSeed']).decode('utf-8')
            accSeeds.add(accSeedDisplay)
            if toCSV:
                self._save_to_csv(accInfo)
            else:
                self._clean_csv_file()
        data = WalletData(seed, list(accSeeds), count, AGENT_STRING)
        self.save_wallet_file(data)
        self.display.show_address(accInfoList)

    def seed_generate(self, toCSV, balanceFlag, count=1):
        seed = WalletCipher.generate_phrase()
        self._protect_local_wallet()
        self.display.show_seed(seed)
        self.recover_wallet(seed=seed, count=count, toCSV=toCSV, balanceFlag=balanceFlag)

    def address_generate(self, count, toCSV, toAppend, balanceFlag):
        if not self.wallet_data:
            self.seed_generate(count, toCSV)
            self.load_wallet_file()

        n = self.wallet_data.nonce - 1
        seed = self.wallet_data.seed
        oldAccSeeds = self.wallet_data.accountSeeds
        newAcc = set()
        accInfoList = []
        for i in range(n, n + count):
            accInfo = WalletCipher.generate_account_info(seed, self.net, i)
            accInfo['seed'] = seed
            accSeedDisplay = b58encode(accInfo['accSeed']).decode('utf-8')
            newAcc.add(accSeedDisplay)
            accInfoList.append(accInfo)
            if balanceFlag == DISPLAY_BALANCE:
                accInfo['balance'] = self._load_account(seed, i).balance()
            elif balanceFlag == DISPLAY_BALANCE_DETAIL:
                accInfo['balanceDetail'] = self._load_account(seed, i).balance_detail()
            if toCSV:
                self._save_to_csv(accInfo)
        if toAppend:
            oldAccSeeds += list(newAcc)
            data = WalletData(seed, oldAccSeeds, count + n, AGENT_STRING)
            self.save_wallet_file(data)
        self.display.show_address(accInfoList)

    def account_pay(self, accountNonce, recipient, amount, attachment=''):
        try:
            account = self.accounts[accountNonce]
            if PAYMENT_METHOD == "vsys":
                resp = account.send_payment(recipient, int(amount * PAYMENT_UNITY), attachment=attachment)
            else:
                data_stack = send_data_stack_generator(recipient, int(amount * PAYMENT_UNITY))
                if data_stack is None:
                    self.display.console.input('[bright_red]Failed to generate data entries for payment! Press ENTER to continue...')
                    return
                resp = account.execute_contract(contract_id=PAYMENT_METHOD, func_id=send_function_index, data_stack=data_stack, attachment=attachment)
            self.display.show_account_pay(recipient, amount)
        except Exception as e:
            raise e

    def _protect_local_wallet(self):
        wallet_path = get_cache_file_path(WALLET_FILENAME)
        if os.path.exists(wallet_path):
            input('> press ENTER to continue.')

    def _save_to_csv(self, jsonData):
        wallet_path = get_cache_file_path(ADDRESS_CSV_FILENAME)
        with open(wallet_path, 'w+') as file:
            file_str = str(jsonData['nonce']) + ',' + \
            jsonData['addr'] + ',' + \
            b58encode(jsonData['pub']).decode('utf-8') + ',' + \
            b58encode(jsonData['priv']).decode('utf-8') + ',' + \
            b58encode(jsonData['accSeed']).decode('utf-8') + ',' + \
            jsonData['seed']
            if self.cipher:
                file.write(self.cipher.encrypt(file_str))
            else:
                file.write(file_str)

    def _clean_csv_file(self):
        file_path = get_cache_file_path(ADDRESS_CSV_FILENAME)
        with open(file_path, 'w+') as file:
            file.write('')

    def _load_accounts(self, seed, nonce):
        for i in range(0, nonce):
            self.accounts.append(self._load_account(seed, i))

    def _load_account(self, seed, nonce):
        if self.net == 'M':
            return Account(chain=mainnet_chain(), seed=seed, nonce=nonce)
        else:
            return Account(chain=testnet_chain(), seed=seed, nonce=nonce)
