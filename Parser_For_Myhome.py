from bs4 import BeautifulSoup
import urllib.request as web
from urllib import parse
import random
import time
import requests
import json
import re
from datetime import datetime
import sys
import csv

startTime = datetime.now()


real_proxy_list = ['104.198.32.133:80','185.108.198.38:8080','88.159.222.201:80','162.243.124.117:8080']
proxy_support = web.ProxyHandler({'http' : '%s'%(random.choice(real_proxy_list))})

opener = web.build_opener(proxy_support)
web.install_opener(opener)

def please_find_cadastral_code_for_me(Longtitude,Latitude):
    #dissabling proxy for gov
    proxy_support = web.ProxyHandler({})
    opener = web.build_opener(proxy_support)
    web.install_opener(opener)
    cad_url = 'http://maps.napr.gov.ge/GetCadobjIdByXy?_dc=' + str(time.time()).split('.')[0] + '&x_in=' + str(
        Longtitude) + '&y_in=' + str(Latitude)
    try:
        print(cad_url,' = cad_url')
        Cadastrial_HTML = web.urlopen(cad_url, timeout=4)
        soup = BeautifulSoup(Cadastrial_HTML, "html.parser")
        Cadastrial_Code = soup.find("td", text="საკ. კოდი:").find_next_sibling("td").text
        print(Cadastrial_Code)
        Separator_list.append(Cadastrial_Code)
        Separator_list.append('Yes')

    except AttributeError:
        Cadastrial_Code = "None" # No cadastrial code for this lon lat
        Separator_list.append(Cadastrial_Code)
        Separator_list.append('Checked')


def filter_html_for_address_text_and_cadastrial(ready_link,latitude,longtitude):
    ready_html = web.urlopen(ready_link)
    eat_html = BeautifulSoup(ready_html,'html.parser')

    try:
        address_data = eat_html.find('div',{'id':'pr_loc_block'})
        more_info =[]
        for row in address_data.find_all("span",{'class':'text_16'}):
            more_info.append(row.text)
        more_info = ', '.join(more_info)

    except AttributeError:
        more_info = "None Address TEXT"


    Separator_list.append(more_info) #Addresstext


    cadastral_info = eat_html.find('div',{'class':'pr_dt_info'})
    code_cadastral = cadastral_info.find_all('a')

    if not code_cadastral:
        if longtitude == '' or longtitude == 'None' or longitude == None:
            Separator_list.append('None')
            Separator_list.append('No')
        else:
            please_find_cadastral_code_for_me(longtitude, latitude)
    else:
        for link in code_cadastral:
            code_cadastral = link.text
        Separator_list.append(code_cadastral)
        Separator_list.append('No')


def WriteListToCSV(csv_file,csv_columns,data_list):
    try:
        with open(csv_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow(csv_columns)
            for data in data_list:
                writer.writerow(data)
    except IOError:
            print("Cannot Create File give me permission maaan")
    return



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
           'X-Requested-With': 'XMLHttpRequest',
           'Host': 'www.myhome.ge',
           'Content-Encoding':'gzip',
           'Referer': 'https://www.myhome.ge/ka/search?geo_search=on&scroll_top=0&pr_grid_id=1&page=2'}


the_amount_of_pages_I_want_to_parse = pages = 100

csv_columns = ['SourceKey','Post_Url', 'SourceId',
               'CreateDate','Deal_Type',
               'Price','Area','CurrencyId',
               'AddressText','CadastralCode','From_Gov',
               'Lat','Long','Description',]

csv_file = 'collected_information_myhome.csv'


Latest_Data = []


while int(the_amount_of_pages_I_want_to_parse) != 0:
    data = parse.urlencode({
        'geo_search': 'on',
        'scroll_top': '0',
        'pr_grid_id': '1',
        'page':  "%d" % (the_amount_of_pages_I_want_to_parse),
    }).encode()
    the_amount_of_pages_I_want_to_parse -= 1
    req = web.Request('https://www.myhome.ge/block/get_products.php', data=data, headers=headers, method='POST')
    resp = web.urlopen(req).read().decode('utf-8-sig')
    j_data = json.loads(resp)

    for each in j_data['products']:
        Separator_list = [ ]
        Separator_list.append('MYHOME') #SourceKey
        ready_link = 'https://www.myhome.ge/ka/product?id=' + each['product_id']
        latitude = each['map_lat']
        longitude = each['map_lon']
        Separator_list.append(ready_link) #Post_Url
        Separator_list.append(each['product_id']) #SourceId
        Separator_list.append(each['order_date']) #CreateDate
        Separator_list.append(each['adtype_id']) #Deal_Type
        Separator_list.append(each['price']) #Price
        Separator_list.append(each['area_size']) #Area
        Separator_list.append(each['currency_id']) #CurrencyId
        #for address text and cadastrial code
        filter_html_for_address_text_and_cadastrial(ready_link,latitude,longitude)
        Separator_list.append(each['map_lat']) #Lat
        Separator_list.append(each['map_lon']) #Long
        Separator_list.append(each['comment']) #Description


        Latest_Data.append(Separator_list)



WriteListToCSV(csv_file,csv_columns,Latest_Data)


print(" The amount of pages  = ", pages,'\n',
      "The time I used      = ", datetime.now() - startTime)

