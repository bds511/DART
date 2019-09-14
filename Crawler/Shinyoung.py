import json, xmltodict
from urllib.request import urlopen
from bs4 import BeautifulSoup

import re



from __init__ import *

def Craw():
    dart_api("20180822","20180824")
    return "완료"

def dart_api(start_date, end_date):
    API_KEY = "a9c0511d113ccb73c6ccef7e823fea22010e65c6"
    company_code = "001720"
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
        read_url(url_to_crawl, pdfurl)




def read_url(url, pdfurl):
    req = urlopen(url)
    html = req.read()
    soup = BeautifulSoup(html, "html.parser")
    최초기준가격평가일_re =re.compile("최초기준가격평가일.*?:.*?(\d*년\s\d*월\s\d*일)",re.DOTALL|re.MULTILINE)
    #최종관찰일평가일_re = re.compile("만기상환평가일.*?:.*?(20\d\d.*?일)",re.DOTALL|re.MULTILINE)
    최종관찰일평가일_re = re.compile("만기상환평가일 :.*?(20\d.*?일)", re.DOTALL | re.MULTILINE)
    Month_re = re.compile("쿠폰지급평가가격이.*?(\d{1,2}%)")
    지급일_re = re.compile("만기상환평가일\(불포함\) 후 (\d)영업일\)")
    Title_re = re.compile("신영.*?[)]")
    q=0
    M=0 #나중에 월지급 수익률, 월수익률 등 셀 용도
    try:

         for i in range(5):
             if "정 정 전" in soup.select("table")[i].text:
                 print("정정공시임")
                 soup.select("table")[i].decompose()
         for i in range(len(soup.select("table[width=678]"))):
            a = 0
            file_to_save =""
            file_to_save += str(soup.select("table[width=678]")[i])
            while "만기상환금액 결정조건" not in soup.select("table[border=1]")[q].text:
                q += 1


            file_to_save += str(soup.select("table[border=1]")[q])
            if "쿠폰지급평가일" in soup.select("table[border=1]")[q-1].text:
                file_to_save += str(soup.select("table[border=1]")[q-3])
                file_to_save += str(soup.select("table[border=1]")[q-2])
                file_to_save += str(soup.select("table[border=1]")[q-1])
            if "자동조기상환평가일" in soup.select("table[border=1]")[q - 1].text:
                file_to_save += str(soup.select("table[border=1]")[q-2])
                file_to_save += str(soup.select("table[border=1]")[q-1])
            print(1)
            file_to_save += "최초기준가평가일 :" +str(최초기준가격평가일_re.findall(soup.text)[i])
            file_to_save += "최종기준가평가일 :" + str(최종관찰일평가일_re.findall(soup.text)[i])
            first_day = str(최초기준가격평가일_re.findall(soup.text)[i])
            last_day = str(최종관찰일평가일_re.findall(soup.text)[i])

            if "퇴직" in soup.text:
                file_to_save += "퇴직"
            Title = Title_re.search(soup.select("table[width=678]")[i].select('td')[3].text).group()
            print(Title)
            if "쿠폰지급평가일" in soup.select("table[border=1]")[q - 1].text:
                month_range= Month_re.findall(soup.text)[M]
                q+=1
                M+=1
                file_to_save += "쿠폰지급조건 :" +str(month_range)

                save_to_csv(file_to_save, first_day, last_day, Title, url, pdfurl, month_range=month_range)
            else:
                q+=1
                save_to_csv(file_to_save, first_day, last_day, Title, url, pdfurl)

    except Exception as e:
        print("---------------------"+str(e)+"-------------------")

def save_to_csv(html, first_day, last_day, Title, url, pdfurl, month_range=None):

    date_re = re.compile('\d*년\s\d*월\s\d*일')
    per_re = re.compile("\d*[.]{0,1}\d+%")
    per_re2 = re.compile("\d{1,2}[.]\d+%")
    lizard_re = re.compile("(\d)-2차")
    range_re = re.compile("(\d)(-1){0,1}차")
    영업일_re = re.compile("(\d)영업일")

    if product.query.filter(product.Title == Title).first():
        print("중복상품")
        wtd = product.query.filter(product.Title == Title).first()
        db.session.delete(wtd)
        db.session.commit()
    add_to_db = product(Title)
    add_to_db.Issure = "신영증권"
    add_to_db.OAddress = url
    add_to_db.PDFAddress = pdfurl
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")
    기초자산 = []
    기초자산순서 = {"KOSPI200": "I.101", "HSCEI": "I.HSCE", "HSI": "I.HSI", "S&P500": "I.GSPC", "NIKKEI225": "I.N225",
              "EuroStoxx50": "SX5E INDEX", "DAX": "I.GDAXI"}
    뽑아낸기초자산 = re.sub("지수", "", re.sub(" ", "", get_list(table[0], 1, "기초자산"))).split("/")
    for key, val in 기초자산순서.items():
        if key in 뽑아낸기초자산:
            기초자산 += {val}
            뽑아낸기초자산.remove(key)
    for i in 뽑아낸기초자산:
        기초자산 += {i}

    add_to_db.기초자산 = 기초자산

    add_to_db.발행가액 = re.sub('[^0-9]', '', get_td(table[0], 1, "발행가액"))
    if "USD" in get_td(table[0], 1, "발행가액").upper():
        add_to_db.화폐단위 = "USD"
    else:
        add_to_db.화폐단위 = "KRW"

    add_to_db.발행일 = re.sub(" ", "-", re.sub('[년월일]', '',str(get_td(table[0], 1, "발 행 일"))))

    add_to_db.Settle_Date_Lags = str(영업일_re.search(soup.text).group(1))
    add_to_db.기초자산기준일 = first_day
    print(1)
    만기장벽 = False
    if per_re2.search(get_xy(table[1], 0, 1)):
        add_to_db.만기수익률 = per_re2.search(get_xy(table[1], 0, 1)).group()
    if per_re2.search(get_xy(table[1], 1, 1)):
        if per_re2.search(get_xy(table[1], 0, 1)).group() == per_re2.search(get_xy(table[1], 1, 1)).group():
            add_to_db.만기장벽 = per_re.search(get_xy(table[1], 1, 0)).group()
            만기장벽 = True
    print(1)

    구간종료일 = []
    차수 = 1
    if len(table) > 2:
        리자드차수 = ""
        리자드레인지 = ""
        리자드수익률 = ""
        구간Range = []
        for i in range(len(table[2].tbody.find_all('tr'))):
            if lizard_re.search(get_xy(table[2], i, 0)):
                리자드차수 += str(lizard_re.search(get_xy(table[2], i, 0)).group(1))
                리자드레인지 += str(per_re.search(get_xy(table[2], i, 1)).group())
                리자드수익률 += str(per_re2.search(get_xy(table[3], i, 2)).group())
            else:
                구간Range += {str(per_re.search(get_xy(table[2], i, 1)).group())}
                구간종료일 += {str(date_re.search(get_xy(table[3], i, 1)).group())}
                차수 += 1
        구간Range += {str(per_re.search(get_xy(table[1], 0, 0)).group())}
        if not month_range:
            add_to_db.중도상환수익률 = str(per_re2.search(get_xy(table[3], 0, 2)).group())
        if 리자드차수 != "":
            add_to_db.Lizard차수= 리자드차수
            add_to_db.Lizard수익률= 리자드수익률
            add_to_db.LizardRange = 리자드레인지
        add_to_db.구간Range = 구간Range



    구간종료일 += {last_day}
    add_to_db.구간종료일 = 구간종료일
    if month_range:
        add_to_db.쿠폰Range = month_range

        add_to_db.쿠폰수익률 = str(per_re.search(get_xy(table[4], 1, 2)).group())
        쿠폰평가일 = []
        if "차수" in get_xy(table[4], 0, 0):
            for i in range(1, len(table[4].tbody.find_all('tr'))):
                쿠폰평가일 += {date_re.search(get_xy(table[4], i, 1)).group()}
            for i in range(1, len(table[4].tbody.find_all('tr'))):
                쿠폰평가일 += {date_re.search(get_xy(table[4], i, 4)).group()}
        else:
            for i in range(len(table[4].tbody.find_all('tr'))):
                쿠폰평가일 += {date_re.search(get_xy(table[4], i, 1)).group()}
            for i in range(len(table[4].tbody.find_all('tr'))):
                쿠폰평가일 += {date_re.search(get_xy(table[4], i, 4)).group()}
        add_to_db.쿠폰평가일 = 쿠폰평가일

    상품구조 = ""
    if "사채" in soup.text:
        if "조기상환" in soup.text:
            상품구조 += "HiFive"
        else:
            상품구조 += "DigitalCall"
    else:
        상품구조 += "StepDn"

    if 상품구조 != "DigitalCall":
        if 만기장벽:
            상품구조 += "_KI"
        else:
            상품구조 += "_NoKI"
        if 리자드차수:
            상품구조 += "_[Lizard]"
        if month_range:
            상품구조 += "_MtlyCpn"
    elif "퇴직" in soup.text:
        상품구조 += "_퇴직"
        #new_series["기초자산코드5"] = per_re2.search(get_xy(table[1], 1, 1)).group()

    if len(구간종료일) > 2 and not month_range:
        if int(float(re.sub("%", "", add_to_db.만기수익률))) != int(float(re.sub("%", "", add_to_db.중도상환수익률)) * len(구간종료일)):
            상품구조 += "_수익률주의"

    Neg_Word = ['% 이하인 경우', '비율의 평균이', '원금부분지급', '있더라도', '단 1회라도']

    for i in Neg_Word:
        if i in soup.text:
            상품구조 = "분류안됨"

    add_to_db.Structure = 상품구조

    db.session.add(add_to_db)
    db.session.commit()









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
            return str(tds[col].text)

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