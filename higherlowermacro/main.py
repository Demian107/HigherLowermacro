from selenium import webdriver
from selenium.webdriver.common.by import By
from pytrends.request import TrendReq
import time
from random import randint
import datetime
import pymysql

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(r"D:\programming\python\chromedriver.exe", options=options)


score = 0
today = datetime.datetime.now()
startdate = '2022-08-01'
enddate = str(today.date())
timerange = startdate + ' ' + enddate


USER = 'Lightspeed30'
PW = '!!Vlxj1215'
DB = 'userinfo'


connection = pymysql.connect(
    user=USER, password=PW, host='localhost', port=3306, database=DB
)


def get_data(text):
    cur = connection.cursor()
    query = f'''
    SELECT amount
    FROM higherlower
    WHERE name='{text}';
    '''
    cur.execute(query)
    res = cur.fetchall()
    res = str(res).replace("(","").replace(")","").replace(",","")
    if res=='':
        return 0
    else:
        return int(res)

def save_data(text,amount):
    con = connection
    query = f'''
            INSERT INTO higherlower (name, amount)
            VALUES ('{text}', {amount});
            '''
    con.cursor().execute(query)
    con.commit()
while True:
    driver.get('https://www.higherlowerkorea.com/')
    driver.minimize_window()
    driver.find_elements(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[4]/button[1]")[0].click()
    while True:
        time.sleep(1)
        texts = []
        texts.append(driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div[3]/div[1]/div/div[1]").text)
        texts.append(driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[1]").text)

        avg = []
        print(get_data(texts[0]), get_data(texts[1]))
        if get_data(texts[0]) != 0 and get_data(texts[1]) != 0:
            avg.append(get_data(texts[0]))
            avg.append(get_data(texts[1]))
        try:
            pt = TrendReq()
            pt.build_payload(texts,geo="KR",timeframe=timerange)
            df = pt.interest_over_time()

            for i in texts:
                avg.append(df[i].mean().round(0))
        except:
            avg.append(randint(0,100))
            avg.append(randint(0,100))

        driver.find_element(By.XPATH, f"/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[2]/div[{1 if avg[0]<avg[1] else 2}]").click()
        print(f"SCORE : {score}  TREND : [{texts[0]}({avg[0]}){'<' if avg[0]<avg[1] else '>'}{texts[1]}({avg[1]})]")
        time.sleep(2)
        amounts = [int(driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div[3]/div[1]/div/div[2]").text[:-1].replace(",","")),int(driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[2]").text[:-2].replace(",",""))]
        print(amounts)
        if get_data(texts[0]) == 0 and amounts[0]!=0:
            save_data(texts[0],amounts[0])
        if get_data(texts[1]) == 0 and amounts[1]!=0:
            save_data(texts[1],amounts[1])
        score+=1
        time.sleep(5)

driver.close()