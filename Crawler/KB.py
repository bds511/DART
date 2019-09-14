import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import re
import pandas as pd
from pandas import Series, DataFrame as df

from __init__ import *


리자드차수_re = re.compile("(\d)차")
date_re = re.compile('\d*년\s\d*월\s\d*일')
per_re = re.compile("\d*[.]{0,1}\d+%")
per_re2 = re.compile("\d{1,2}[.]\d+%")
Settle_re = re.compile('(\d)\s*영업일')

def Craw():
    dart_api("20180822","20180824")
    return "완료"

def dart_api(start_date,end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = "003450"
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
                    get_url(a['result']['list'][i]['rcp_no'])
        except Exception as e:
            print("####무슨에러:"+str(e)+"####")

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

def read_url(url,pdfurl):
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html, "html.parser")
    최초기준가격평가일_re =re.compile("최초기준가격평가일 :\s{0,2}(\d*년\s\d*월\s\d*일)")
    최종관찰일평가일_re = re.compile("최종관찰일 :\s{0,2}(\d*년\s\d*월\s\d*일)")
    만기평가일_re = re.compile("만기평가일 :\s{0,2}(\d*년\s\d*월\s\d*일)")
    Month_re = re.compile("월수익지급평가가격이 각 최초기준가격의 (\d{1,2}%)")
    Month_coupon_re = re.compile("× (0[.]\d{1,5}%)[(]연")
    Title_re= re.compile("KB.*?호")
    q=0

    M=0 #나중에 월지급 수익률, 월수익률 등 셀 용도
    try:
         for i in range(5):
             if "정 정 전" in soup.select("table")[i].text:
                 print("정정공시임")
                 soup.select("table")[i].decompose()

         #for i in soup.find_all("table",{"width": "411"}):
         #    i.decompose()

         a = 0
         for i in range(len(soup.select("table[width=624]"))):
            if "모집총액" in soup.select("table[width=624]")[i].text:
                file_to_save =""
                file_to_save += str(soup.select("table[width=624]")[i])
                while "만기상환금액 결정조건" not in soup.select("table")[q].text:
                    q += 1
                file_to_save += str(soup.select("table")[q])
                if "평가일자" in soup.select("table")[q - 1].text:
                    file_to_save += str(soup.select("table")[q-3])
                    file_to_save += str(soup.select("table")[q-2])
                    file_to_save += str(soup.select("table")[q - 1])
                if "자동조기상환평가일" in soup.select("table")[q - 1].text:
                    file_to_save += str(soup.select("table")[q-2])
                    file_to_save += str(soup.select("table")[q-1])
                print(1)
                file_to_save += str(최초기준가격평가일_re.findall(soup.text)[a])
                first_day = str(최초기준가격평가일_re.findall(soup.text)[a])
                if 최종관찰일평가일_re.search(soup.text):
                    file_to_save += str(최종관찰일평가일_re.findall(soup.text)[a])
                    last_day = str(최종관찰일평가일_re.findall(soup.text)[a])
                else:
                    if 만기평가일_re.search(soup.text):
                        file_to_save += str(만기평가일_re.findall(soup.text)[a])
                        last_day = str(만기평가일_re.findall(soup.text)[a])
                a+=1

                print(i)
                Title = Title_re.search(soup.select("table[width=624]")[i].select('td')[1].text).group()
                print(Title)
                if "퇴직" in soup.text:
                    file_to_save += "퇴직"
                if "종가의 산술평균" in soup.text:
                    file_to_save += "_종평"
                print(i)

                print("---------------------------")

                if "평가일자" in soup.select("table")[q - 1].text:
                    print("월수익이네")
                    month_range= Month_re.findall(soup.text)[M]
                    print("레인지확인")
                    Month_coupon = Month_coupon_re.findall(soup.text)[M]
                    q+=1
                    M+=1
                    save_to_csv(file_to_save, Title, first_day, last_day, url, pdfurl,  month_range=month_range, Month_coupon=Month_coupon)
                else:
                    q+=1
                    save_to_csv(file_to_save,Title, first_day, last_day, url, pdfurl)


    except Exception as e:
        print("--------------------"+str(e)+"---------------------------")

def save_to_csv(html,Title,first_day,last_day,url, pdfurl,month_range = None, Month_coupon=None):

    soup = BeautifulSoup(html, "html.parser")
    table= soup.find_all("table")
    lizard_re =re.compile("(\d)-2차")
    range_re = re.compile("(\d)차")
    리자드_range_re = re.compile("(\d*%) 미만으로 하락한 적이 없는 경우[(]종가기준[)]")


    기초자산 =[]
    기초자산순서 = {"KOSPI200":"I.101","HSCEI":"I.HSCE","HSI":"I.HSI", "S&P500":"I.GSPC","NIKKEI225":"I.N225", "EUROSTOXX50":"SX5E INDEX", "DAX" : "I.GDAXI"}

    뽑아낸기초자산 = re.sub("\s","",re.sub("지수","",get_td(table[0], 1, "기초자산"))).split("/")
    for key, val in 기초자산순서.items():
        if key in 뽑아낸기초자산:
            기초자산 +={val}
            뽑아낸기초자산.remove(key)
    for i in 뽑아낸기초자산:
        기초자산 +={i}
    기초자산코드 = 기초자산

    if "USD" in get_td(table[0],1,"발행가액").upper():
        화폐단위 = "USD"
    else:
        화폐단위 = "KRW"

    발행가액 =  re.sub('[^0-9]', '', get_td(table[0],1,"발행가액"))
    발행일 = str(get_td(table[0],1,"발 행 일"))
    발행일 = re.sub(" ", "-", re.sub('[년월일]', '', 발행일))

    기초자산기준일 = first_day
    쿠폰Range= None
    쿠폰수익률=None
    쿠폰평가일 = None
    if month_range:
        쿠폰Range = month_range
        쿠폰수익률 = Month_coupon
        쿠폰평가일 =[]
        for i in range(len(table[4].tbody.find_all('tr'))):
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,1)).group()}
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,3)).group()}
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,5)).group()}

    구간Range = [per_re.search(get_xy(table[1],0,0)).group()]
    구간종료일 = [last_day]

    Settle_Date_Lags = None
    if Settle_re.search(soup.text):
        Settle_Date_Lags = Settle_re.search(soup.text).group(1)
    print("이까지됨")

    중도상환수익률 = None
    Lizard차수 = None
    LizardRange =None
    Lizard수익률 = None

    if len(table)>3:
        Lizard차수 = get_lizard_차수(table[3])
        LizardRange = get_lizard_range(table[2])
        Lizard수익률 = get_lizard_profit(table[3])

        #if not month_range:
        구간Range = get_non_lizard_range(table[2])
        구간Range += {per_re.search(get_xy(table[1], 0, 0)).group()}
        구간종료일 = get_date(table[3])

        구간종료일 += {last_day}
        print("이까지됨2")
        if not month_range:
            if per_re2.search(get_xy(table[3],0,2)):
                중도상환수익률= per_re2.search(get_xy(table[3],0,2)).group()
            else:
                if per_re2.search(get_xy(table[3], 0,3)):
                    중도상환수익률 = per_re2.search(get_xy(table[3], 0, 3)).group()
    만기수익률 = None
    if per_re2.search(get_xy(table[1], 0, 1)):
        만기수익률 = per_re2.search(get_xy(table[1], 0, 1)).group()

    만기장벽 = None
    if "미만으로 하락한 적이 없는 경우" in get_xy(table[1],1,0):
        만기장벽 = per_re.search(get_xy(table[1], 1, 0)).group()
        if not month_range:
            if per_re2.search(get_xy(table[1],1,1)).group() != 만기수익률:
                만기장벽 = str(만기장벽) +"(수익률 : " +per_re2.search(get_xy(table[1],1,1)).group() +")"

    상품구조 =""
    if "사채" in soup.text:
        if len(구간Range)>2 :
            상품구조 +="HiFive"
        else:
            if "이하에 있는 경우" in soup.text:
                상품구조 = "UOC"
            else:
                상품구조 +="DigitalCall"
                만기수익률 = str(만기수익률)+", "+str(per_re2.search(get_xy(table[1], 1, 1)).group())
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
    Structure = 상품구조
    if 중도상환수익률 != None:
        if abs(len(구간Range) * float(re.sub("%", "", 중도상환수익률)) - float(re.sub("%", "", 만기수익률))) > 1:
            Structure = Structure + "_수익률주의"
    if "종평" in soup.text:
        Structure += "종평"
    print("여기까지")
    print(Title)
    if product.query.filter(product.Title == Title).first():
        print("중복상품")
        wtd = product.query.filter(product.Title == Title).first()
        db.session.delete(wtd)
        db.session.commit()
    add_to_db = product(Title, 발행가액, 발행일, 화폐단위, Structure, Settle_Date_Lags, 기초자산코드, 만기수익률, 만기장벽, 중도상환수익률,
                        Lizard차수, Lizard수익률, LizardRange, 쿠폰수익률, 쿠폰Range, 구간Range, 기초자산기준일, 구간종료일,
                        쿠폰평가일, "KB증권", url, pdfurl)
    db.session.add(add_to_db)
    db.session.commit()

def get_td(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in tds[0].prettify(formatter=lambda s: s.replace(u'\xa0', ' ')):
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
        range_list += {per_re.findall(tds[1].text)[0]}
    return range_list


def get_lizard_range(table):
    range_list =""
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds= tr.find_all('td')
        if len(per_re.findall(tds[1].text))>1:
            range_list += per_re.findall(tds[1].text)[1]
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
            range_list += per_re2.search(tds[1].text).group()
    return range_list


Craw()