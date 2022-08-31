# -*- coding: utf-8 -*-
from scrapy.exporters import JsonLinesItemExporter
from audit.items import NwperItem, CpaItem, ProfileItem, FirmItem

class AuditPipeline(object):
    def __init__(self):
        self.NwperItem_fp = open('nwp_info.json', 'wb')
        self.CpaItem_fp = open('cpa_info.json', 'wb')
        self.ProfileItem_fp = open('cpa_profile.json', 'wb')
        self.FirmItem_fp = open('audit_firm.json', 'wb')
        self.NwperItem_exporter = JsonLinesItemExporter(self.NwperItem_fp, ensure_ascii=False)
        self.CpaItem_exporter = JsonLinesItemExporter(self.CpaItem_fp, ensure_ascii=False)
        self.ProfileItem_exporter = JsonLinesItemExporter(self.ProfileItem_fp, ensure_ascii=False)
        self.FirmItem_exporter = JsonLinesItemExporter(self.FirmItem_fp, ensure_ascii=False)


    def process_item(self, item, spider):
        if isinstance(item, NwperItem):
            self.NwperItem_exporter.export_item(item)

        if isinstance(item, CpaItem):
            self.CpaItem_exporter.export_item(item)

        if isinstance(item, FirmItem):
            self.FirmItem_exporter.export_item(item)

        if isinstance(item, ProfileItem):
            self.ProfileItem_exporter.export_item(item)


