from iWAN import iWAN #pip install iWAN
import json
import time
from iWAN_Request import iWAN_Request

class StoremanUtility:
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
    def getWorkingGroupsIds(self):
        '''
        get working storemanGroups status ==5
        :return: groupIDs:list
        '''
        working_groupIds = []
        rsp_dic = self.iwan.sendRequest(iWAN_Request.getGroupID())['result']
        for gr in rsp_dic:
            if int(gr['status']) == 5 and time.time() >= int(gr['startTime']):
                working_groupIds.append(gr['groupId'])
        return working_groupIds
    def getWorkingGroupsDetails(self):
        '''
        get working storemanGroups
        :return: groups: list
        '''
        working_groups = []
        rsp_dic = self.iwan.sendRequest(iWAN_Request.getGroupID())['result']
        for gr in rsp_dic:
            if int(gr['status']) == 5 and time.time() >= int(gr['startTime']):
                working_groups.append(gr)
        return working_groups
    def getReadyGroups(self):
        '''
        get working storemanGroups
        :url: iwan url
        :return:
        '''
        ready_groupIDs = []
        rsp_dic = self.iwan.sendRequest(iWAN_Request.getGroupID())['result']
        for gr in rsp_dic:
            if int(gr['status']) == 5:
                ready_groupIDs.append(gr['groupId'])
        return ready_groupIDs
    def getStoremanCandidates(self):
        '''
        get the candidats for not ready storemanGroups
        :param:
        :return:
        '''
        notReadyGrs = []
        Candidates = []
        groups = self.iwan.sendRequest(iWAN_Request.getGroupID())['result']
        for gr in groups:
            if int(gr['status']) < 5:
                notReadyGrs.append(gr['groupId'])
        for grID in notReadyGrs:
            Candidates.extend(self.iwan.sendRequest(iWAN_Request.getStoremanCandidates(grID))['result'])
        return Candidates
    def getNotReadyStmGrs(self):
        '''
                0：none,
            1：initial,
            2：curveSeted,
            3：failed,
            4：selected,
            5：ready,
            6：unregistered,
            7：dismissed
        :return:notReadyGrs : dict {'GroupID':'GroupInfo'}
        '''
        notReadyGrs = []
        notReadyGrIDs = []
        groups = self.iwan.sendRequest(iWAN_Request.getGroupID())['result']
        for gr in groups:
            if int(gr['status']) < 5:
                notReadyGrs.append(gr)
                notReadyGrIDs.append(gr['groupId'])
        return dict(zip(notReadyGrIDs, notReadyGrs))
    def getCandidatesPerGr(self, grID):
        '''
        :param iwan:
        :param grID:
        :return: candidates:list
        '''
        Candidates = self.iwan.sendRequest(iWAN_Request.getSelectedStoreman(grID))['result']
        return Candidates
    def getGroupStatus(self,statusID):
        dict = {1: 'Initial', 2: 'CurveSeted', 3: 'Failed', 4: 'Selected', 5: 'Ready', 6: 'Unregistered',
                7: 'Dismissed'}
        return dict.get(statusID, 'Invalid statusID-{}'.format(statusID))

if __name__ == '__main__':
    utl = StoremanUtility('main','E:\Automation\github\cross_asset_monitor\.iWAN_config.json',print_flag=True)
    print(utl.getWorkingGroupsDetails())