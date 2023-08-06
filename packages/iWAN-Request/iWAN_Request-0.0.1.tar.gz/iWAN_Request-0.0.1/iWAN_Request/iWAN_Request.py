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