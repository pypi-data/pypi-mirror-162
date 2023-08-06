def getGroupID(chainPair):
    '''
    :param chainPair: ["2153201998", "2147483708"]
    :return:
    '''
    getWAN_ETH_GroupID = {"jsonrpc":"2.0","method":"getStoremanGroupList","params":{"chainIds":chainPair},"id":1}
    return getWAN_ETH_GroupID

def getStoremans(ID):
    '''
    :param ID: groupID
    :return:
    '''
    getStoremans = {"jsonrpc":"2.0","method":"getStoremanGroupMember","params":{"groupId":ID},"id":1}
    return getStoremans

def getRapidCCUserLockEvents(Chain,fromBlock,toBlock,scAddr,topic):
    '''
    get UserFastMintLogger event
    :param Chain:
    :param fromBlock:
    :param toBlock:
    :param scAddr:
    :param UserFastMintLogger:
    :return:
    '''
    getFastMint = {"jsonrpc":"2.0","method":"getScEvent","params":{"chainType":Chain, "fromBlock":fromBlock,"toBlock":toBlock,"address": scAddr, "topics": [topic]},"id":1}
    return getFastMint

def getScEvent(Chain,fromBlock,toBlock,scAddr,topics):
    '''
    get UserFastMintLogger event
    :param Chain:
    :param fromBlock:
    :param toBlock:
    :param scAddr:
    :param topics:[]
    :return:
    '''
    getScEvent = {"jsonrpc":"2.0","method":"getScEvent","params":{"chainType":Chain, "fromBlock":fromBlock,"toBlock":toBlock,"address": scAddr, "topics": topics},"id":1}
    return getScEvent

def getLatestBlock(Chain):
    getLatestBlock = {"jsonrpc": "2.0", "method": "getBlockNumber", "params": {"chainType": Chain}, "id": 1}
    return getLatestBlock

def getBlock(Chain,blockNumber):
    '''
    :param Chain: WAN/ETH
    :param blockNumber:
    :return:
    '''
    getBlock = {"jsonrpc":"2.0","method":"getBlockByNumber","params":{"chainType":Chain, "blockNumber":blockNumber},"id":1}
    return getBlock

def getRapidCCStoremanLockEvents(Chain,fromBlock,toBlock,scAddr,smLock,txHash):
    '''
    :param Chain:
    :param fromBlock:
    :param toBlock:
    :param scAddr:
    :param smFastMintLogger:
    :param txHash:
    :return:
    '''
    getSmFastMint = {"jsonrpc":"2.0","method":"getScEvent","params":{"chainType":Chain, "fromBlock":fromBlock,"toBlock":toBlock,"address": scAddr, "topics": [smLock,txHash]},"id":1}
    return getSmFastMint

def getStoremanGrpInfo(GrID):
    getStoremanGrpInfo = {"jsonrpc":"2.0","method":"getStoremanGroupInfo","params":{"groupId":GrID},"id":1}
    return getStoremanGrpInfo


def getBalance(account,chain):
    '''
    :param account:
    :param chain:
    :return: int wan/ether
    '''
    getBalance = {"jsonrpc":"2.0","method":"getBalance","params":{"address":account, "chainType":chain},"id":1}
    return getBalance

def getStoremanDelegatorInfo(wkAddrs_store):
    getStoremanDelegatorInfo = {"jsonrpc": "2.0", "method": "getStoremanDelegatorInfo", "params": {"wkAddr": wkAddrs_store}, "id": 1}
    return getStoremanDelegatorInfo


def getLatestBlockNumber(chain):
    getLatestBlockNumber = {"jsonrpc":"2.0","method":"getBlockNumber","params":{"chainType":chain},"id":1}
    return getLatestBlockNumber


def getBlockByNumber(chain,blockNumber):
    '''
    :param chain:
    :param blockNumber:
    :return:
    '''
    getBlockByNumber = {"jsonrpc": "2.0", "method": "getBlockByNumber", "params": {"chainType": chain, "blockNumber": blockNumber}, "id": 1}
    return getBlockByNumber


def getStoremanCandidates(ID):
    '''
    :param ID: groupID
    :return:
    '''
    getStoremanCandidates = {"jsonrpc":"2.0","method":"getStoremanCandidates","params":{"groupId":ID},"id":1}
    return getStoremanCandidates

def getOSMEvent(fromBlock,scAddr,topic):
    '''
    :param ID: groupID
    :return:
    '''
    getOSMEvent = {"jsonrpc":"2.0","method":"getScEvent","params":{"chainType":"WAN", "fromBlock":fromBlock,"address": scAddr, "topics": [topic]},"id":1}
    return getOSMEvent

def getStoremanInfo(wkAddr):
    '''
    :param ID: groupID
    :return:
    '''
    getStoremanInfo ={"jsonrpc":"2.0","method":"getStoremanInfo","params":{"wkAddr":wkAddr},"id":1}
    return getStoremanInfo


def getOSMReturnRadio():
    '''
    :param ID: groupID
    :return:
    '''
    getOSMReturnRadio ={"jsonrpc":"2.0","method":"getRewardRatio","params":{},"id":1}
    return getOSMReturnRadio


def getRegisteredValidator(wkAddr):
    '''
    :param address: work address
    :return:
    '''
    getRegisteredValidator ={"jsonrpc":"2.0","method":"getRegisteredValidator","params":{"after":1506789219,"address":wkAddr},"id":1}
    return getRegisteredValidator

def getEpochID():
    getEpochID = {"jsonrpc":"2.0","method":"getEpochID","params":{"chainType":"WAN"},"id":1}
    return getEpochID

def getEpochIDByTime(timestamp):
    getEpochIDByTime = {"jsonrpc":"2.0","method":"getEpochIDByTime","params":{"chainType":"WAN", "time":timestamp},"id":1}
    return getEpochIDByTime

def getStoremanGroupActivity(groupId,epochID):
    activity = {"jsonrpc":"2.0","method":"getStoremanGroupActivity","params":{"fromEpoch":epochID,"toEpoch":epochID,"groupId": groupId},"id":1}
    return activity

def getTokenPairs():
    tokenPairs = {"jsonrpc":"2.0","method":"getTokenPairs","params":{"chainIds":[2147483708, 2153201998]},"id":1}
    return tokenPairs

def getTokenBalance(chainType,account,tokenScAddr):
    getTokenBalance = {"jsonrpc": "2.0", "method": "getTokenBalance", "params": {"chainType":chainType,"address": account,"tokenScAddr": tokenScAddr},"id": 1}
    return getTokenBalance

def getTokenSupply(chainType,tokenScAddr):
    getTokenSupply = {"jsonrpc":"2.0","method":"getTokenSupply","params":{"chainType":chainType, "tokenScAddr" : tokenScAddr},"id":1}
    return getTokenSupply

def getTransaction(chainType,txHash):
    getTxInfo = {"jsonrpc":"2.0","method":"getTxInfo","params":{"chainType":chainType, "txHash":txHash},"id":1}
    return getTxInfo
def getOpReturnOutputs(btcAddress,startBlock,endBlock):
    '''
    :param btcAddress:
    :param startBlock:
    :param endBlock:
    :return:
                    {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": [
                        {
                            "txid": "08000247d89ad8a07fe849b25d0a2e47d215fe64c57c4dd36e27c75b7208e490",
                            "height": 675114,
                            "vout": [
                                {
                                    "scriptPubKey": {
                                        "addresses": [
                                            "1GPYp3ifU6DAGSrqqcoZbNBhQV5sCiZmg6"
                                        ],
                                        "asm": "OP_DUP OP_HASH160 a8cd97affe137d82449af725b52b5cb2635192f3 OP_EQUALVERIFY OP_CHECKSIG",
                                        "hex": "76a914a8cd97affe137d82449af725b52b5cb2635192f388ac",
                                        "reqSigs": 1,
                                        "type": "pubkeyhash"
                                    },
                                    "value": 0.01551803,
                                    "index": 0
                                },
                                {
                                    "scriptPubKey": {
                                        "asm": "OP_RETURN 01000f01c5c3711c72ffbb5ad5e04c1d5730ea9a27c30e0000765c",
                                        "hex": "6a1b01000f01c5c3711c72ffbb5ad5e04c1d5730ea9a27c30e0000765c",
                                        "type": "nulldata"
                                    },
                                    "value": 0,
                                    "index": 1
                                }
                            ]
                        }
                    ]
                }
    '''
    getOpReturnOutputs = {"jsonrpc":"2.0","method":"getOpReturnOutputs","params":{"chainType":"BTC", "fromBlock":startBlock,"toBlock":endBlock,"address":[btcAddress]},"id":1}
    return getOpReturnOutputs
def getOpReturnOutputsLTC(btcAddress,startBlock,endBlock):
    '''
    :param btcAddress:
    :param startBlock:
    :param endBlock:
    :return:
                    {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": [
                        {
                            "txid": "08000247d89ad8a07fe849b25d0a2e47d215fe64c57c4dd36e27c75b7208e490",
                            "height": 675114,
                            "vout": [
                                {
                                    "scriptPubKey": {
                                        "addresses": [
                                            "1GPYp3ifU6DAGSrqqcoZbNBhQV5sCiZmg6"
                                        ],
                                        "asm": "OP_DUP OP_HASH160 a8cd97affe137d82449af725b52b5cb2635192f3 OP_EQUALVERIFY OP_CHECKSIG",
                                        "hex": "76a914a8cd97affe137d82449af725b52b5cb2635192f388ac",
                                        "reqSigs": 1,
                                        "type": "pubkeyhash"
                                    },
                                    "value": 0.01551803,
                                    "index": 0
                                },
                                {
                                    "scriptPubKey": {
                                        "asm": "OP_RETURN 01000f01c5c3711c72ffbb5ad5e04c1d5730ea9a27c30e0000765c",
                                        "hex": "6a1b01000f01c5c3711c72ffbb5ad5e04c1d5730ea9a27c30e0000765c",
                                        "type": "nulldata"
                                    },
                                    "value": 0,
                                    "index": 1
                                }
                            ]
                        }
                    ]
                }
    '''
    getOpReturnOutputs = {"jsonrpc":"2.0","method":"getOpReturnOutputs","params":{"chainType":"LTC", "fromBlock":startBlock,"toBlock":endBlock,"address":[btcAddress]},"id":1}
    return getOpReturnOutputs
def getTokenPairsByChainID(chainPair,isAllTokenPairs=True):
    '''
    :param chainPair: list type [2147483708, 2153201998] isAllTokenPairs: True for all, False only for lite wallet
    :return:
    '''
    tokenPairs = {"jsonrpc":"2.0","method":"getTokenPairs","params":{"chainIds":chainPair,"isAllTokenPairs":isAllTokenPairs},"id":1}
    return tokenPairs

def getAllTokenPairs():
    '''
    :param
    :return:
    '''
    tokenPairs = {"jsonrpc":"2.0","method":"getTokenPairs","params":{"isAllTokenPairs":True},"id":1}
    return tokenPairs

def getStoremanGroupQuota(grid,chain,token):
    '''
    :param chain:'ETH'
    token:['USDT']
    :return:
    '''
    rsp = {"jsonrpc":"2.0","method":"getStoremanGroupQuota","params":{"chainType":chain,"groupId":grid, "symbol": token},"id":1}
    return rsp
def getSelectedStoreman(grid):
    rsp = {"jsonrpc":"2.0","method":"getSelectedStoreman","params":{"groupId":grid},"id":1}
    return rsp

def getBTCUTXO(asset,address):
    rsp = {"jsonrpc": "2.0", "method": "getUTXO","params": {"chainType": asset, "minconf": 0, "maxconf": 10000, "address": [address]},"id": 1}
    return rsp
def getTransactionReceipt(chain,tx):
    rsp = {"jsonrpc": "2.0", "method": "getTransactionReceipt","params": {"chainType": chain, "txHash": tx},"id": 1}
    return rsp