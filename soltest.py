import struct
from pprint import pprint as p
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction,AccountMeta
from base58 import b58encode,b58decode as b58d
from base64 import b64encode,b64decode as b64d
from spl.token._layout import MINT_LAYOUT
b58e = lambda x : b58encode(x).decode('ascii')

uri = "http://api.mainnet-beta.solana.com"

client = Client(uri)

usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

ai = client.get_account_info(usdc)

p(ai)

account_data = ai['result']['value']['data'][0]

print(account_data)

data = b64d(account_data)
#unpacking 4byte integer (uint)

struct.unpack("<I",data[0:4])[0]