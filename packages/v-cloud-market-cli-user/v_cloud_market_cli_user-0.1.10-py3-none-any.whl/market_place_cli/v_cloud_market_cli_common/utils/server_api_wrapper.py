import os
import urllib
import requests
import base64
import time
import json
import base58
import axolotl_curve25519 as curve
from urllib.parse import urlparse
from hashlib import sha256

from .vsyschain.crypto import str2bytes
from .wallet_cipher import WalletCipher
from v_cloud_market_cli_common.service.wallet_service import WalletService
from v_cloud_market_cli_common.config.server_config import PLATFORM_HOST

class ServerWrapper(object):

    def __init__(self, nodeHost, privKey=b'', pubKey=b'', address=''):
        self.node_host = nodeHost
        self.priv_key = privKey
        self.pub_key = pubKey
        self.user_agent = "market command line v1.0"
        self.address = address

    def get_request(self, api, url_param={}, body_data={}, headers={}, needAuth=False, raw_res=False):
        if url_param:
            url_param = {k: url_param[k] for k in url_param if url_param[k]}
            api += '?' + urllib.parse.urlencode(url_param, doseq=True)
        return self._form_request("GET", api, body_data, extra_headers=headers, needAuth=needAuth, raw_res=raw_res)

    def post_request(self, api, url_param={}, body_data={}, headers={}, needAuth=False, raw=False, raw_res=False):
        if url_param:
            url_param = {k: url_param[k] for k in url_param if url_param[k]}
            api += '?' + urllib.parse.urlencode(url_param, doseq=True)
        return self._form_request("POST", api, body_data, needAuth, extra_headers=headers, raw=raw, raw_res=raw_res)

    def delete_request(self, api, url_param={}, body_data={}, headers={}, needAuth=False, raw=False, raw_res=False):
        if url_param:
            url_param = {k: url_param[k] for k in url_param if url_param[k]}
            api += '?' + urllib.parse.urlencode(url_param, doseq=True)
        return self._form_request("DELETE", api, body_data, needAuth, extra_headers=headers, raw=raw, raw_res=raw_res)

    def _form_request(self, method, api, body_data, needAuth, extra_headers={}, raw=False, raw_res=False):
        curTime = int(time.time())
        headers = {
            "x-sdk-time": str(curTime),
            "User-Agent": self.user_agent,
            "address": self.address
        }
        if needAuth:
            msg = self._form_string_to_sign(
                curTime,
                self._form_canonical_request(method, api, body_data))

            sig = self.sign(msg)
            b58Pubkey = base58.b58encode(self.pub_key).decode('utf-8')
            headers['public-key'] = b58Pubkey
            headers['signature'] = sig
        headers = {**headers, **extra_headers}
        resp = None
        try:
            if method == "GET" and body_data:
                resp = requests.get(self.node_host + api, headers=headers, json=body_data)
            elif method == "GET" and not body_data:
                resp = requests.get(self.node_host + api, headers=headers)
            elif method == "POST":
                if raw:
                    resp = requests.post(self.node_host + api, headers=headers, data=body_data, timeout=30)
                else:
                    resp = requests.post(self.node_host + api, headers=headers, json=body_data)
            elif method == "DELETE":
                resp = requests.delete(self.node_host + api, headers=headers, json=body_data)
            result = resp.json()
        except requests.exceptions.Timeout as e:
            result = {'error': {'code': resp.status_code, 'message': str(resp)}}
        except json.decoder.JSONDecodeError:
            result = {'error': {'code': resp.status_code, 'message': str(resp)}}
        except Exception as err:
            result = {'error': {'code': resp.status_code, 'message': str(resp)}}
        if raw_res or "message" in resp:
            return resp
        return result

    def _form_canonical_request(self, method, api, body_data={}):
        """
        canonical_request_string = \
            http_request_method + "\n" + \
            canonical_query_string + "\n" + \
            canonical_headers + "\n" + \
            SginedHeaders + "\n" + \
            HexEncode(Hash(RequestPayload))
        """
        m = sha256()
        u = urlparse(self.node_host + api)
        path = u.path
        if not path.startswith("/api/v1"):
            path = path[path.find('/api/v1'):]
        reqString = method + '\n' + \
                    path + '\n' + \
            '\n'.join(u.query.split('&')) + '\n' \
            'User-Agent:' + self.user_agent + '\n' + \
            'address:' + self.address + '\n'
        if body_data is not None:
            body_data = sha256(json.dumps(body_data).encode('utf-8')).hexdigest()
            reqString += body_data

        m.update(reqString.encode('utf-8'))
        return str(m.hexdigest())

    def _form_string_to_sign(self, timestamp, hashed):
        return sha256(("HMAC-SHA256" + str(timestamp) + hashed).encode('utf-8')).digest()

    def sign(self, inputByte):
        randm64 = os.urandom(64)
        sig = curve.calculateSignature(randm64, self.priv_key, inputByte)
        b64sig = base64.b64encode(sig).decode('utf-8')
        return b64sig


def NewServerWrapper(net_type, password, nonce, server_host=PLATFORM_HOST):
    walletService = WalletService(None, net_type, password)
    if len(walletService.accounts) - 1 < nonce:
        print(f"Info: wallet only contains address of nonce {len(walletService.accounts) - 1}, use nonce 0")
        nonce = 0
    account = walletService.accounts[nonce]
    pubKey = base58.b58decode(str2bytes(account.publicKey))
    privKey = base58.b58decode(str2bytes(account.privateKey))
    address = WalletCipher.generate_address(pubKey, net_type).decode('utf-8')
    return ServerWrapper(PLATFORM_HOST, privKey, pubKey, address), account
