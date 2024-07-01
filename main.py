import ipaddress
import os
import platform
import subprocess
import time

import geoip2.database
import requests


class IpExtractor(object):
    def extract(self, ips_json):
        pass


class CloudFrontExtractor(IpExtractor):
    def extract(self, ips_json):
        res = []
        with geoip2.database.Reader('db/GeoLite2-Country.mmdb') as reader:
            for ips in ips_json['CLOUDFRONT_GLOBAL_IP_LIST'] + ips_json['CLOUDFRONT_REGIONAL_EDGE_IP_LIST']:
                ip = ipaddress.ip_network(ips)[0]
                response = reader.country(ip)
                # print(ip, '-', response.country.iso_code)
                if response.country.iso_code != 'CN':
                    res.append(ips)
        return res


def getCloudflareRelativePath():
    if platform.system() not in ['Darwin', 'Linux']:
        raise Exception('Not Supported OS')
    return 'bin/{}'.format(platform.system())


def update(ip_extractor):
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '获取cloudfront最新IP')
    ip_url = os.getenv('ip_url', default="https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips")
    response = requests.get(ip_url)
    ips = ip_extractor().extract(response.json())
    if len(ips) == 0:
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), "未找到可用IP")
    # 更新IP列表至文件
    with open('/tmp/ip.txt', 'w') as f:
        for ip in ips:
            f.write(ip + '\r\n')
    # 执行CloudflareST，进行测速优选
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '进行cloudfront IP优选')
    st = subprocess.Popen(['./CloudflareST', '-f', '/tmp/ip.txt',
                           '-n', '1000',
                           '-tl', '100',
                           '-p', '0',
                           '-dd',
                           "-p", "10",
                           "-o", ""],
                          cwd=getCloudflareRelativePath(), stdout=None)
    st.wait()
    # # 调用 CloudFlora API，更新 DNS 记录
    # update_dns_record(domain, record_name, bestCDNIP['IP 地址'], api_key, email)


update(CloudFrontExtractor)
