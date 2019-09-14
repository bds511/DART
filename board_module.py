from flask import Flask, request, flash, url_for, redirect, render_template, abort, session, jsonify, Response
from __init__ import *
import pandas as pd
from io import StringIO
from model import *




@app.route('/')
def home():
    return render_template('home.html')


@app.route('/Product', methods=["GET","POST"])
def Product_Search():
    if request.args.get("date"):
        발행일 = request.args.get("date")
        Issure = request.args.get("Issure")
        contents = product.query.filter(product.Issure == Issure, product.발행일 == 발행일).order_by(product.Title)

        return render_template("result.html", contents= contents, date =발행일, Issure = Issure)


    return render_template('search.html')


@app.route('/Get_CSV', methods=["GET","POST"])
def Get_CSV():
    if request.args.get("date"):
        발행일 = request.args.get("date")
        Issure = request.args.get("Issure")
        contents = product.query.filter(product.Issure == Issure, product.발행일 == 발행일).order_by(product.Title)
        df= pd.read_sql(contents.statement, contents.session.bind)
        table_type = request.args.get("type")
        if table_type == "1":
            df = Change_array(df)
        else:
            df = Change_array2(df)
        output = StringIO()
        output.write(u'\ufeff')
        df.to_csv(output)

        response = Response(
            output.getvalue(),
            mimetype="text/csv",
            content_type='application/octet-stream',
        )
        response.headers["Content-Disposition"] = "attachment; filename=post_export.csv"  # 다운받았을때의 파일 이름 지정해주기
        return response

def Change_array(df):
    for i in range(5):
        df['기초자산코드'+str(i+1)] = df.기초자산코드.str[i]
    for i in range(15):
        df['구간Range'+str(i+1)]= df.구간Range.str[i]
    for i in range(15):
        df['구간종료일'+str(i+1)] = df.구간종료일.str[i]
    for i in range(60):
        df['쿠폰평가일'+str(i+1)] = df.쿠폰평가일.str[i]

    df['만기평가일'] = df.구간종료일.str[-1]
    df['종평여부'] = None
    data_array = ["Title", "발행가액", "발행일", "화폐단위","Structure", "Settle_Date_Lags"] + ["기초자산코드"+str(i+1) for i in range(5)] + ["만기수익률", "만기장벽", "중도상환수익률", "Lizard차수", "Lizard수익률", "LizardRange", "쿠폰수익률", "쿠폰Range"] +["구간Range" +str(i+1) for i in range(15)]+["기초자산기준일", "만기평가일", "종평여부"] +  ["구간종료일" +str(i+1) for i in range(15)] + ["쿠폰평가일" +str(i+1) for i in range(60)]
    return df[data_array].transpose()

def Change_array2(df):
    for i in range(5):
        df['기초자산코드'+str(i+1)] = df.기초자산코드.str[i]
    for i in range(15):
        df['구간Range'+str(i+1)]= df.구간Range.str[i]
    for i in range(15):
        df['구간종료일'+str(i+1)] = df.구간종료일.str[i]
    for i in range(60):
        df['쿠폰평가일'+str(i+1)] = df.쿠폰평가일.str[i]
    for i in range(3):
        df['거래소'+str(i+1)] = None
    for i in range(6):
        df['기초자산기준가'+str(i+1)] = None
    for i in range(6):
        df['구간지급일'+str(i+1)] = None
    data_array = ["Title", "Structure", "Settle_Date_Lags"] + ["기초자산코드"+str(i+1) for i in range(3)] + ["만기수익률", '거래소1','거래소2','거래소3','기초자산기준가1',	'기초자산기준가2',	'기초자산기준가3','만기장벽', "중도상환수익률", "기초자산기준일"]+ ["구간종료일" +str(i+1) for i in range(6)] +["구간지급일" +str(i+1) for i in range(6)] +["구간Range" +str(i+1) for i in range(6)]
    return df[data_array]


@app.route('/qna', methods=["GET", "POST"])
def qna():
    if request.method == 'POST':
        if request.args.get('mode') == "asking":
            add_to_db = asking(request.form['user'], request.form['contents'])
            db.session.add(add_to_db)
            db.session.commit()
        else:
            add_to_db = reply(request.form['qna_num'], request.form['user'], request.form['contents'])
            db.session.add(add_to_db)
            db.session.commit()
        return redirect(url_for('qna', page = request.args.get('page')))
    if request.args.get("page"):
        page = int(request.args.get("page"))
    else:
        page =1
    max_page = int(len(asking.query.all())/20)+1

    contents= asking.query.order_by(asking.qna_num.desc())[(page-1)*20:page*20]
    condition = ((reply.qna_num == i.qna_num for i in contents))

    replying = reply.query.filter(or_(*condition)).all()
    return render_template('QnA.html',contents= contents, replying = replying, page = page, max_page = max_page)



@app.route('/Get_URL', methods=["GET","POST"])
def Get_URL():
    if request.args.get("date"):
        발행일 = request.args.get("date")
        contents = save_url.query.filter(save_url.발행일 == 발행일).order_by(save_url.Title)
        df= pd.read_sql(contents.statement, contents.session.bind)
        data_array = ["발행일", "발행사", "Type", "차수", "url"]
        df= df[data_array]
        output = StringIO()
        output.write(u'\ufeff')
        df.to_csv(output)

        response = Response(
            output.getvalue(),
            mimetype="text/csv",
            content_type='application/octet-stream',
        )
        response.headers["Content-Disposition"] = "attachment; filename="+발행일+".csv"  # 다운받았을때의 파일 이름 지정해주기
        return response