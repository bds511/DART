import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup

import re
import pandas as pd
from pandas import Series, DataFrame as df

from __init__ import *



def Craw():
    dart_api("20180822","20180824")#626부터하면됨
    return "완료"



def dart_api(start_date, end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = "016360"
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
    pdfurl = "http://dart.fss.or.kr/pdf/download/pdf.do?rcp_no="+str(rcp_no) +"&dcm_no="+str(dcmno)
    print(url_to_crawl,pdfurl)

    if "파생결합" in soup.text:
        read_url(url_to_crawl, pdfurl)


def read_url(url,pdfurl):
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html , "html.parser")
    q=0
    try:
        for i in range(20):
            a = 0
            file_to_save =""
            file_to_save += str(soup.select("table[width=630]")[i])
            while "최종기준가격 결정일" not in soup.select("table[width=586]")[q].text:
                q += 1
            if "최초기준가격" in soup.select("table[width=586]")[q-1].text and q != 0:
                file_to_save += str(soup.select("table[width=586]")[q-1])
                a = 1
            file_to_save += str(soup.select("table[width=586]")[q])
            #htmlfile = open("삼성공모/" + soup.select("table[width=630]")[i].select('td')[1].text+".html", 'w', encoding='utf-8')
            #htmlfile.write(file_to_save)
            table1 = pd.read_html(file_to_save)[0]
            table1 = table1.loc[:, ~table1.columns.str.contains('^Unnamed')]##셀뭉개지는거 지우기
            table2 = pd.read_html(file_to_save)[1]

            print(a)
            if a==1:
                table3 = pd.read_html(file_to_save)[2]
                table_to_df= pd.concat([table1, table2, table3])
            else:
                table_to_df= pd.concat([table1, table2])
            #table_to_df.to_csv("삼성공모/" + soup.select("table[width=630]")[i].select('td')[1].text+".csv",mode='w', encoding='utf-8-sig')
            #htmlfile.close()
            data_csv2(file_to_save, table_to_df, url,pdfurl)
            q +=1
    except IndexError as e:
        print(e)



def data_csv2(file_to_save, table_to_df, url,pdfurl):
    try:
        date_re = re.compile('\d*년\s\d*월\s\d*일')
        per_re = re.compile("\d*[.]{0,1}\d+%")
        per_re2 = re.compile("\d+[.]\d+%")
        Lizard차_re = re.compile("나.\s.*?(\d)차")
        Lizard수익률_re = re.compile("나.\s.*?(\d+[.]\d+%)")
        발행가액 = re.sub('[^0-9]', '', table_to_df.loc[table_to_df['항   목'].str.contains("발행가액"), '내   용'].values[0])
        발행일 = date_re.search(table_to_df.loc[table_to_df['항   목'] == "발 행 일", '내   용'].values[0]).group()
        발행일 = re.sub(" ", "-", re.sub('[년월일]','',발행일))
        만기수익 = per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("\) 만기상환금액"), '내   용'].values[0])
        Settle_Date_Lags = re.sub('[^0-9]', '', table_to_df.loc[table_to_df['항   목'].str.contains(" 만기상환금액 지급일"), '내   용'].values[0])
        기초자산기준일 = date_re.search(table_to_df.loc[table_to_df['항   목'].str.contains("최초기준가격 결정일"), '내   용'].values[0]).group()
        group_of = ""
        if "중간기준가격" not in file_to_save:
            group_of += "DigitalCall"
        else:
            if "결합사채" in file_to_save:
                group_of += "HiFive"
            else:
                group_of += "StepDn"
            if "하락한계가격" in file_to_save:
                group_of += "_KI"
            else:
                group_of += "_NoKI"
            if "월수익 행사가격" in file_to_save:
                group_of += "_MtlyCpn"
            if "리자드" in file_to_save:
                group_of +="_[Lizard]"
        Structure = group_of
        Neg_Word = ["케어", "만기행사가격 2", "가격변동률2", "참여수익률","상승한계가격","보장수익률"]
        for p in Neg_Word:
            if p in file_to_save:
                Structure = "분류안됨"
        if "만기평가일" in file_to_save: ##만기평가일 대신 만기일만 있는 경우도 많은데.. 띄어쓰기개 한개 혹은 두개 ㅠ...
            만기평가일 = date_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("만기평가일"), '내   용'].values[0])[0]
            if len(date_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("만기평가일"), '내   용'].values[0]))>1:
                Structure +="_만기주의_만종평"
        else:
            만기평가일 = date_re.search(table_to_df.loc[table_to_df['항   목'].str.contains(r'만\s{0,5}기\s{0,5}일'), '내   용'].values[0]).group()
        만기수익률 = None
        if len(만기수익)>1:
            만기수익률 = 만기수익[1]
        if Structure == "DigitalCall":
            만기수익률 += 만기수익[3]

        만기장벽 = None
        if "하락한계가격" in file_to_save:
            만기장벽 = per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("하락한계가격"), '내   용'].values[0])[0]
        Title = table_to_df.loc[table_to_df['항   목'].str.contains("종목명"), '내   용'].values[0]
        print(Title)
        중도상환수익률 =None
        쿠폰Range = None
        쿠폰수익률 = None
        쿠폰평가일 = None
        구간종료일 = None
        print("여기까지")
        if "월수익 행사가격" in file_to_save:
            쿠폰평가일 = date_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("중간기준가격 결정일"), '내   용'].values[0])
            쿠폰평가일 += {만기평가일}
            구간종료일 =[]
            for i in range(1,int(len(쿠폰평가일)/6)+1):
                구간종료일 += {쿠폰평가일[6*i-1]}
            쿠폰Range = per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("월수익 행사가격"), '내   용'].values[0])[0]
            쿠폰수익률 = per_re.search(
                table_to_df.loc[table_to_df['항   목'].str.contains("월수익 금액 및 지급조건"), '내   용'].values[0]).group()
        else:
            if "중간기준가격" in file_to_save:
                구간종료일 = date_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("중간기준가격 결정일"), '내   용'].values[0])
                구간종료일 +={만기평가일}
                중도상환수익률 = per_re2.findall(table_to_df.loc[table_to_df['항   목'].str.contains("자동조기상환조건 및 자동조기상환금액"), '내   용'].values[0])[0]
            else:
                구간종료일 =[만기평가일]
        Lizard차수 = None
        LizardRange= None
        Lizard수익률=None
        print("여기까지2")
        if "2차 리자드 행사가격" in file_to_save:
            Lizard차수 = "1,2"
            LizardRange = str(per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("1차 리자드 행사가격"), '내   용'].values[0])[0])+", "+ str(per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("2차 리자드 행사가격"), '내   용'].values[0])[0])
            if "월수익 행사가격" not in file_to_save:
                Lizard수익률 = per_re2.findall(table_to_df.loc[table_to_df['항   목'].str.contains("자동조기상환조건 및 자동조기상환금액"), '내   용'].values[0])[1] +","+ per_re2.findall(table_to_df.loc[table_to_df['항   목'].str.contains("자동조기상환조건 및 자동조기상환금액"), '내   용'].values[0])[3]
        elif "리자드 행사가격" in file_to_save:
            Lizard차수 = Lizard차_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("자동조기상환조건 및 자동조기상환금액"), '내   용'].values[0])[0]
            LizardRange = per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("리자드 행사가격"), '내   용'].values[0])[0]
            Lizard수익률 = Lizard수익률_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("자동조기상환조건 및 자동조기상환금액"), '내   용'].values[0])[0]
        if "USD" in table_to_df.loc[table_to_df['항   목'].str.contains("발행가액"), '내   용'].values[0].upper():
            화폐단위 = "USD"
        else:
            화폐단위 = "KRW"

        기초자산 = []
        기초자산순서 = {"KOSPI200": "I.101", "HSCEI": "I.HSCE", "HSI": "I.HSI", "S&P500": "I.GSPC", "NKY225": "I.N225",
                  "EUROSTOXX50": "SX5E INDEX", "DAX": "I.GDAXI"}

        뽑아낸기초자산 = re.sub(" ", "",re.sub('\s및', ',', table_to_df.loc[table_to_df['항   목'] == "기초자산", '내   용'].values[0])).split(",")


        for key, val in 기초자산순서.items():
            if key in 뽑아낸기초자산:
                기초자산 += {val}
                뽑아낸기초자산.remove(key)
        for i in 뽑아낸기초자산:
            기초자산 += {i}
        기초자산코드 = 기초자산






        print("여기까지4")
        구간Range =[]

        if ") 행사가격" in file_to_save:
            구간Range += {per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("\) 행사가격"), '내   용'].values[0])[0]}
        else:
            i=0
            if "중간기준가격" in file_to_save:
                중간기준가격 = per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("중간기준가격 결정일 행사가격"), '내   용'].values[0])
                for i in range(1, int(len(중간기준가격) / len(기초자산코드)+1)):
                    구간Range += {중간기준가격[(i - 1) * len(기초자산코드)]}
            if ") 만기행사가격" in file_to_save:
                구간Range += {per_re.findall(table_to_df.loc[table_to_df['항   목'].str.contains("\) 만기행사가격"), '내   용'].values[0])[0]}
        if 중도상환수익률 != None:
            if 만기수익률:
                if abs(len(구간Range) * float(re.sub("%", "", 중도상환수익률)) - float(re.sub("%", "", 만기수익률)))>1:
                    Structure = Structure + "_수익률주의"
        if product.query.filter(product.Title == Title).first():
            wtd = product.query.filter(product.Title == Title).first()
            print("중복상품")
            db.session.delete(wtd)
            db.session.commit()
            add_to_db = product(Title, 발행가액, 발행일, 화폐단위, Structure, Settle_Date_Lags, 기초자산코드, 만기수익률, 만기장벽, 중도상환수익률,
                                Lizard차수, Lizard수익률, LizardRange, 쿠폰수익률, 쿠폰Range, 구간Range, 기초자산기준일, 구간종료일,
                                쿠폰평가일, "삼성증권", url, pdfurl)
            db.session.add(add_to_db)
            db.session.commit()
            print("중복값 업데이트 완료")

        else:
            add_to_db = product(Title, 발행가액, 발행일, 화폐단위, Structure, Settle_Date_Lags,기초자산코드,만기수익률,만기장벽,중도상환수익률,
                                Lizard차수,Lizard수익률,LizardRange,쿠폰수익률,쿠폰Range, 구간Range, 기초자산기준일, 구간종료일,
                                쿠폰평가일,"삼성증권", url, pdfurl)
            db.session.add(add_to_db)
            db.session.commit()

        print("--------------------------------------------------------------------------------------------------------")
    except Exception as ex:
        print("--------------------에러발생:" + str(ex) + "----------------------")
        pass

Craw()