import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup

import re
import pandas as pd
from pandas import Series, DataFrame as df

from __init__ import *

def Craw():
    dart_api("20180822","20180824")
    return "완료"

def dart_api(start_date, end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = "008670"
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
    최초기준가격평가일_re =re.compile("최초기준가격평가일 :(\d*년\s\d*월\s\d*일)")
    최종관찰일평가일_re = re.compile("만기평가일 : (\d*년\s\d*월\s\d*일)")
    Month_re = re.compile("매월 수익지급 평가일에 각 기초자산의 월수익지급평가가격이 모두 최초기준가격의 (\d*[.]{0,1}\d+%)")
    Month_profit_re = re.compile("(0[.]\d*%)[(]세전[)]")
    지급일_re = re.compile("최종관찰일\(불포함\) 후 (\d)영업일\)")
    Title_re = re.compile("신한.*?[)]")
    q=0
    p=0
    M=0 #나중에 월지급 수익률, 월수익률 등 셀 용도
    try:
         for i in range(5):
             if "정 정 전" in soup.select("table")[i].text:
                 print("정정공시임")
                 soup.select("table")[i].decompose()
         for i in range(len(soup.select("table[width=617]"))):
            if "종목명" in soup.select("table[width=617]")[i].text:
                a = 0
                month_range = 0
                file_to_save =""
                file_to_save += str(soup.select("table[width=617]")[i])
                while "만기상환금액 결정조건" not in soup.select("table")[q].text:
                    q += 1
                print(1)
                file_to_save += str(soup.select("table")[q])
                if "자동조기상환평가일" in soup.select("table")[q - 1].text:
                    file_to_save += str(soup.select("table")[q-2])
                    file_to_save += str(soup.select("table")[q-1])
                    print(1)
                    if "평가일자" in soup.select("table")[q - 3].text:
                        file_to_save += str(soup.select("table")[q-3])
                        month_range =Month_re.findall(soup.text)[M]
                        month_profit= Month_profit_re.findall(soup.text)[M]
                        M+=1
                        file_to_save += "<br>월수익레인지 :" +str(month_range)
                        file_to_save += "<br>월수익 :" + str(month_profit)
                file_to_save += "<br>최초기준가평가일 :" +str(최초기준가격평가일_re.findall(soup.text)[p])
                file_to_save += "<br>최종기준가평가일 :" + str(최종관찰일평가일_re.findall(soup.text)[p])
                first_day = str(최초기준가격평가일_re.findall(soup.text)[p])
                last_day = str(최종관찰일평가일_re.findall(soup.text)[p])
                #settle_lag = str(지급일_re.findall(soup.text)[i-1])
                if "퇴직" in soup.text:
                    file_to_save += "퇴직"
                Title= Title_re.search(soup.select("table[width=617]")[i].text).group()
                print(Title)
                print("2")
                q+=1
                p+=1
                if month_range == 0:
                    save_to_csv(file_to_save, first_day, last_day, Title, url, pdfurl)
                else:
                    save_to_csv(file_to_save, first_day, last_day, Title, url, pdfurl, month_range = month_range, month_profit = month_profit)


    except Exception as e:
        print("---------------------"+str(e)+"-------------------")

def save_to_csv(html,first_day, last_day, Title, url, pdfurl, month_range = None, month_profit = None):
    date_re = re.compile('\d*년\s*?\d*월\s*?\d*일')
    per_re = re.compile("\d*[.]{0,1}\d+%")
    per_re2 = re.compile("\d{1,2}[.]\d+%")
    lizard_re =re.compile("(\d)-2차")
    range_re = re.compile("(\d)차")
    영업일_re = re.compile("(\d)영업일")
    soup = BeautifulSoup(html, "html.parser")
    table= soup.find_all("table")
    리자드_range_re = re.compile("(\d*%)미만으로 하락한적이 없는경우[(]종가기준[)]")
    기초자산코드 = []
    기초자산 =[]
    기초자산순서 = {"KOSPI200":"I.101","HSCEI":"I.HSCE","HSI":"I.HSI", "S&P500":"I.GSPC","NIKKEI225":"I.N225", "EUROSTOXX50":"SX5E INDEX", "DAX" : "I.GDAXI"}
    뽑아낸기초자산 =  re.sub("\s","",re.sub("&nbps;","",re.sub("[(].*?[)]","",re.sub("&amp;","",(re.sub(" ","",re.sub("지수","",get_td(table[0], 1, "기초자산")))))))).split("/")
    for key, val in 기초자산순서.items():
        if key in 뽑아낸기초자산:
            기초자산 +={val}
            뽑아낸기초자산.remove(key)
    for i in 뽑아낸기초자산:
        기초자산 +={i}
    for idx, val in enumerate(기초자산):
        기초자산코드 += {val}

    발행가액 = re.sub('[^0-9]', '', get_td(table[0],1,"발행가액"))
    if "US" in get_td(table[0],1,"발행가액").upper():
        화폐단위 = "US"
    else:
        화폐단위 = "KRW"
    발행일 = str(get_like_td(table[0],1,"발행일"))
    발행일 = re.sub(" ", "-", re.sub('[년월일]', '', 발행일))

    Settle_Date_Lags = None

    if 영업일_re.search(soup.text):
        Settle_Date_Lags = str(영업일_re.search(soup.text).group(1))
    기초자산기준일 = first_day

    만기장벽 = None
    만기수익률 = None
    if per_re2.search(get_xy(table[1], 0, 1)):
        만기수익률 = per_re2.search(get_xy(table[1], 0, 1)).group()
        if per_re2.search(get_xy(table[1], 1, 1)):
            if per_re2.search(get_xy(table[1], 0, 1)).group() == per_re2.search(get_xy(table[1], 1, 1)).group():
                만기장벽 = per_re.search(get_xy(table[1], 1, 0)).group()



    Lizard차수 = None
    LizardRange = None
    Lizard수익률 = None
    구간Range = []
    중도상환수익률=None
    구간종료일 = []
    if len(table)>2:
        구간Range = []
        for i in range(len(table[2].tbody.find_all('tr'))):
            if 리자드_range_re.search(get_xy(table[2],i,1)):
                if LizardRange == None:
                    LizardRange =""
                    Lizard수익률 = ""
                    Lizard차수 = ""
                LizardRange += str(리자드_range_re.search(get_xy(table[2],i,1)).group(1))
            구간Range += {str(per_re.search(get_xy(table[2], i, 1)).group())}


        if per_re2.search(get_xy(table[3], 0, 2)):
            중도상환수익률 = str(per_re2.search(get_xy(table[3], 0, 2)).group())
        else:
            try:
                if per_re2.search(get_xy(table[3], 0, 3)):
                    중도상환수익률 = str(per_re2.search(get_xy(table[3], 0, 3)).group())
            except IndexError:
                print("수익률0인듯")
        print("여기까지되나2")
        for i in range(len(table[3].tbody.find_all('tr'))):
            if len(get_xy(table[3],i,0))<4:
                if date_re.search(get_xy(table[3], i, 1)):
                    구간종료일 += {date_re.search(get_xy(table[3], i, 1)).group()}
                #else:
                #    new_series["구간종료일" + str(차수2)] = 0
            else:
                Lizard차수 += range_re.search(get_xy(table[3], i, 0)).group(1)
                if per_re2.search(get_xy(table[3], i, 1)):
                    Lizard수익률 += str(per_re2.search(get_xy(table[3], i, 1)).group())

    print("여기까지되나")
    구간종료일 += {last_day}
    구간Range += {str(per_re.search(get_xy(table[1], 0, 0)).group())}


    쿠폰Range= None
    쿠폰수익률 = None
    쿠폰평가일 = None

    if len(table)>4:
        쿠폰Range = month_range
        쿠폰수익률 = month_profit
        쿠폰평가일 = []
        for i in range(len(table[4].tbody.find_all('tr'))):
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,1)).group()}
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,3)).group()}
            쿠폰평가일 += {date_re.search(get_xy(table[4],i,5)).group()}

    print("여기까지되나3")


    상품구조 =""
    if "사채" in soup.text:
        if "조기상환" in soup.text:
            상품구조 +="HiFive"
        else:
            상품구조 +="DigitalCall"
    else:
        상품구조 +="StepDn"
    if 상품구조 != "DigitalCall":
        if 만기장벽:
            상품구조 +="_KI"
        else:
            상품구조 +="_NoKI"
        if Lizard차수 != None:
            상품구조 +="_[Lizard]"
        if len(table)>4:
            상품구조 +="_MtlyCpn"
    elif "퇴직"in soup.text:
        상품구조 +="_퇴직"


    print("여기까지되나4")
    if len(구간Range)>2 and not "Mtly" in 상품구조:
        if  int(float(re.sub("%","",만기수익률))) != int(float(re.sub("%","",중도상환수익률))*len(구간Range)):
            상품구조 += "_수익률주의"
    Neg_Word = ['% 이하인 경우', '비율의 평균이', '원금부분지급', '있더라도']
    for i in Neg_Word:
        if i in soup.text:
            상품구조 = "분류안됨"
    Structure = 상품구조


    print("여기까지되나5")
    if product.query.filter(product.Title == Title).first():
        print("중복상품")
        wtd = product.query.filter(product.Title == Title).first()
        db.session.delete(wtd)
        db.session.commit()
    add_to_db = product(Title, 발행가액, 발행일, 화폐단위, Structure, Settle_Date_Lags, 기초자산코드, 만기수익률, 만기장벽, 중도상환수익률,
                        Lizard차수, Lizard수익률, LizardRange, 쿠폰수익률, 쿠폰Range, 구간Range, 기초자산기준일, 구간종료일,
                        쿠폰평가일, "신한금융투자", url, pdfurl)

    db.session.add(add_to_db)
    db.session.commit()





def get_td(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in tds[0].text:
            return tds[col].text

def get_like_td(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in re.sub("\s","",tds[0].text):
            return tds[col].text


def get_list(table, col, txt):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if txt in tds[0].text:
            return str(tds[col].stripped_strings)


def get_xy(table, row, col):
    trs = table.tbody.find_all("tr")
    tr = trs[row]
    tr = tr.find_all('td')
    td = tr[col]
    return td.text

def df_plus(idx, val,Series1):
    s1 = pd.Series([val], index= [idx])
    Series1.append(s1)

Craw()