from flask import Flask, render_template, url_for, request, send_file
from io import BytesIO, StringIO
import cx_Oracle
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
app = Flask(__name__)

connect = cx_Oracle.connect("c##py_user", "1234", "192.168.30.30/xe")
cursor = connect.cursor()
data = pd.read_sql("select * from movieinfo", con = connect)
rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

@app.route('/')
def index():
   return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    try:
        keyword = request.form['title']
        movieinfo = pd.read_sql("select * from movieinfo where TITLE ='"+keyword+"'", con = connect)
        title = movieinfo.iloc[0, 0]
        rel_date = str(movieinfo.iloc[0, 1])[0:10]
        genre = movieinfo.iloc[0, 6]
        actor = movieinfo.iloc[0, 7]
        image = movieinfo.iloc[0, 8]
        summary = movieinfo.iloc[0, 9]
        moviereview = pd.read_sql("select * from moviereview where TITLE ='"+keyword+"'", con = connect)
        review = moviereview.iloc[:, 1]
        genres = []
        ranks = []
        dff = pd.read_sql("select genre,count(*) from moviegenre group by genre order by count(*) desc", con = connect)
        dff
        for i in range(0, 15):
            genres.append(dff.loc[i]['GENRE'])
        for i in genres:
            dfff = pd.read_sql("select * from movieinfo where moviegenre like '%"+i+"%' order by audience desc", con = connect)
            ranks.append([dfff.loc[0]['TITLE'],dfff.loc[1]['TITLE'],dfff.loc[2]['TITLE'],dfff.loc[3]['TITLE'],dfff.loc[4]['TITLE'],dfff.loc[5]['TITLE'],dfff.loc[6]['TITLE'],dfff.loc[7]['TITLE'],dfff.loc[8]['TITLE'],dfff.loc[9]['TITLE']])
        year =pd.read_sql("select year from rank where TITLE ='"+keyword+"'", con = connect)
        year = year.iloc[0,0]
        yearlist = []
        df3 = pd.read_sql("select title from rank where YEAR ='"+year+"'order by audience desc", con = connect)
        for i in range(0,10):
            yearlist.append(df3.iloc[i, 0])
        df4 = pd.read_sql("select rank from(select title, ROW_NUMBER() OVER (ORDER BY audience DESC) AS RANK from rank where YEAR = '"+year+"'order by audience desc) where title ='"+keyword+"'", con = connect)
        rank = df4.iloc[0,0]
        return render_template('result.html',title = title, rel_date = rel_date, genre = genre, actor = actor, image = image, summary = summary, rank = ranks, genrelist = genres, rank1 = rank, yearlist = yearlist, re = review, year = year)
    except:
        return render_template('except.html')


# 코로나에 의한 영화 매출 동향
@app.route('/graph1/')
def graph1():
    covid = data.loc[:, ['REL_DATE', 'SALES']].sort_values(by='REL_DATE')
    covid['REL_DATE'] = covid.REL_DATE.dt.year
    stats = covid.groupby('REL_DATE').mean()
    stats = stats[11:21]
    #시각화
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot(stats.index, stats['SALES'])
    ax.set_xticks(stats.index)
    ax.set_xlabel('연도',size = 12)
    ax.set_ylabel('평균 매출액',size = 12)
    ax.legend()
    img = BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/stats1/')
def stats1():
    return render_template("stats1.html")

# 여름에 공포 영화 수요가 진짜 많은지
@app.route('/graph2/')
def graph2():
    data2 = pd.read_sql("select * from movieinfo where regexp_like(moviegenre,'공포|스릴러')", con = connect)
    horror = data2.loc[:, ['REL_DATE', 'AUDIENCE']]
    horror['REL_DATE'] = horror.REL_DATE.dt.quarter
    horror.sort_values(by='REL_DATE', inplace=True)
    stats2 = horror.groupby('REL_DATE').mean()
    # 시각화
    fig = plt.figure()
    ax = fig.subplots()
    ax.bar(stats2.index, stats2['AUDIENCE'])
    ax.set_xticks(stats2.index)
    ax.set_xticklabels(['겨울', '봄', '여름', '가을'])
    ax.set_ylabel('평균 관객수',size = 12)
    ax.legend()
    img2 = BytesIO()
    fig.savefig(img2, format='png', dpi=100)
    img2.seek(0)
    return send_file(img2, mimetype='image/png')

@app.route('/stats2/')
def stats2():
    return render_template("stats2.html")

# 평점과 매출액의 관계
@app.route('/graph3/')
def graph3():
    corr = data.loc[:, ['SALES','GRADE']].sort_values(by='GRADE')
    corr.dropna(axis=0, inplace=True)
    corr = corr[corr['GRADE'] != 0]
    corr['GRADE'] = corr['GRADE'].astype(int)
    stats3 = corr.groupby('GRADE').mean()
    # 시각화
    fig = plt.figure()
    ax = fig.subplots()
    ax.bar(stats3.index, stats3['SALES'])
    ax.set_xticks(stats3.index)
    ax.set_xlabel('평점',size = 12)
    ax.set_ylabel('평균 매출액',size = 12)
    ax.legend()
    img3 = BytesIO()
    fig.savefig(img3, format='png', dpi=100)
    img3.seek(0)
    return send_file(img3, mimetype='image/png')

@app.route('/stats3/')
def stats3():
    return render_template("stats3.html")


# 상영횟수와 매출액의 관계
@app.route('/graph4/')
def graph4():
    corr2 = data.loc[:, ['REL_DATE', 'PLAY', 'SALES']].sort_values(by='PLAY')
    corr2['REL_DATE'] = corr2.REL_DATE.dt.year
    stats4 = corr2.groupby('REL_DATE').mean()
    stats4 = stats4[11:21]
    # 시각화
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot(stats4.index, stats4['PLAY']*1000000, label = '평균 상영 횟수*1000000')
    ax.plot(stats4.index, stats4['SALES'], label = '평균 매출액')
    ax.set_xlabel('연도',size = 12)
    ax.axes.yaxis.set_visible(False)
    ax.legend()
    img4 = BytesIO()
    fig.savefig(img4, format='png', dpi=100)
    img4.seek(0)
    return send_file(img4, mimetype='image/png')

@app.route('/stats4/')
def stats4():
    return render_template("stats4.html")

if __name__ == '__main__':
    app.run(debug=True)
