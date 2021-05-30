#!/usr/bin/env python3

from json import load, dump
from web3 import Web3, HTTPProvider
from eth_account import Account
from time import sleep
from os import getenv
from dotenv import load_dotenv
from logging import basicConfig, info, INFO

basicConfig(level=INFO)

STOP_FILE = 'stop.tmp'

dotenv_read = False

while True: 
    XDAI_RPC = getenv('XDAI_RPC', 'https://xdai.poanetwork.dev')

    BSC_OB = getenv('BSC_OB', '0x59447362798334d3485c64D1e4870Fde2DDC0d75')
    ETH_OB = getenv('ETH_OB', '0xf6A78083ca3e2a662D6dd1703c939c8aCE2e268d')

    MOONS_EXT = getenv('MOONS_EXT', '0x1E0507046130c31DEb20EC2f870ad070Ff266079')
    BRICKS_EXT = getenv('BRICKS_EXT', '0xf85b17E64Bc788D0CB1A8c8C87c0d74e520c2A54')

    FAUCET_PRIVKEY = getenv('FAUCET_PRIVKEY', None)

    GAS_PRICE = int(getenv('GAS_PRICE', 1))
    GAS_LIMIT = int(getenv('GAS_LIMIT', 30000))
    REWARD = float(getenv('REWARD', 0.005))
    POLLING_INTERVAL = getenv('POLLING_INTERVAL', 60)

    #INITIAL_START_BLOCK = 16173518
    INITIAL_START_BLOCK = int(getenv('INITIAL_START_BLOCK', 16190379))
    FINALIZATION_INTERVAL = int(getenv('FINALIZATION_INTERVAL', 12)) # blocks

    JSON_DB_DIR = getenv('JSON_DB_DIR', '.')
    JSON_START_BLOCK = getenv('JSON_START_BLOCK', 'faucet_start_block.json')
    JSON_CONTRACTS = getenv('JSON_CONTRACTS', 'xdai-contracts.json')
    
    if not FAUCET_PRIVKEY:
        if dotenv_read:
            break

        info('Environment is not configured')
        load_dotenv('./.env')
        dotenv_read = True
    else: 
        break

if not FAUCET_PRIVKEY:
    raise BaseException("Faucet's privkey is not provided. Check the configuration")

info(f'XDAI_RPC = {XDAI_RPC}')
info(f'BSC_OB = {BSC_OB}')
info(f'ETH_OB = {ETH_OB}')
info(f'MOONS_EXT = {MOONS_EXT}')
info(f'BRICKS_EXT = {BRICKS_EXT}')
info(f'FAUCET_PRIVKEY = ...')
info(f'GAS_PRICE = {GAS_PRICE}')
info(f'GAS_LIMIT = {GAS_LIMIT}')
info(f'REWARD = {REWARD}')
info(f'POLLING_INTERVAL = {POLLING_INTERVAL}')
info(f'INITIAL_START_BLOCK = {INITIAL_START_BLOCK}')
info(f'FINALIZATION_INTERVAL = {FINALIZATION_INTERVAL}')
info(f'JSON_DB_DIR = {JSON_DB_DIR}')
info(f'JSON_START_BLOCK = {JSON_START_BLOCK}')
info(f'JSON_CONTRACTS = {JSON_CONTRACTS}')

# event
# TokensBridged(address token, address recipient, uint256 value, bytes32 messageId)
ABI = """
[
  {
    "type":"event",
    "name":"TokensBridged",
    "inputs":[
      {
        "type":"address",
        "name":"token",
        "internalType":"address",
        "indexed":true
      },
      {
        "type":"address",
        "name":"recipient",
        "internalType":"address",
        "indexed":true
      },
      {
        "type":"uint256",
        "name":"value",
        "internalType":"uint256",
        "indexed":false
      },
      {
        "type":"bytes32",
        "name":"messageId",
        "internalType":"bytes32",
        "indexed":true
      }
    ],
    "anonymous":false
  }
]
"""

# TokensBridged(address recipient, uint256 value, bytes32 messageId)
EXT_ABI = """
[
  {
    "type":"event",
    "name":"TokensBridged",
    "inputs":[
      {
        "type":"address",
        "name":"recipient",
        "indexed":true
      },
      {
        "type":"uint256",
        "name":"value",
        "indexed":false
      },
      {
        "type":"bytes32",
        "name":"messageId",
        "indexed":true
      }
    ],
    "anonymous":false
  }
]
"""

xdai_w3 = Web3(HTTPProvider(XDAI_RPC))

bsc_ob = xdai_w3.eth.contract(abi = ABI, address = BSC_OB)
eth_ob = xdai_w3.eth.contract(abi = ABI, address = ETH_OB)

moons_mediator = xdai_w3.eth.contract(abi = EXT_ABI, address = MOONS_EXT)
bricks_mediator = xdai_w3.eth.contract(abi = EXT_ABI, address = BRICKS_EXT)

faucet = Account.privateKeyToAccount(FAUCET_PRIVKEY)

try:
    with open(f'{JSON_DB_DIR}/{JSON_START_BLOCK}') as f:
      tmp = load(f)
      start_block = int(tmp['start_block'])
except IOError:
    info("no start block stored previously")
    start_block = INITIAL_START_BLOCK
info(f'start block: {start_block}')

while True:
    try:
        with open(f'{JSON_DB_DIR}/{STOP_FILE}') as f:
            info("Stopping faucet")
            break
    except IOError:
        pass

    try:
        last_block = xdai_w3.eth.getBlock('latest').number
    except:
        raise BaseException('Cannot get the latest block number')
    info(f'current last block: {last_block}')
    last_block = last_block - FINALIZATION_INTERVAL

    filter = bsc_ob.events.TokensBridged.build_filter()
    info(f'Looking for TokensBridged events on BSC-xDAI OB from {start_block} to {last_block}')
    try:
        bsc_logs = xdai_w3.eth.getLogs({'fromBlock': start_block, 
                                        'toBlock': last_block, 
                                        'address': filter.address, 
                                        'topics': filter.topics})
    except:
        raise BaseException('Cannot get BSC-xDAI OB logs')
    info(f'Found {len(bsc_logs)} TokensBridged events on BSC-xDAI OB')

    filter = eth_ob.events.TokensBridged.build_filter()
    info(f'Looking for TokensBridged events on ETH-xDAI OB from {start_block} to {last_block}')
    try:
        eth_logs = xdai_w3.eth.getLogs({'fromBlock': start_block, 
                                        'toBlock': last_block, 
                                        'address': filter.address, 
                                        'topics': filter.topics})
    except:
        raise BaseException('Cannot get ETH-xDAI OB logs')
    info(f'Found {len(eth_logs)} TokensBridged events on ETH-xDAI OB')

    filter = moons_mediator.events.TokensBridged.build_filter()
    info(f'Looking for TokensBridged events on MOONs extension from {start_block} to {last_block}')
    try:
        moons_logs = xdai_w3.eth.getLogs({'fromBlock': start_block, 
                                          'toBlock': last_block, 
                                          'address': filter.address, 
                                          'topics': filter.topics})
    except:
        raise BaseException('Cannot get MOONs extension logs')
    info(f'Found {len(moons_logs)} TokensBridged events on MOONs extension')

    filter = bricks_mediator.events.TokensBridged.build_filter()
    info(f'Looking for TokensBridged events on BRICKs extension from {start_block} to {last_block}')
    try:
        bricks_logs = xdai_w3.eth.getLogs({'fromBlock': start_block, 
                                            'toBlock': last_block, 
                                            'address': filter.address, 
                                            'topics': filter.topics})
    except:
        raise BaseException('Cannot get BRICKs extension logs')
    info(f'Found {len(bricks_logs)} TokensBridged events on BRICKs extension')

    recipients = set()

    for log in bsc_logs:
        recipient = bsc_ob.events.TokensBridged().processLog(log).args.recipient
        recipients.add(recipient)
    info(f'Identified {len(recipients)} tokens recipients from BSC-xDAI OB events')
    
    tmp = len(recipients)
    for log in eth_logs:
        recipient = eth_ob.events.TokensBridged().processLog(log).args.recipient
        recipients.add(recipient)
    info(f'Identified {len(recipients) - tmp} tokens recipients from ETH-xDAI OB events')
    
    tmp = len(recipients)
    for log in moons_logs:
        recipient = moons_mediator.events.TokensBridged().processLog(log).args.recipient
        recipients.add(recipient)
    info(f'Identified {len(recipients) - tmp} tokens recipients from MOONs extension events')

    tmp = len(recipients)
    for log in bricks_logs:
        recipient = bricks_mediator.events.TokensBridged().processLog(log).args.recipient
        recipients.add(recipient)
    info(f'Identified {len(recipients) - tmp} tokens recipients from BRICKs extension events')

    try:
        with open(f'{JSON_DB_DIR}/{JSON_CONTRACTS}') as f:
          contracts = load(f)
    except IOError:
        info("no contracts identified previously")
        contracts = {}

    endowing = []
    for recipient in recipients:
        if recipient in contracts:
            continue
        code = xdai_w3.eth.getCode(recipient)
        if code != b'':
            contracts[recipient] = True
            continue
        balance = xdai_w3.eth.getBalance(recipient)
        if balance == 0:
            info(f'{recipient} balance is zero')
            endowing.append(recipient)
    info(f'found {len(endowing)} accounts for reward')
    
    with open(f'{JSON_DB_DIR}/{JSON_CONTRACTS}', 'w') as json_file:
      dump(contracts, json_file)
    
    balance_error = False
    
    if len(endowing) > 0:
        try:
            faucet_balance = xdai_w3.eth.getBalance(faucet.address)
        except:
            raise BaseException("Cannot get faucet balance")
        info(f'faucet balance: {faucet_balance}')

        if faucet_balance > len(endowing) * GAS_LIMIT * Web3.toWei(GAS_PRICE, 'gwei'):
            try:
                nonce = xdai_w3.eth.getTransactionCount(faucet.address)
            except:
                raise BaseException("Cannot get transactions count of faucet's account")
            info(f'starting nonce: {nonce}')
            for recipient in endowing:
                tx = {
                    'nonce': nonce,
                    'gas': GAS_LIMIT,
                    'gasPrice': Web3.toWei(GAS_PRICE, 'gwei'),
                    'data': b'Rewarded for OmniBridge transaction',
                    'chainId': 100,
                    'value': Web3.toWei(REWARD, 'ether'),
                    'to': recipient,
                }
                rawtx = faucet.signTransaction(tx)
                sent_tx_hash = xdai_w3.eth.sendRawTransaction(rawtx.rawTransaction)
                info(f'{recipient} rewarded by {Web3.toHex(sent_tx_hash)}')
                nonce += 1
                sleep(0.1)
        else:
            info(f'not enough balance on the faucet {faucet.address}')
            balance_error = True

    if not balance_error:
        start_block = last_block + 1
        with open(f'{JSON_DB_DIR}/{JSON_START_BLOCK}', 'w') as json_file:
            dump({'start_block': start_block}, json_file)
            
    sleep(POLLING_INTERVAL)