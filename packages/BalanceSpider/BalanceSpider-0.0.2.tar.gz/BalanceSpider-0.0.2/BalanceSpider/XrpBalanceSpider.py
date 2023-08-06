import requests
import traceback

class XrpBalanceSpider:
    def __init__(self, print_flag):
        '''
        :param print_flag:
        '''
        self.print_flag = print_flag
        #need update
        self.xrpApiPools = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/xrp_balance_api.json').json()

    def pprint(self,*args,**kwargs):
        if self.print_flag :
            print(*args,**kwargs)

    def getXRPBalance(self,address):
        '''
        :param adress:
        :return: XRP Balance
        '''
        url = self.xrpApiPools['XRP']
        balancePool = []
        try:
            self.pprint('{}/{}'.format(url,address))
            wbdata = requests.get('{}/{}'.format(url,address)).json()
            self.pprint(wbdata)
            balancePool.append(int(float(wbdata['xrpBalance'])*1000000))
            print(balancePool)
            return max(balancePool)
        except Exception:
            print('Get XRP Balance failed due to {}'.format(traceback.format_exc()))


if __name__ == '__main__':
    bb = XrpBalanceSpider(True)
    print(bb.getXRPBalance('rpzp36VUHCzYeTRuuVYGkzzBPAs2p8XK2A'))