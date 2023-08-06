from iWAN import iWAN #pip install iWAN
import json
from pubkey2address import Gpk2BtcAddr,Gpk2DotAddr,Gpk2XrpAddr #pip install pubkey2address
from iWAN_Request import iWAN_Request
import requests
class TokenPairsUtility:
    '''
    LockedAccounts;
    TokenPairs related infomations
    '''
    def __init__(self,net,iWAN_Config,print_flag=False):
        '''
        :param net: 'main'/'test'
        :param iWAN_Config: ".iWAN_config.json"
                {
                    "secretkey": "your secretkey",
                    "Apikey": "your apikey",
                    "url_test": "wss://apitest.wanchain.org:8443/ws/v3/",
                    "url_main": "wss://api.wanchain.org:8443/ws/v3/",
                    "dingApi":"https://oapi.dingtalk.com/robot/send?access_token=your ding robot token",
                    "emailAddress":"your email address",
                    "assetblackList":[black asset list]
                }

        '''
        with open(iWAN_Config,'r') as f:
            config = json.load(f)
        self.net = net
        self.iwan = iWAN.iWAN(config["url_{}".format(net)],config['secretkey'],config['Apikey'])
        self.print_flag = print_flag
    def pprint(self,*args,**kwargs):
        if self.print_flag :
            print(*args,**kwargs)
    def getTokenPairs(self):
        '''
        :return:
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": [
                    {
                        "id": "1",
                        "fromChainID": "2147483708",
                        "fromAccount": "0x0000000000000000000000000000000000000000",
                        "toChainID": "2153201998",
                        "toAccount": "0xe3ae74d1518a76715ab4c7bedf1af73893cd435a",
                        "ancestorSymbol": "ETH",
                        "ancestorDecimals": "18",
                        "ancestorAccount": "0x0000000000000000000000000000000000000000",
                        "ancestorName": "ethereum",
                        "ancestorChainID": "2147483708",
                        "name": "wanETH@wanchain",
                        "symbol": "wanETH",
                        "decimals": "18"
                    }
                ]
            }
        '''
        tokenPairs = self.iwan.sendRequest(iWAN_Request.getAllTokenPairs())
        return tokenPairs
    def getChainInfo(self):
        '''
        :return:
        '''
        chainInfo = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/chainInfos.json').json()[self.net]
        return chainInfo
    def getPoolTokenInfo(self):
        poolTokenInfo = requests.get("https://raw.githubusercontent.com/Nevquit/configW/main/crossPoolTokenInfo.json").json()[self.net]
        return poolTokenInfo
    def getEVMLockedAccounts(self):
        evmLockedAccounts = requests.get("https://raw.githubusercontent.com/Nevquit/configW/main/evmChainCrossSc.json").json()[self.net]
        return evmLockedAccounts
    def getNoEVMLockedAccounts(self,grInfo):
        BTCAddr = Gpk2BtcAddr.GPK2BTCADDRESS(grInfo,net=self.net)
        btcAddress = BTCAddr.Public_key_to_address('BTC')
        ltcAddress = BTCAddr.Public_key_to_address('LTC')
        dogeAddress = BTCAddr.Public_key_to_address('DOGE')
        xrpAddress = Gpk2XrpAddr.GPK2XRPADDRESS().getSmXrpAddr(grInfo)
        dotAddress = Gpk2DotAddr.GPK2DOTADDRESS().getSmDotAddr(grInfo,self.net)
        noEVMLockedAccout = {'LTC':ltcAddress,'XRP':xrpAddress,'BTC':btcAddress,'DOGE':dogeAddress,'DOT':dotAddress}
        return noEVMLockedAccout
    def getLockedAccount(self,grInfo):
        LockedAccounts = {}
        evmLockedAccounts = self.getEVMLockedAccounts()
        noEVMLockedAccout = self.getNoEVMLockedAccounts(grInfo)
        LockedAccounts.update(evmLockedAccounts)
        LockedAccounts.update(noEVMLockedAccout)
        return LockedAccounts
    def getChainDict(self):
        '''
        :return: chainIdDict,chainAbbr,noEVMChains
        '''
        chainIdDict={}
        chainAbbr = {}
        noEVMChains = []
        chainInfo = self.getChainInfo()
        for chainID in chainInfo.keys():
            chainName = chainInfo[chainID]["chainName"]
            chainIdDict[chainID] = chainName

            chainType = chainInfo[chainID]["chainType"]
            chainAbbr[chainName] = chainType

            evm = chainInfo[chainID]["evm"]
            if not evm:
                noEVMChains.append(chainType)
        return chainIdDict, chainAbbr, noEVMChains
    def getPoolTokenDict(self):
        poolTokenDict = {}
        poolTokenInfo = self.getPoolTokenInfo()
        poolTokenIDList = [int(i) for i in list(poolTokenInfo.keys())]
        for tokenPairID in poolTokenIDList:
            poolTokenDict[poolTokenInfo[str(tokenPairID)]['Asset']]={'TokenAddress':poolTokenInfo[str(tokenPairID)]['TokenAddress']}
            poolTokenDict[poolTokenInfo[str(tokenPairID)]['Asset']]['PoolScAddress'] = poolTokenInfo[str(tokenPairID)]['PoolScAddress']
            poolTokenDict[poolTokenInfo[str(tokenPairID)]['Asset']]['originalAmount'] = poolTokenInfo[str(tokenPairID)]['originalAmount']
        return poolTokenDict, poolTokenIDList
    def getassetCCDit(self):
        '''
        :return: assetCCDit:
                {
                "LTC": {
                    "OriginalChain": {
                        "Litcoin": "0x0000000000000000000000000000000000000000"
                    },
                    "MapChain": [
                        {
                            "Wanchain": "0xd8e7bd03920ba407d764789b11dd2b5eaee0961e"
                        },
                        {
                            "Ethereum": "0x6ec534cc08e7318c35220daf2b2bd8ae63878385"
                        },
                        {
                            "BSC": "0xdd4b9b3ce03faaba4a3839c8b5023b7792be6e2c"
                        }
                    ],
                    "CCType":"Pool"
                }
            }
        supportChains = ["Wanchain","Ethereum","BSC"]
        '''
        assetCCDit = {}
        supportMapChains = []
        tokenPairs = self.getTokenPairs()
        chainIdDict, chainAbbr, noEVMChains = self.getChainDict()
        poolTokenDict, poolTokenIDList = self.getPoolTokenDict()
        for tokenPair in tokenPairs['result']:
            '''
            tokenPair ={
                        "id": "1",
                        "fromChainID": "2147483708",
                        "fromAccount": "0x0000000000000000000000000000000000000000",
                        "toChainID": "2153201998",
                        "toAccount": "0xe3ae74d1518a76715ab4c7bedf1af73893cd435a",
                        "ancestorSymbol": "ETH",
                        "ancestorDecimals": "18",
                        "ancestorAccount": "0x0000000000000000000000000000000000000000",
                        "ancestorName": "ethereum",
                        "ancestorChainID": "2147483708",
                        "name": "wanETH@wanchain",
                        "symbol": "wanETH",
                        "decimals": "18" #to chain decimal
                    }
            '''
            '''
                    {
                        "id": "3",
                        "fromChainID": "2147483708",
                        "fromAccount": "0x514910771af9ca656af840dff83e8264ecf986ca",
                        "toChainID": "2153201998",
                        "toAccount": "0x06da85475f9d2ae79af300de474968cd5a4fde61",
                        "ancestorSymbol": "LINK",
                        "ancestorDecimals": "18",
                        "ancestorAccount": "0x514910771af9ca656af840dff83e8264ecf986ca",
                        "ancestorName": "ChainLink Token",
                        "ancestorChainID": "2147483708",
                        "name": "wanLINK@wanchain",
                        "symbol": "wanLINK",
                        "decimals": "18"
                    }
            '''
            # if chainIDdit.get(tokenPair['fromChainID']): #确保新增链已加入到监控
            #     if tokenPair['toChainID'] not in toBlackList:
            #         asset = tokenPair['ancestorSymbol']
            #         if not assetCCDit.get(asset):  # 如果没有记录，将资产记录到
            #             decimal = tokenPair['ancestorDecimals']
            #             assetCCDit[asset]={}
            #             if tokenPair['ancestorChainID'] == tokenPair['fromChainID']:
            #                 OriginalChain = chainIDdit[tokenPair['ancestorChainID']]
            #                 OriginalChainTokenAddr = tokenPair['fromAccount']
            #                 assetCCDit[asset]['OriginalChain'] = {OriginalChain: OriginalChainTokenAddr}
            #                 assetCCDit[asset]['OriginalChain']['Decimal']= decimal
            #
            #             MapChain = chainIDdit[tokenPair['toChainID']]
            #             MapChainTokenAddr = tokenPair['toAccount']
            #             assetCCDit[asset]['MapChain']={}
            #             assetCCDit[asset]['MapChain'][MapChain] = MapChainTokenAddr
            #             supportMapChains.append(MapChain)
            #
            #         else:  ##如果有记录，进行mapChain信息补充
            #             if tokenPair['ancestorChainID'] == tokenPair['fromChainID']:
            #                 OriginalChain = chainIDdit[tokenPair['ancestorChainID']]
            #                 OriginalChainTokenAddr = tokenPair['fromAccount']
            #                 assetCCDit[asset]['OriginalChain'] = {OriginalChain: OriginalChainTokenAddr}
            #             MapChain = chainIDdit[tokenPair['toChainID']]
            #             MapChainTokenAddr = tokenPair['toAccount']
            #             assetCCDit[asset]['MapChain'][MapChain] = MapChainTokenAddr
            #         supportMapChains.append(MapChain)
            #
            #         if int(tokenPair['id']) in poolTokenList:
            #             assetCCDit[asset]['CCType'] = 'PoolToken'
            #             print(json.dumps(assetCCDit))
            if chainIdDict.get(tokenPair['fromChainID']):# to ensure the new chain has been added to chainInfo(github:https://github.com/Nevquit/configW/blob/main/chainInfos.json)
                asset = tokenPair['ancestorSymbol']
                if not assetCCDit.get(asset):  # 如果没有记录，将资产记录到
                    assetCCDit[asset]={'OriginalChains':{},'MapChain':{}}

                if tokenPair['ancestorChainID'] == tokenPair['fromChainID']:
                    OriginalChain = chainIdDict[tokenPair['ancestorChainID']]
                    assetCCDit[asset]['OriginalChains'][OriginalChain]={'TokenAddr':tokenPair['fromAccount'],'ancestorDecimals': tokenPair['ancestorDecimals']}

                MapChain = chainIdDict[tokenPair['toChainID']]
                assetCCDit[asset]['MapChain'][MapChain] = {'TokenAddr':tokenPair['toAccount'],'decimals':tokenPair['decimals']}
                supportMapChains.append(MapChain)

                if int(tokenPair['id']) in poolTokenIDList:
                    assetCCDit[asset]['CCType'] = 'Pool'

        #delete the original chain from mappchain dic
        for asset,assetDetail in assetCCDit.items():
            oriChains = list(assetDetail['OriginalChains'].keys())
            for chain in oriChains:
                assetDetail['MapChain'].pop(chain,'')
        return assetCCDit,list(set(supportMapChains))


if __name__ == '__main__':
    utl = TokenPairsUtility('main','E:\Automation\github\cross_asset_monitor\.iWAN_config.json',print_flag=True)
    gr = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "groupId": "0x000000000000000000000000000000000000000000000000006465765f303232",
            "status": "5",
            "deposit": "307199999999999999953800",
            "depositWeight": "435649999999999999930700",
            "selectedCount": "25",
            "memberCount": "25",
            "whiteCount": "1",
            "whiteCountAll": "11",
            "startTime": "1623211200",
            "endTime": "1623816000",
            "registerTime": "1623121135",
            "registerDuration": "10875",
            "memberCountDesign": "25",
            "threshold": "17",
            "chain1": "2153201998",
            "chain2": "2147483708",
            "curve1": "1",
            "curve2": "0",
            "tickedCount": "0",
            "minStakeIn": "10000000000000000000000",
            "minDelegateIn": "100000000000000000000",
            "minPartIn": "10000000000000000000000",
            "crossIncoming": "0",
            "gpk1": "0x10b3eb33a8b430561bb38404444c587e47247205771a40969ceabe0c08423ab220b5ddf25f856b71f6bb54cea88bceaa1bbe917f5d903ff82691a345ea4e0556",
            "gpk2": "0xca8ef3a93b2819851e3587dc0906a7e6563ab55ab4f8de76077813df03becc21a9a10957256667fbe3bca2aecd2db0ae5d76b8e8a636dc61e1b960a32b105bdb",
            "delegateFee": "1000"
        }
    }
    print(utl.getassetCCDit())

