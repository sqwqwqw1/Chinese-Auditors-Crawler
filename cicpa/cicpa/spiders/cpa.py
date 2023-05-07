import scrapy, json
import requests
from typing import Optional
from cicpa.items import CicpaItem


class CpaSpider(scrapy.Spider):
    name = 'cpa'
    allowed_domains = ['cicpa.org.cn']


    # 从[注册会计师行业管理信息系统](https://cmis.cicpa.org.cn/)获取地区对应的ID
    def get_cpa_institute(self):
        url = 'https://cmis.cicpa.org.cn/publicQuery/getAscExcludeZZXList'
        r = requests.post(url)
        return {x['SHORTNAME'][:2]:x['ID'] for x in r.json()['info']}

    # 从[注册会计师行业统一监管平台](http://acc.mof.gov.cn/)获取注册会计师列表
    def get_cpa_list(self):
        url = 'http://acc.mof.gov.cn/searchBfLogin/searchCpaAcct'
        data = {
            'currentPage': '1',
            'pageSize': '999999',
            'cpaStatus': '10',
        }
        r = requests.post(url, data=data)
        return r.json()['list']

    # 提取注册会计师编号，并把地区转换为ID
    def get_asc_and_per(self, cpa, cpaInstitute):
        institute = f'{cpa["DIVISION_NAME"][:2]}'
        ASC_GUID = cpaInstitute[institute]
        PER_CODE = cpa['CPA_CNO']
        return ASC_GUID, PER_CODE


    # 从[注册会计师行业管理信息系统](https://cmis.cicpa.org.cn/)获取注册会计师对应的ID
    # 按列表获取注册会计师对应的ID，用ID发起查询
    def start_requests(self):
        cpaInstitute = self.get_cpa_institute()
        cpaList = self.get_cpa_list()
        url = 'https://cmis.cicpa.org.cn/publicQuery/getCpaListByPage'
        for cpa in cpaList:
            ASC_GUID, PER_CODE = self.get_asc_and_per(cpa, cpaInstitute)
            data = {"OFF_NAME":"",
                "ASC_GUID":ASC_GUID,
                "PER_CODE":PER_CODE,
                "PER_NAME":"",
                "pageNow":1,
                "pageSize":10}
            yield scrapy.Request(url, method="POST", body=json.dumps(data), headers={'Content-Type': 'application/json'}, callback=self.parse_cpa_id)

    def parse_cpa_id(self, response):
        cpaID = response.json()['info']['rows'][0]['ID']
        url = f'https://cmis.cicpa.org.cn/publicQuery/getCpaInfo?id={cpaID}'
        yield scrapy.FormRequest(url, method='POST', callback=self.parse)


    def parse(self, response):
        result = response.json()['info']['headInfo']
        item = CicpaItem()
        for key in result.keys():
            item.fields[key] = key
            item[key] = result[key]
        yield item

