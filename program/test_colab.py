from dydx3 import Client
from web3 import Web3
from pprint import pprint
from datetime import datetime, timedelta
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import API_HOST_SEPOLIA, API_HOST_MAINNET
from decouple import config
from dydx3.constants import MARKET_BTC_USD, ORDER_SIDE_BUY, ORDER_TYPE_MARKET, TIME_IN_FORCE_FOK, NETWORK_ID_SEPOLIA
import pytz

MODE = "DEVELOPMENT"

# Must be on Mainnet in DYDX
STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")

# KEYS - DEVELOPMENT
# Must be on Testnet in DYDX
STARK_PRIVATE_KEY_TESTNET = "02bdf79a38360f814f07ee3bbb6b48a6cbd75fd1ccce9915a434d751830fdeb2"
DYDX_API_KEY_TESTNET = "3dc6af7f-f11e-3029-6493-f0492b0a4737"
DYDX_API_SECRET_TESTNET = "ZPa1fSr4KHR41JhLEq_HthRym2aRZpST6EEa-3GI"
DYDX_API_PASSPHRASE_TESTNET = "sNkgTjieuUivri34bjN8"

# KEYS - Export
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PRODUCTION" else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY = DYDX_API_KEY_MAINNET if MODE == "PRODUCTION" else DYDX_API_KEY_TESTNET
DYDX_API_SECRET = DYDX_API_SECRET_MAINNET if MODE == "PRODUCTION" else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_MAINNET if MODE == "PRODUCTION" else DYDX_API_PASSPHRASE_TESTNET

# HOST - Export
HOST = API_HOST_MAINNET if MODE == "PRODUCTION" else API_HOST_SEPOLIA

# HTTP PROVIDER
HTTP_PROVIDER_MAINNET = "https://eth-mainnet.g.alchemy.com/v2/C38A2E03uos12XB0zaw4OhkHEZm5Io8T"
HTTP_PROVIDER_TESTNET = "https://eth-goerli.g.alchemy.com/v2/b9CmjVOibZ3s90EAMdjalLg8Q4sVzfdQ"
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET if MODE == "PRODUCTION" else HTTP_PROVIDER_TESTNET

# Ethereum Address
ETHEREUM_ADDRESS = "0xc84921bD37a5DC54B23e7b89e7766c3800384FBd"

# Create Client Connection
client = Client(
    host=HOST,
    api_key_credentials={
        "key": DYDX_API_KEY,
        "secret": DYDX_API_SECRET,
        "passphrase": DYDX_API_PASSPHRASE,
    },
    stark_private_key = STARK_PRIVATE_KEY,
    network_id = NETWORK_ID_SEPOLIA,
    eth_private_key = config("ETH_PRIVATE_KEY"),
    default_ethereum_address = ETHEREUM_ADDRESS,
    web3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER))
)

# Check Connection
account = client.private.get_account(
    ethereum_address=ETHEREUM_ADDRESS
)
account_id = account.data["account"]["id"]
quote_balance = account.data["account"]["quoteBalance"]
print("Connection successful")
print("Account Id: ", account_id)
print("Quote Balance: ", quote_balance)
print(NETWORK_ID_SEPOLIA)

# OHLC Candlestick Data
candles = client.public.get_candles(
  market="BTC-USD",
  resolution='1HOUR',
  limit=3
)

# PPrint Result
pprint(candles.data["candles"][0])

# Get Position Id
account_response = client.private.get_account()
position_id = account_response.data["account"]["positionId"]

# Get expiration time
server_time = client.public.get_time()
expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "+00:00")) + timedelta(seconds=70)

# Place an order
placed_order = client.private.create_order(
  position_id=position_id, # required for creating the order signature
  market=MARKET_BTC_USD,
  side=ORDER_SIDE_BUY,
  order_type=ORDER_TYPE_MARKET,
  post_only=False,
  size='0.001',
  price='100000',
  limit_fee='0.015',
  expiration_epoch_seconds=expiration.timestamp(),
  time_in_force=TIME_IN_FORCE_FOK, 
  reduce_only=False
)