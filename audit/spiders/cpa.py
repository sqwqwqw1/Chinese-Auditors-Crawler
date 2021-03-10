# -*- coding: utf-8 -*-
import scrapy, re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from audit.items import NwperItem, CpaItem, ProfileItem, FirmItem
import requests

class CpaSpider(CrawlSpider):
    name = 'cpa'
    allowed_domains = ['cicpa.org.cn']
    query_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/OfficeIndexAction.do'

    def get_firm_url(value):
        offGuid = re.search("javascript:viewDetail\(\'(.*?)\'", value)
        if offGuid:
            firm_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/09/' + offGuid.group(1) + '.shtml'
            return firm_url

    def get_sub_firm_url(value):
        offGuid = re.search("getSubOffice\(\'(.*?)\'", value)
        if offGuid:
            firm_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/09/' + offGuid.group(1) + '.shtml'
            return firm_url

    def get_nwper_url(value):
        offGuid = re.search("getNwPers\(\'(.*?)\'", value)
        if offGuid:
            nwper_list_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/public/query/swscyry/%20/' + offGuid.group(1) + '.html'
            return nwper_list_url

    def get_cpa_url(value):
        offGuid = re.search("getPersons\(\'(.*?)\'", value)
        if offGuid:
            cpa_list_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/public/query/swszs/%20/' + offGuid.group(1) + '.html'
            return cpa_list_url

    rules = (
        Rule(LinkExtractor(process_value=get_firm_url), callback="parse_firm_page", follow=True),
        Rule(LinkExtractor(attrs='onclick', process_value=get_sub_firm_url), callback="parse_firm_page", follow=True),
        Rule(LinkExtractor(attrs='onclick', process_value=get_nwper_url), callback="parse_nwper_page", follow=False),
        Rule(LinkExtractor(attrs='onclick', process_value=get_cpa_url), callback="parse_cpa_page", follow=False), 
    )

    def start_requests(self):
        acc_url = 'http://acc.mof.gov.cn/searchBfLogin/searchCpaCpaf'
        acc_data = {
            'currentPage': '1',
            'pageSize': '20',
            'cpafCno': '',
            'cpafName': '',
            'cpafStatus': '11',
            'cpaNumBegin': '',
            'cpaNumEnd': '',
            'orgForm': ''
        }
        r = requests.post(acc_url, data=acc_data)
        pages = r.json()['pages']+1
        for i in range(1,pages):
            acc_data = {
                'currentPage': str(i),
                'pageSize': '20',
                'cpafCno': '',
                'cpafName': '',
                'cpafStatus': '11',
                'cpaNumBegin': '',
                'cpaNumEnd': '',
                'orgForm': ''
            }
            r = requests.post(acc_url, data=acc_data)
            li = r.json()['list']
            for office in li:
                data = {
                        'pageSize': '',
                        'pageNum': '',
                        'method': 'indexQuery',
                        'queryType': '1',
                        'isStock': '00',
                        'offName': '',
                        'ascGuid': '',
                        # 'offAllcode': offAllcode
                        'offAllcode': office['CPAF_CNO']
                    }
                yield scrapy.FormRequest(self.query_url, formdata=data)

    #采集事务所信息
    def parse_firm_page(self, response):
        table = response.xpath('.//table[@class="detail_table"]')
        tdls = table.xpath('.//td[@class="tdl"]')
        tdcs = table.xpath('.//td[@class="data_tb_content"]')
        item = FirmItem()
        for i in range(len(tdls)):
            label = re.sub('\s|（请点击）', '', ''.join(tdls[i].xpath('.//text()').getall()))
            content = re.sub('\s|（请点击）', '', ''.join(tdcs[i].xpath('.//text()').getall()))
            if label != '':
                item.fields[label] = scrapy.Field()
                item[label] = content
        yield item


    #采集从业人员信息
    def parse_nwper_page(self, response):
        offGuid = re.search(r'.+/([A-Z0-9]+)\.html', response.url).group(1)
        page_info = ''.join(response.xpath('.//div[@id="pageDiv"]//text()').getall())
        total_page = re.search(' 共(.+?)页', page_info)
        if total_page:
            total_page = re.search(' 共(.+?)页', page_info).group(1).strip()
            for page in range(1, int(total_page)+1):
                data = {
                        'method': 'getEmployeeList',
                        'offGuid': str(offGuid),
                        'pageNum': str(page),
                        'pageSize': '',
                        }
                yield scrapy.FormRequest(self.query_url, formdata=data, callback=self.get_nwper_info)

    def get_nwper_info(self, response):
        table = response.xpath('.//table[@id="nwp"]')
        trs = table.xpath('.//tr')
        firm = re.sub('\s', '', ''.join(trs[0].xpath('.//text()').getall()))
        columns = trs[1].xpath('.//th/text()').getall()
        for tr in trs[2:]:
            info = tr.xpath('.//td/text()').getall()
            item = NwperItem()
            item.fields['所在事务所'] = scrapy.Field()
            item['所在事务所'] = firm
            for i in range(len(info)):
                label = columns[i]
                content = re.sub('\s', '', info[i])
                item.fields[label] = scrapy.Field()
                item[label] = content
            yield item


    #采集cpa列表
    def parse_cpa_page(self, response):
        offGuid = re.search(r'.+/([A-Z0-9]+)\.html', response.url).group(1)
        page_info = ''.join(response.xpath('.//div[@id="pageDiv"]//text()').getall())
        total_page = re.search(' 共(.+?)页', page_info)
        if total_page:
            total_page = re.search(' 共(.+?)页', page_info).group(1).strip()
            for page in range(1, int(total_page)+1):
                data = {
                        'method': 'getPersons',
                        'offGuid': str(offGuid),
                        'pageNum': str(page),
                        'pageSize': '',
                        }
                yield scrapy.FormRequest(self.query_url, formdata=data, callback=self.get_cpa_info)

    def get_cpa_info(self, response):
        table = response.xpath('.//table[@class="detail_table"]')
        trs = table.xpath('.//tr')
        firm = re.sub('\s', '', ''.join(trs[0].xpath('.//text()').getall()))
        columns = trs[2].xpath('.//th/text()').getall()
        for tr in trs[3:]:
            info = tr.xpath('.//td')
            item = CpaItem()
            item.fields['所在事务所'] = scrapy.Field()
            item['所在事务所'] = firm
            for i in range(len(info)):
                label = columns[i]
                content = re.sub('\s', '', ''.join(info[i].xpath('.//text()').getall()))
                item.fields[label] = scrapy.Field()
                item[label] = content
            yield item
            PerGuid = re.search("getPerDetails\('(.*?)\'", re.sub('\s', '', ''.join(info[1].xpath('.//@onclick').getall()))).group(1)
            profile_url = 'https://cmispub.cicpa.org.cn/cicpa2_web/07/' + PerGuid + '.shtml'
            yield scrapy.Request(profile_url, callback=self.parse_profile_page)

    #采集cpa简介
    def parse_profile_page(self, response):
        table = response.xpath('.//table[@class="detail_table"]')
        tdls = table.xpath('.//td[@class="tdl"]')
        tdcs = table.xpath('.//td[@class="data_tb_content"]')
        item = ProfileItem()
        for i in range(len(tdls)):
            label = re.sub('\s', '', ''.join(tdls[i].xpath('.//text()').getall()))
            content = re.sub('\s', '', ''.join(tdcs[i].xpath('.//text()').getall()))
            if label != '':
                item.fields[label] = scrapy.Field()
                item[label] = content
        yield item
