import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import Series, DataFrame as df
import datetime

from __init__ import *

data_index1 = ["발행일", "발행사","Type","차수", "pdfurl"]

new_df = df(index=data_index1)



def dart_api(코드, 회사명,start_date, end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = str(코드)
    url = "http://dart.fss.or.kr/api/search.xml?auth="+API_KEY+"&crp_cd="+company_code+"&start_dt="+start_date+"&end_dt="+end_date+"&dsp_tp=C&fin_rpt=Y&series=asc"
    readjson = urlopen(url).read()
    readjson = xmltodict.parse(readjson)
    a = json.dumps(readjson)
    a = json.loads(a)
    print(a)
    num_of_page = a['result']['total_page']
    print(num_of_page)
    print(1)
    for y in range(int(num_of_page)):
        print(1)
        page_no = y+1
        new_url = "http://dart.fss.or.kr/api/search.xml?auth="+API_KEY+"&crp_cd="+company_code+"&start_dt="+start_date+"&end_dt="+end_date+"&dsp_tp=C&fin_rpt=Y&series=asc&page_no="+str(int(page_no))
        readjson = urlopen(new_url).read()
        readjson = xmltodict.parse(readjson)
        a = json.dumps(readjson)
        a = json.loads(a)
        try:
            for i in range(10):
                print(a['result']['list'][i])
                if '투자설명서' in a['result']['list'][i]['rpt_nm']:
                    get_url(a['result']['list'][i]['rcp_no'], str(코드), 회사명)
        except Exception as e:
            print("####무슨에러:"+str(e)+"####")

def get_url(rcp_no,코드,회사명):
    url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rcp_no
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html , "html.parser")
    parse_text = soup.text.split("\n")
    text_to_list = parse_text[125]
    dcmno=re.findall(r'\d+', text_to_list)[1]
    url_to_crawl = "http://dart.fss.or.kr/reportKeyword/viewer.do?rcpNo="+str(rcp_no)+"&dcmNo="+str(dcmno)+"&eleId=1&offset=589&length=4225&dtd=dart3.xsd&keyword=1#keyword"
    pdf_url= "http://dart.fss.or.kr/pdf/download/pdf.do?rcp_no=" + str(rcp_no) + "&dcm_no=" + str(dcmno)
    print(url_to_crawl)
    if "파생결합" in soup.text:
        read_url(url_to_crawl, pdf_url,회사명)

def read_url(url,pdf_url,회사명):
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html, "html.parser")
    try:
        if not "(주식워런트증권" in soup.text or "신영증권" in soup.text or "메리츠" in soup.text:
             for i in range(5):
                 if "정 정 전" in soup.select("table")[i].text:
                     print("정정공시임")
                     soup.select("table")[i].decompose()
             for i in range(len(soup.select("table"))):##
                if "종목명" in soup.select("table")[i].text or "증권의 종류" in soup.select("table")[i].text or ("모집총액" in soup.select("table")[i].text and not "삼성증권" in soup.text):
                    table = soup.select("table")[i]
                    print("여까지됨")

                    ##삼성증권에서는 밑에게 문제
                    title = re.sub("\n","",soup.select("table")[i].select('td')[1].text)

                    if "메리츠" in  table.text or "신영" in  table.text or "키움" in  table.text:
                        title = str(get_td(table, 1, "종목명"))

                    add_to_url = save_url()

                    add_to_url.차수 = re.sub('[^0-9]', '', title)
                    add_to_url.Title = title
                    if "기타" in title:
                        add_to_url.Type = "DLS"
                    else:
                        add_to_url.Type = "ELS"
                    print(title)
                    발행일 = str(get_td(table, 1, "발행일"))
                    add_to_url.발행일 = re.sub(" ", "-", re.sub('[년월일]', '', 발행일))
                    print(add_to_url.발행일)
                    add_to_url.발행사 = 회사명
                    add_to_url.url = pdf_url

                    if add_to_url.발행일 != None and add_to_url.발행일 != "None" :
                        if save_url.query.filter(save_url.Title == title).first():
                            print("중복상품")
                            wtd = save_url.query.filter(save_url.Title == title).first()
                            db.session.delete(wtd)
                            db.session.commit()
                        db.session.add(add_to_url)
                        db.session.commit()
    except Exception as e:
        print("---------------------"+str(e)+"-------------------")



def get_td(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        #print(str(tds[0].text))
        if txt in re.sub('\s', '', str(tds[0].text)):
            return re.sub("\n",'',re.sub("\]","",re.sub("\[","",tds[col].text)))
회사코드 = {'016360': '삼성증권' , '003540': '대신증권', '006800': '미래에셋대우', '008670': "신한금융투자", '030610':"교보증권",'003470': "유안타증권",'003530': '한화투자증권',
        '005940': 'NH투자증권','00160144': '한국투자증권','003450': 'KB증권','001720': '신영증권','00113465': '하나금융투자','00684918': 'IBK투자증권','001500': '현대차투자증권','039490':'키움증권','001200': '유진투자증권',
        '016610':'DB금융투자','008560':"메리츠종금증권",'001510':'SK증권','00148665':'하이투자증권'}
#회사코드 = ['016360', '003540', '006800', '008670', '030610','003470','003530','005940','00160144','003450','001720','00113465','00684918','001500','039490','001200','016610','008560','001510','00148665']
#회사코드 = ['016360']
#회사코드 = {'001720': '신영증권', '008560':"메리츠종금증권",'001510':'SK증권'}

def Craw(start_date,end_date):
    for key,val in 회사코드.items():
        dart_api(key,val)
for key,val in 회사코드.items():
    dart_api(key,val,"20180822","20180824")
#new_df.transpose().to_csv("url_list2.csv",mode='w', encoding='utf-8-sig')

#주식워런트증구권빼도록 하자 - 신영 메리츠
