from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import cx_Oracle
import pandas as pd


browser = webdriver.Chrome()
browser.implicitly_wait(20)
browser.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findPeriodBoxOfficeList.do')


## DB 연동
connect = cx_Oracle.connect("system", "oracle", "localhost:1521/xe")
cursor = connect.cursor()

moviename = []
moviedate = []
movieincome = []
moviepeople = []
movieplays = []

# 영화이름, 개봉일, 누적매출액, 누적관객수, 상영횟수
for year in range(12, 22):
    browser.find_element_by_id('sSearchFrom').clear()
    browser.switch_to_alert().accept()
    browser.find_element_by_id('sSearchFrom').send_keys('20{}-01-01'.format(year))
    browser.find_element_by_id('sSearchTo').clear()
    browser.switch_to_alert().accept()
    browser.find_element_by_id('sSearchTo').send_keys('20{}-12-31'.format(year))
    browser.find_element_by_class_name('btn_blue').send_keys(Keys.ENTER)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    name = soup.select('.ellip.per90')
    for i in name:
        moviename.append((i.text).strip())
    date = soup.select('tr > td:nth-of-type(3)')
    for i in date:
        moviedate.append((i.text).strip())
    income = soup.select('tr > td:nth-of-type(6)')
    for i in income:
        movieincome.append(((i.text).strip()).replace(',', ''))
    people = soup.select('tr > td:nth-of-type(8)')
    for i in people:
        moviepeople.append(((i.text).strip()).replace(',', ''))
    plays = soup.select('tr > td:nth-of-type(10)')
    for i in plays:
        movieplays.append(((i.text).strip()).replace(',', ''))

browser.close()


# 영화장르
moviegenre = []
for i in moviename:
    try:
        resp = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=영화+'+i+'+정보')
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.select_one('.info_group:nth-child(3) > dt').text == '장르':
            genre = soup.select_one('.info_group:nth-child(3) > dd')
            moviegenre.append(genre.text)
        else:
            moviegenre.append('')
    except:
        moviegenre.append('')

# 영화배우
movieactor = []
for i in moviename:
    try:
        resp = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q=영화+'+i)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.select('.tit_base')[2].text == '출연':
            actor = soup.select('.dl_comm:nth-child(4) > .cont > a')
            movieactor.append([actor[0].text.strip(),actor[1].text.strip(),actor[2].text.strip()])
        else:
            movieactor.append('')
    except:
        movieactor.append('')

# 영화평점
moviescore = []
for i in moviename:
    try:
        resp = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=영화+'+i+'+평점')
        soup = BeautifulSoup(resp.text, 'html.parser')
        score = soup.select('.area_star_number')
        moviescore.append(score[0].text)
    except:
        moviescore.append('')


# 영화 정보들을 list안에 tuple로 저장
movielist = []
for i in range(len(moviename)):
    movielist.append((moviename[i], moviedate[i], movieincome[i], moviepeople[i], movieplays[i], moviescore[i]))
# movielist 영화이름 중복값 제거
movielist.sort()
num = 0
while num < len(movielist)-1:
    if movielist[num][0] == movielist[num+1][0]:
        del movielist[num]
        num = 0
    num += 1


# 영화명 + 배우 list
nameactor = []
count = 0
for i in moviename:
    for j in range(0,3):
        if len(movieactor[count]) != 0:
            nameactor.append((i, movieactor[count][j]))
    count += 1
# nameactor 영화이름 중복값 제거
nameactor.sort()
num = 0
while num < len(nameactor)-1:
    if nameactor[num][0] == nameactor[num+1][0] and nameactor[num][1] == nameactor[num+1][1]:
        del nameactor[num]
        num = 0
    num += 1
len(nameactor)
nameactor


# 영화명 + 장르 list
genrelist = []
for i in moviegenre:
    genrelist.append(i.split(","))

namegenre = []
count = 0
for i in moviename:
    for j in range(0, len(genrelist[count])):
        if genrelist[count][j] != '':
            namegenre.append((i, genrelist[count][j].replace(' ','')))
    count += 1
# namegenre 영화이름 중복값 제거
namegenre.sort()
num = 0
while num < len(namegenre)-1:
    if namegenre[num][0] == namegenre[num+1][0] and namegenre[num][1] == namegenre[num+1][1]:
        del namegenre[num]
        num = 0
    num += 1
len(namegenre)
namegenre


## 영화 리뷰 크롤링, 영화명 + 리뷰 list
namereview = []
for i in moviename:
    try:
        resp = requests.get('https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query='+i+'+평점')
        soup = BeautifulSoup(resp.text, 'html.parser')
        for j in soup.select('p.area_p_title > strong'):
            namereview.append((i, j.text))
    except:
        namereview.append((i, ''))
# namereview 영화이름 중복값 제거
namereview.sort()
num = 0
while num < len(namereview)-1:
    if namereview[num][0] == namereview[num+1][0] and namereview[num][1] == namereview[num+1][1]:
        del namereview[num]
        num = 0
    num += 1


# 영화 줄거리 크롤링, 영화명 + 줄거리 list
namesummary = []
for i in moviename:
    try:
        resp = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='+i+'+줄거리')
        soup = BeautifulSoup(resp.text, 'html.parser')
        namesummary.append((i,soup.select('.desc._content_text')[0].text))
    except:
        namesummary.append((i,''))
# namesummary 영화이름 중복값 제거
namesummary.sort()
num = 0
while num < len(namesummary)-1:
    if namesummary[num][0] == namesummary[num+1][0]:
        del namesummary[num]
        num = 0
    num += 1


## 영화 포스터 크롤링, 영화명 + 사진경로 list
nameimage = []
browser = webdriver.Chrome()
for i in moviename:
    try:
        browser.get('https://ko.wikipedia.org/wiki/'+i)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.close()
        nameimage.append((i, soup.select_one("a.image > img")["src"]))
    except:
        nameimage.append((i, ''))
# namesummary 영화이름 중복값 제거
nameimage.sort()
num = 0
while num < len(nameimage)-1:
    if nameimage[num][0] == nameimage[num+1][0]:
        del nameimage[num]
        num = 0
    num += 1


## 크롤링 데이터 db에 저장
# movielist를 movie테이블에 삽입
sql = "insert into movie(title, rel_date, sales, audience, play, grade) values (:1, :2, :3, :4, :5, :6)"
cursor.executemany(sql, movielist)
# nameactor를 movieactor테이블에 삽입
cursor.executemany("insert into movieactor(title, actor) values(:1, :2)", nameactor)
# namegenre를 movieactor테이블에 삽입
cursor.executemany("insert into moviegenre(title, genre) values(:1, :2)", namegenre)
# namereview를 moviereview테이블에 삽입
cursor.executemany("insert into moviereview(title, review) values(:1, :2)", namereview)
# namesummary를 moviesummary테이블에 삽입
cursor.executemany("insert into moviesummary(title, summary) values(:1, :2)", namesummary)
# nameimage를 movieimage테이블에 삽입
cursor.executemany("insert into movieimage(title, image) values(:1, :2)", nameimage)
connect.commit()
