from __init__ import *
from flask import session


#다트상품
class product(db.Model):
    __tablename__ = 'Dart_Product'
    Product_Num = db.Column(db.INTEGER, db.Sequence('public_dart_Product_Num_seq'), primary_key=True)
    Title = db.Column(db.Text)
    발행가액 = db.Column(db.Text)
    발행일 = db.Column(db.Text)
    화폐단위 = db.Column(db.Text)
    Structure = db.Column(db.Text)
    Settle_Date_Lags = db.Column(db.Integer)
    기초자산코드 = db.Column(db.ARRAY(db.Text()))
    만기수익률 = db.Column(db.Text)
    만기장벽 = db.Column(db.Text)
    중도상환수익률 = db.Column(db.Text)
    Lizard차수 = db.Column(db.Text)
    Lizard수익률 = db.Column(db.Text)
    LizardRange = db.Column(db.Text)
    쿠폰수익률 = db.Column(db.Text)
    쿠폰Range = db.Column(db.Text)
    구간Range= db.Column(db.ARRAY(db.Text()))
    기초자산기준일 = db.Column(db.Text)
    구간종료일 = db.Column(db.ARRAY(db.Text()))
    쿠폰평가일 = db.Column(db.ARRAY(db.Text()))
    Issure = db.Column(db.Text)
    OAddress = db.Column(db.Text)
    PDFAddress = db.Column(db.Text)

    def __init__(self, Title=None, 발행가액 = None, 발행일 = None, 화폐단위 = None, Structure  = None, Settle_Date_Lags = None,
                 기초자산코드 = None,만기수익률 = None,만기장벽 = None,중도상환수익률 = None,
                 Lizard차수 = None,Lizard수익률 = None,LizardRange = None,쿠폰수익률 = None,쿠폰Range = None,구간Range = None,
                 기초자산기준일 = None,구간종료일 = None,쿠폰평가일 = None,Issure = None,OAddress= None, PDFAddress = None):
        self.Title = Title
        self.발행가액 = 발행가액
        self.발행일 = 발행일
        self.화폐단위 = 화폐단위
        self.Structure = Structure
        self.Settle_Date_Lags = Settle_Date_Lags
        self.기초자산코드 = 기초자산코드
        self.만기수익률 = 만기수익률
        self.만기장벽 = 만기장벽
        self.중도상환수익률 = 중도상환수익률
        self.Lizard차수 = Lizard차수
        self.Lizard수익률 = Lizard수익률
        self.LizardRange = LizardRange
        self.쿠폰수익률 = 쿠폰수익률
        self.쿠폰Range = 쿠폰Range
        self.구간Range = 구간Range
        self.기초자산기준일 = 기초자산기준일
        self.구간종료일 = 구간종료일
        self.쿠폰평가일 = 쿠폰평가일
        self.Issure = Issure
        self.OAddress = OAddress
        self.PDFAddress = PDFAddress

class asking(db.Model):
    __tablename__ = 'qna'
    qna_num = db.Column(db.INTEGER, db.Sequence('qna_qna_num_seq'), primary_key=True)
    user = db.Column(db.Text)
    contents = db.Column(db.Text)

    def __init__(self, user, contents):
        self.user = user
        self.contents = contents


class reply(db.Model):
    __tablename__ = 'qna_comment'
    com_num = db.Column(db.INTEGER, db.Sequence('qna_comment_com_num_seq'), primary_key=True)
    qna_num = db.Column(db.INTEGER)
    user = db.Column(db.Text)
    contents = db.Column(db.Text)

    def __init__(self, qna_num, user, contents):
        self.qna_num = qna_num
        self.user = user
        self.contents = contents



class save_url(db.Model):
    __tablename__ = 'url_list'
    url_index = db.Column(db.INTEGER, db.Sequence('url_list_url_index_seq'), primary_key=True)
    url = db.Column(db.Text)
    발행사 = db.Column(db.Text)
    발행일 = db.Column(db.Text)
    차수 = db.Column(db.Text)
    Title = db.Column(db.Text)
    Type = db.Column(db.Text)

    def __init__(self, url = None, 발행사 = None, 발행일 = None, 차수 = None, Title = None, Type= None):
        self.url = url
        self.발행사 = 발행사
        self.발행일 = 발행일
        self.차수 = 차수
        self.Title = Title
        self.Type = Type


