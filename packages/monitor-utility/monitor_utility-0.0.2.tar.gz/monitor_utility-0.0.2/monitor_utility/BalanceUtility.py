from iWAN import iWAN #pip install iWAN
import json
from iWAN_Request import iWAN_Request
from BalanceSpider import BtcBalanceSpider,XrpBalanceSpider
import requests
import traceback
from substrateinterface import SubstrateInterface # for DOT RPC
from websocket import create_connection

class BalanceUtility:
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
    def getEVMChainCoinBalanceViaIwan(self,account, chain):
        '''
        :param account:
        :param chain:
        :return:
        {"jsonrpc": "2.0", "id": 1, "result": "63063269117771397923"} #wei
        '''
        result = self.iwan.sendRequest(iWAN_Request.getBalance(account, chain))
        return result
    def getEVMChainTokenBalanceViaIwan(self,chainType,account, tokenScAddr):
        '''

        :param chainType:
        :param account:
        :param tokenScAddr:
        :return:
        {"jsonrpc": "2.0", "id": 1, "result": "44390"} #wei
        '''
        result = self.iwan.sendRequest(iWAN_Request.getTokenBalance(chainType, account, tokenScAddr))
        return result
    def getBTCsBalanceViaNode(self,node,user,password,address):
        '''
        :param node BTC/LTC/DOGE
        :return: str
        '''
        url = node
        balance = 0
        headers = {"Content-Type": "application/json"}
        method = json.dumps(
            {"jsonrpc": "1.0", "id": "curltest", "method": "listunspent", "params": [1, 99999999, [address]]})
        try:
            rsp = requests.post(url=url, auth=(user, password), headers=headers, data=method).json()
            for utxo in rsp['result']:
                balance += utxo['amount']
            return int(balance * 100000000)
        except Exception:
            print(traceback.format_exc())
    def getBTCsBalanceViaIwan(self,chainType, Addr):
        '''

        :param BTC/LTC/DOGE:
        :param Addr:
        :return: amount staoshi
        '''

        try:
            amount = 0
            totalSupply = self.iwan.sendRequest(iWAN_Request.getBTCUTXO(chainType, Addr))
            for tx in totalSupply['result']:
                amount += float(tx['amount'])
            return int(amount*100000000)
        except:
            return
    def getBTCsBalance(self,chain,node,user,password,address):
        '''
        get the balance from node,iwan,third part data
        :param chain:
        :param address:
        :return:
        '''
        balancePool = []
        balance_iWAN = self.getBTCsBalanceViaIwan(chain, address)
        if balance_iWAN:
            balancePool.append(balance_iWAN)

        if self.net == 'main':
            try:
                balance_spider = BtcBalanceSpider.BtcBalanceSpider().getBTCBalance(chain,address)
            except:
                balance_spider = None
            if balance_spider:
                balancePool.append(balance_spider)
        balance_Node = self.getBTCsBalanceViaNode(node,user,password,address)
        if balance_Node:
            balancePool.append(balance_Node)
        if balancePool:
            amt = max(balancePool,key=balancePool.count)
            self.pprint(balancePool)
            return amt
        self.pprint(balancePool)
    def getDOTBalanceViaNode(self, url, dotAddress):
        '''
        '''
        try:
            substrate = SubstrateInterface(url=url)
            result = substrate.query(
                module='System',
                storage_function='Account',
                params=[dotAddress]
            )
            return result.value['data']['free']  # unit wei
        except:
            return
    def getDOTBalance(self, nodes:list,dotAddress):
        '''
        :param nodes: [node1,node2,node3,...]
        :param dotAddress:
        :return:
        '''
        balancePool = []
        urls = nodes
        for url in urls:
            balance = self.getDOTBalanceViaNode(url, dotAddress)
            if balance:
                balancePool.append(int(balance))
        if balancePool:
            return max(balancePool, key=balancePool.count)
    def getXRPBalanceViaNode(self, url, xrpAddress):
        data = {
            "id": 2,
            "command": "account_info",
            "account": xrpAddress,
            "strict": True,
            "ledger_index": "current",
            "queue": True
        }
        try:
            ws = create_connection(url=url, timeout=30)
            ws.send(json.dumps(data))
            r_raw = json.loads(ws.recv())
            ws.close()
            self.pprint('{} : {} '.format(url, r_raw))
            balance = r_raw['result']['account_data']['Balance']
            '''
                {
                    "result": {
                        "account_data": {
                            "Account": "rpzp36VUHCzYeTRuuVYGkzzBPAs2p8XK2A",
                            "Balance": "22601014",
                            "Flags": 0,
                            "LedgerEntryType": "AccountRoot",
                            "OwnerCount": 0,
                            "PreviousTxnID": "8AB9C836D1BC09CD561E6C6BD4C99ACDD60FF2D8724AB0A31627AEE21C231578",
                            "PreviousTxnLgrSeq": 64438977,
                            "Sequence": 62845237,
                            "index": "058D902BB05287733CA576D81A9629545128CE641D5C9868F8ACCE7E4E8F8DA1"
                        },
                        "ledger_current_index": 64441144,
                        "queue_data": {
                            "txn_count": 0
                        },
                        "status": "success",
                        "validated": false
                    }
                }
            '''
            self.pprint('{} : {} '.format(url, balance))
            return balance
        except Exception:
            self.pprint('{} : {} '.format(url,traceback.format_exc()))
    def getXRPBalance(self,nodes:list,xrpAddress):
        '''
        curl - H
        'Content-Type: application/json' - d
        '{"method":"account_info","params":[{"account":"rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn","strict":true,"ledger_index":"current","queue":true}]}'
        :param: nodes
        '''

        balance_pool = []
        urls = nodes
        for url in urls:
            balance = self.getXRPBalanceViaNode(url,xrpAddress)
            if balance:
                balance_pool.append(balance)
        if self.net =='main':
            try:
                xrpbalance_spider = XrpBalanceSpider.XrpBalanceSpider().getXRPBalance(xrpAddress)
            except:
                self.pprint('xrpbalance_spider get failed due to {}'.format(traceback.format_exc()))
                xrpbalance_spider = None

            if xrpbalance_spider:
                balance_pool.append(xrpbalance_spider)
        if balance_pool:
            self.pprint(balance_pool)
            return max(balance_pool,key=balance_pool.count) #to avoid get 0 balance



if __name__ == '__main__':
    utl = BalanceUtility('main','E:\Automation\github\cross_asset_monitor\.iWAN_config.json',print_flag=True)
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

