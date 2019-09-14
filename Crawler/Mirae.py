import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup

import re
import pandas as pd
from pandas import Series, DataFrame as df

from __init__ import *



리자드차수_re = re.compile("(\d)차")
date_re = re.compile('\d*년\s\d*월\s\d*일')
per_re3 = re.compile("\d*[.]{0,1}\d*%")
per_re = re.compile("\d*[.]{0,1}\d+%")
per_re2 = re.compile("\d{1,2}[.]\d+%")

def Craw():
    dart_api("20180822","20180824")
    return "완료"


def dart_api(start_date, end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = "006800"
    url = "http://dart.fss.or.kr/api/search.xml?auth="+API_KEY+"&crp_cd="+company_code+"&start_dt="+start_date+"&end_dt="+end_date+"&dsp_tp=C&fin_rpt=Y&series=asc"
    readjson = urlopen(url).read()
    readjson = xmltodict.parse(readjson)
    a = json.dumps(readjson)
    a = json.loads(a)
    num_of_page = a['result']['total_page']
    print(1)
    for y in range(int(num_of_page)):
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
                    get_url(a['result']['list'][i]['rcp_no'])
        except Exception as e:
            print(e)



def get_url(rcp_no):
    url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rcp_no
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html , "html.parser")
    parse_text = soup.text.split("\n")
    text_to_list = parse_text[125]
    dcmno=re.findall(r'\d+', text_to_list)[1]
    url_to_crawl = "http://dart.fss.or.kr/reportKeyword/viewer.do?rcpNo="+str(rcp_no)+"&dcmNo="+str(dcmno)+"&eleId=1&offset=589&length=4225&dtd=dart3.xsd&keyword=1#keyword"
    print(url_to_crawl)
    pdfurl = "http://dart.fss.or.kr/pdf/download/pdf.do?rcp_no=" + str(rcp_no) + "&dcm_no=" + str(dcmno)

    if "파생결합" in soup.text:
        read_url(url_to_crawl,pdfurl)

def read_url(url, pdfurl):

    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html, "html.parser")
    최초기준가격평가일_re =re.compile("최초기준가격평가일 : (\d*년\s\d*월\s\d*일)")
    최종관찰일평가일_re = re.compile("만기평가일 : (\d*년\s\d*월\s\d*일)")
    Month_re = re.compile("○매월 월 수익지급 평가일에.*?(\d{1,2}%)")
    Month_coupon_re = re.compile("월 단위 수익인 (\d[.]\d{1,5}%)")
    Title_re= re.compile("미래에셋대우 제(\d*)회.*?[(](\w{1,3})[)]")
    Settle_re = re.compile("후 (\d)영업일 [(]서울시간 기준[)]")
    q=0
    M=0 #나중에 월지급 수익률, 월수익률 등 셀 용도
    try:
         for i in range(5):
             if "정 정 전" in soup.select("table")[i].text or "정 정 후" in soup.select("table")[i].text:
                 print("정정공시임")
                 soup.select("table")[i].decompose()
                 정정 =1

         for i in range(1,len(soup.select("table[width=622]"))):
            a = 0

            file_to_save =""
            file_to_save += str(soup.select("table[width=622]")[i])

            while "만기상환금액 결정조건" not in soup.select("table")[q].text:
                q += 1
            file_to_save += str(soup.select("table")[q])

            print("안되나?")
            if "자동조기상환평가일" in soup.select("table")[q - 1].text:
                file_to_save += str(soup.select("table")[q-2])
                file_to_save += str(soup.select("table")[q-1])
                print("여기까지됨2")
                if "월수익지급평가일" in soup.select("table")[q - 3].text:
                    file_to_save += str(soup.select("table")[q-3])
            print(1)

            file_to_save += str(최초기준가격평가일_re.findall(soup.text)[i - 1])
            file_to_save += str(최종관찰일평가일_re.findall(soup.text)[i - 1])
            first_day = str(최초기준가격평가일_re.findall(soup.text)[i - 1])
            last_day = str(최종관찰일평가일_re.findall(soup.text)[i - 1])

            Title= "미래에셋대우(" + Title_re.findall(soup.select("table[width=622]")[0].text)[i-1][1]+")"+Title_re.findall(soup.select("table[width=622]")[0].text)[i-1][0]
            print(Title)

            if "퇴직" in soup.text:
                file_to_save  += "퇴직"
            if "월수익지급평가일" in soup.select("table")[q - 3].text:
                month_range= Month_re.findall(soup.text)[M]
                Month_coupon = Month_coupon_re.findall(soup.text)[M]
                q+=1
                M+=1

                save_to_db(file_to_save, Title, first_day, last_day,  url, pdfurl, month_range=month_range, Month_coupon=Month_coupon)
            else:
                q+=1
                save_to_db(file_to_save,Title, first_day, last_day,url, pdfurl)
    except Exception as e:
        print("--------------------"+str(e)+"---------------------------")

def save_to_db(html,Title,first_day,last_day, url, pdfurl,month_range = None, Month_coupon=None):
    soup = BeautifulSoup(html, "html.parser")
    print("여기까지됨")
    table= soup.find_all("table")
    기초자산 = re.sub(" ", "", re.sub(" / ", ",", re.sub("지수", "", get_td(table[0], 1, "기초자산")))).split(",")
    기초자산코드 = []
    기초자산순서= {"KOSPI200":"I.101","HSCEI":"I.HSCE","HSI":"I.HSI", "S&P500":"I.GSPC","NIKKEI225":"I.N225", "EUROSTOXX50":"SX5E INDEX", "DAX" : "I.GDAXI"}
    for key, val in 기초자산순서.items():
        if key in 기초자산:
            기초자산코드 +={val}
            기초자산.remove(key)
    for i in 기초자산:
        기초자산코드 +={i}


    if "USD" in get_td(table[0], 1, "발행가액").upper():
        화폐단위 = "USD"
    else:
        화폐단위 = "KRW"
    발행가액 = re.sub('[^0-9]', '', get_td(table[0],1,"발행가액"))
    발행일 = str(get_td(table[0],1,"발 행 일"))
    발행일 = re.sub(" ", "-", re.sub('[년월일]', '', 발행일))
    기초자산기준일 = first_day
    print("여기")
    Settle_Date_Lags = 0
    if "자동조기상환일" in soup.text:
        Settle_Date_Lags = re.sub('[^0-9]', '',get_td(table[0],1,"자동조기상환일"))
    print("여기")
    쿠폰수익률 = None
    쿠폰Range = None
    쿠폰평가일 = []
    if month_range:
        쿠폰Range = month_range
        쿠폰수익률 = Month_coupon
        for i in range(len(table[4].tbody.find_all('tr'))):
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,1)).group()}
        for i in range(len(table[4].tbody.find_all('tr'))):
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,3)).group()}
    구간Range = []
    #구간Range +=  {per_re.search(get_xy(table[1],0,0)).group()}
    Lizard차수= None
    LizardRange = None
    Lizard수익률 = None
    만기수익률 = None
    구간종료일 = []
    중도상환수익률 = None
    if len(table)>3:
        Lizard차수= get_lizard_차수(table[2])
        LizardRange = get_lizard_range(table[2])
        Lizard수익률 = get_lizard_profit(table[3])
        구간Range +=  get_non_lizard_range(table[2])
        구간종료일 += get_date(table[3])
        중도상환수익률 = per_re2.search(get_xy(table[3],0,2)).group()

    구간Range += {per_re.search(get_xy(table[1], 0, 0)).group()}
    구간종료일 += [last_day]
    if per_re2.search(get_xy(table[1], 0, 1)):
        만기수익률 = per_re2.search(get_xy(table[1], 0, 1)).group()
    만기장벽 = None
    if "어느 하나도 각 최초기준가격의" in get_xy(table[1],1,0) or "미만으로 하락한 적이 없는 경우" in get_xy(table[1],1,0):
        만기장벽 = per_re.search(get_xy(table[1], 1, 0)).group()
        if per_re2.search(get_xy(table[1],1,1)).group() != 만기수익률:
            만기장벽 += "장벽주의, (수익률 : " +per_re2.search(get_xy(table[1],1,1)).group() +")"

    상품구조 =""
    if "사채" in soup.text:
        if "조기상환" in soup.text:
            상품구조 +="HiFive"
        else:
            상품구조 +="DigitalCall"
            만기수익률 = str(만기수익률) +","+ str(per_re2.search(get_xy(table[1], 1, 1)).group())
    else:
        상품구조 +="StepDn"
    if 상품구조 != "DigitalCall":
        if 만기장벽:
            상품구조 +="_KI"
        else:
            상품구조 +="_NoKI"
        if Lizard차수:
            상품구조 +="_[Lizard]"
        if month_range:
            상품구조 +="_MtlyCpn"
    elif "퇴직"in soup.text:
        상품구조 +="_퇴직"
    if "평균" in soup.text:
        상품구조 += "_Average"
    if "기초자산 하락률 x 100%" in soup.text:
        상품구조 += "_eagle"
    if "그 중 어느" in soup.text:
        상품구조 += "_만기주의"
        if len(table)<3:
            상품구조 = "Range"
    if "초과하여 상승한 적이 없는 경우" in soup.text:
        상품구조 = "양방향KO"
    Structure = 상품구조

    if 중도상환수익률 != None:
        if 만기수익률:
            if abs(len(구간Range) * float(re.sub("%", "", 중도상환수익률)) - float(re.sub("%", "", 만기수익률))) > 1:
                Structure = Structure + "_수익률주의"

    if Settle_Date_Lags =='':
        print("settleDateLags에러인듯")
        Settle_Date_Lags = "0"
    if product.query.filter(product.Title == Title).first():
        print("중복상품")
        wtd = product.query.filter(product.Title == Title).first()
        db.session.delete(wtd)
        db.session.commit()
    add_to_db = product(Title, 발행가액, 발행일, 화폐단위, Structure, Settle_Date_Lags, 기초자산코드, 만기수익률, 만기장벽, 중도상환수익률,
                        Lizard차수, Lizard수익률, LizardRange, 쿠폰수익률, 쿠폰Range, 구간Range, 기초자산기준일, 구간종료일,
                        쿠폰평가일, "미래에셋대우", url, pdfurl)
    db.session.add(add_to_db)
    db.session.commit()


    return "abc"



def get_td(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in tds[0].text:
            return tds[col].text


def get_list(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in tds[0].text:
            return list(tds[col].stripped_strings)

def get_xy(table, row, col):
    trs = table.tbody.find_all("tr")
    tr = trs[row]
    tr = tr.find_all('td')
    td = tr[col]
    return td.text

def get_lizard_차수(table):
    리자드차수 = ""
    차수=""
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')[0].text
        if len(tds)<3:
            차수 = 리자드차수_re.search(tds).group(1)
        else:
            리자드차수 += 차수
    return 리자드차수

def get_non_lizard_range(table):
    range_list =[]
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')
        if len(tds[0].text)<3:
            range_list += {per_re.search(tds[1].text).group()}
    return range_list


def get_lizard_range(table):
    range_list =""
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')
        if len(tds[0].text)>3:
            range_list += per_re.search(tds[0].text).group()
    return range_list

def get_date(table):
    range_list =[]
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')
        if len(tds[0].text)<3:
            range_list += {date_re.search(tds[1].text).group()}
    return range_list

def get_lizard_profit(table):
    range_list =""
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')
        if len(tds[0].text)>3:
            range_list += per_re2.search(tds[0].text).group()
    return range_list




Craw()







