import requests
from lxml import etree
import traceback

class BtcBalanceSpider:
    def __init__(self, print_flag):
        '''
        :param print_flag:
        '''
        self.print_flag = print_flag
        #need update
        self.btcURLPools = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/btc_balance_spider_url_pool.json').json()
        self.btcApiPools = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/btc_balance_api.json').json()

    def pprint(self,*args,**kwargs):
        if self.print_flag :
            print(*args,**kwargs)

    def _getBTCBalanceViaPage(self,chain, adress):
        url_pool = self.btcURLPools
        balancePool = []
        for url,xpath in url_pool[chain].items():
            try:
                wbdata = requests.get('{}{}'.format(url, adress)).text
                selector = etree.HTML(wbdata)
                ret = selector.xpath('{}/text()'.format(xpath))
                self.pprint('Blance for {}{}: {}'.format(url, adress, ret))
                # print('{}{}:::{}'.format(url,adress,ret))
                balance = float(ret[0].replace(chain, '').replace(',', '').replace('\n            ', '').replace(' ', ''))
                balancePool.append(int(balance * 100000000))
            except Exception:
                print('Featch balance failed for {}, due to {}'.format(url,traceback.format_exc()))
        return balancePool
    def _getBTCBalanceViaApi(self,chain,address):
        '''
        :param chain:
        :param address:
        :return: balance pool, unit btc
        '''
        url_pool = self.btcApiPools
        balancePool = []
        try:
            if chain == 'BTC':
                for name,url in url_pool[chain].items():
                    if name == 'blockchain.info':
                        try:
                            rsp = requests.get(url.format(address)).text
                            balancePool.append(int(rsp))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain,name,traceback.format_exc()))
                    if name == 'chain.so':
                        try:
                            rsp = requests.get(url.format(address)).json()['data']['confirmed_balance']
                            balancePool.append(int(float(rsp)*100000000))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain, name, traceback.format_exc()))
            if chain == 'LTC':
                for name,url in url_pool[chain].items():
                    if name == 'chain.so':
                        try:
                            rsp = requests.get(url.format(address)).json()['data']['confirmed_balance']
                            balancePool.append(int(float(rsp)*100000000))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain, name, traceback.format_exc()))
                    if name == 'api.blockcypher':
                        try:
                            rsp = requests.get(url.format(address)).json()['balance']
                            balancePool.append(int(rsp))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain, name, traceback.format_exc()))
            if chain == 'DOGE':
                for name,url in url_pool[chain].items():
                    if name == 'chain.so':
                        try:
                            rsp = requests.get(url.format(address)).json()['data']['confirmed_balance']
                            balancePool.append(int(float(rsp)*100000000))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain, name, traceback.format_exc()))
                    if name == 'api.blockcypher':
                        try:
                            rsp = requests.get(url.format(address)).json()['balance']
                            balancePool.append(int(rsp))
                        except  Exception:
                            print('Get {} balance from {} failed with {}'.format(chain, name, traceback.format_exc()))
            if balancePool:
                return balancePool
        except Exception:
            print('Get BTC Balance failed due to {}'.format(traceback.format_exc()))

    def getBTCBalance(self,chain,address):
        '''
        :param urlPool: {'BTC':{url1:xpath1,url2:xpath2},'LTC':{url1:xpath1,url2:xpath2}}
        :return: BTC Balance, unit BTC
        '''
        balancePool=[]

        #Get balance from html
        # print('Get balance from html')
        balance_page = self._getBTCBalanceViaPage(chain,address)
        if balance_page:
            balancePool.extend(balance_page)

        #Get balance from third api
        # print('Get balance from third api')
        balance_api = self._getBTCBalanceViaApi(chain,address)
        if balance_api:
            balancePool.extend(balance_api)
        if balancePool:
            # print(balancePool)
            return max(balancePool,key=balancePool.count)

if __name__ == '__main__':
    bb = BtcBalanceSpider(False)
    # print(bb._getBTCBalanceViaPage('BTC',"https://www.blockchain.com/btc/address/","/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div[6]/div[2]/span",'1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY'))
    # print(bb._getBTCBalanceViaPage('LTC',"https://litecoinblockexplorer.net/address/","/html/body/main/div/div[1]/div/div/div/div/div[4]/p[2]",'LTCPodha2LAxSyBGsGfkWcmKDEB8cWrqLU'))
    # print(bb._getBTCBalanceViaPage('DOGE',"https://dogeblocks.com/address/","/html/body/main/div/div[1]/div/div/div/div/div[4]/p[2]",'DMr3fEiVrPWFpoCWS958zNtqgnFb7QWn9D'))
    # print(bb._getBTCBalanceViaApi('BTC','1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY'))
    print(bb.getBTCBalance('BTC','1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY'))