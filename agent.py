import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import brands
import stores
import smtplib
from email.mime.text import MIMEText

MIN_DISCOUNT = 0

results=[]

def brand_match(text):

    text=text.lower()

    for b in brands.BRANDS:
        if b.lower() in text:
            return True

    return False


def check_store(name,url):

    try:

        r=requests.get(url,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        products=soup.find_all("article")

        for p in products:

            text=p.get_text()

            if not brand_match(text):
                continue

            numbers=[int(s) for s in text.split() if s.isdigit()]

            if len(numbers)<2:
                continue

            price=min(numbers)
            old=max(numbers)

            discount=(old-price)/old*100

            if discount>MIN_DISCOUNT:

                results.append({

                "store":name,
                "product":text[:100],
                "price":price,
                "old":old,
                "discount":round(discount,1)

                })

    except:
        pass


def send_mail(text):

    sender=os.environ["EMAIL_FROM"]
    password=os.environ["EMAIL_PASS"]
    receiver=os.environ["EMAIL_TO"]

    msg=MIMEText(text)

    msg["Subject"]="Beste alpintilbud i Norge i dag"
    msg["From"]=sender
    msg["To"]=receiver

    server=smtplib.SMTP_SSL("smtp.gmail.com",465)

    server.login(sender,password)

    server.send_message(msg)

    server.quit()


def run():

    for s in stores.STORES:

        check_store(s[0],s[1])

    if len(results)==0:
        return

    df=pd.DataFrame(results)

    df=df.sort_values("discount",ascending=False)

    top=df.head(5)

    text="\nBeste alpintilbud i Norge\n\n"

    for i,row in top.iterrows():

        text+=f"""
Produkt: {row['product']}
Butikk: {row['store']}
Før: {row['old']} kr
Nå: {row['price']} kr
Rabatt: {row['discount']} %
"""

    send_mail(text)

run()
