import pandas as pd
import tushare as ts
import matplotlib
from  datetime import  datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter,date2num
from mpl_finance import candlestick_ohlc

matplotlib.style.use("ggplot")
# 通过股票代码获取股票数据,这里没有指定开始及结束日期
# 002351 漫步者
# 300510 金冠
# 600519 茅台
df = ts.get_k_data("002351",start='2019-01-28')

# 查看前十条数据
df.head()

# 查看后十条数据
df.tail()

# 将数据的index转换成date字段对应的日期
df.index = pd.to_datetime(df.date)
print(df)
# 将多余的date字段删除
df.drop("date", inplace=True, axis=1)

# 计算5,15,50日的移动平均线, MA5, MA15, MA50
days = [5, 15, 50]
for ma in days:
    column_name = "MA{}".format(ma)
    df[column_name] = df.close.rolling(ma).mean()

# 计算浮动比例
df["pchange"] = df.close.pct_change()
# 计算浮动点数
df["change"] = df.close.diff()

#走势图
# df[["close", "MA5", "MA15", "MA50"]].plot(figsize=(12,5))
# k线
def candlePlot(data, title=""):
    data["date"] = [date2num(pd.to_datetime(x)) for x in data.index]
    dataList = [tuple(x) for x in data[
        ["date", "open", "high", "low", "close"]].values]

    ax = plt.subplot()
    ax.set_title(title)
    ax.xaxis.set_major_formatter(DateFormatter("%y-%m-%d"))
    candlestick_ohlc(ax, dataList, width=1, colorup="r", colordown="g")
    plt.setp(plt.gca().get_xticklabels(), rotation=50,
             horizontalalignment="center")
    fig = plt.gcf()
    fig.set_size_inches(20, 15)
    plt.grid(True)

# candlePlot(df)

def kdj(df, parameters=(9, 3, 3)):
    """
    RSVt＝(Ct－L9)／(H9－L9)＊100
    Kt＝RSVt／3＋2＊Kt-1／3
　　Dt＝Kt／3＋2＊Dt-1／3
　　Jt＝3＊Dt－2＊Kt
    :param df: 
    :param parameters: 
    :return: 
    """
    p0 = parameters[0]
    p1 = parameters[1]
    p2 = parameters[2]
    df = df.sort_index()
    df.index = pd.to_datetime(df.index)
    high_n = df[u'high'].rolling(p0).max()
    low_n = df[u"low"].rolling(p0).min()
    rsvt = (df[u"close"] - low_n) / (high_n - low_n) * 100
    rsvt.dropna(inplace=True)
    k = []
    d = []
    j = []
    for i in range(len(rsvt)):
        if i == 0:
            k.append(50)
            d.append(50)
            j.append(50)
        else:
            kt = rsvt.ix[i] / 3 + 2 * k[i - 1] / 3
            dt = kt / 3 + 2 * d[i - 1] / 3
            jt = 3 * kt - 2 * dt
            k.append(kt)
            d.append(dt)
            j.append(jt)
    kdj_df = pd.DataFrame()
    kdj_df["k"] = k
    kdj_df["d"] = d
    kdj_df["j"] = j
    kdj_df["long"] = (kdj_df[u"k"] > kdj_df[u"d"]) & (kdj_df[u"k"] > kdj_df[u"j"])
    kdj_df["short"] = (kdj_df[u"k"] < kdj_df[u"d"]) & (kdj_df[u"k"] < kdj_df[u"j"])
    kdj_df.index = rsvt.index
    kdj_df["open"] = df[u"open"][rsvt.index]
    return kdj_df


def plot_kdj(kdj_df):
    plt.subplot(211)
    plot0, = plt.plot(df["close"], label="day performance")
    plt.subplot(212)
    plot1, = plt.plot(kdj_df["k"], label="k line")
    plot2, = plt.plot(kdj_df["d"], label="d line")
    plot3, = plt.plot(kdj_df["j"], label="j line")
    plt.legend(handles=[plot0, plot1, plot2, plot3])
    plt.show()


def parser_time(time):
    if time=="0":
        return pd.to_datetime('19000101', format='%Y%m%d',errors="ignore")
    else:
        return pd.to_datetime(time, format='%Y%m%d',errors="ignore")

def save_data(code):
    file_name = save_path+"%s.csv"%code
    import os
    if os.path.exists(file_name):
        return
    df = ts.get_h_data(code)
    df.to_csv(save_path+"%s.csv"%code,encoding="gbk")



# 获取股票代码
codes = ts.get_stock_basics()


codes[u'timeToMarket'] = codes[u'timeToMarket'].apply(str)
codes[u'timeToMarket']  =  codes[u'timeToMarket'].apply(parser_time)

code_in =   codes.index[(codes[u'timeToMarket'] > datetime(1970,1,1)) & (codes[u'timeToMarket'] < datetime(2019,12,1))]
print(code_in)

# save_path = "gold_cross/new_stocks/"

# code_in = pd.Series(list(set(code_in)))
# code_in.apply(save_data)

# code_i = code_in[1]
code_i = "300104"

def gold_cross(code):
    # df = ts.get_h_data(code_i)
    kdj_df = kdj(code)
    long = (kdj_df["long"] > (kdj_df["long"].shift(1))).shift(1)
    short = (kdj_df["short"] > (kdj_df["short"].shift(1))).shift(1)
    long[kdj_df["k"] < 50] = False
    short[kdj_df["k"] > 50] = False
    buy_sell = kdj_df["open"] * long - short * kdj_df["open"]
    buy_sell = buy_sell[buy_sell != 0]
    gain = buy_sell + buy_sell.shift(1)
    gain.cumsum().plot()
    plt.show()
    return gain


# gain_i = gold_cross(df)
# 近2天交易日
date = '2020-01-16 00:00:00'
date1 = '2020-01-17 00:00:00'
for i in code_in:
    print(i)
    df = ts.get_k_data(i,start='2019-01-28')
    a = ts.get_realtime_quotes(i)
    for index,row in a.iterrows():
        name = row['name']
    # print(name)
    if df.size == 0:
        continue
    # 将数据的index转换成date字段对应的日期
    df.index = pd.to_datetime(df.date)
    kdj_df = kdj(df)

    # plot_kdj(kdj_df)
    # kdj_df.tail()
    # print(kdj_df)
    kdj_df['KDJ_金叉死叉'] = ''
    kdj_position=kdj_df['k']>kdj_df['d']
    kdj_df.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉'

    kdj_df.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'
    for index,row in kdj_df.iterrows():
        if row['KDJ_金叉死叉'] != '':
            # print(index)
            if str(index) == date or str(index) == date1:
                if row['KDJ_金叉死叉'] == '死叉' :
                    f = open('xcode'+ str(index) +'.txt','a+')
                    f.read()
                    f.write(str(name) + i + row['KDJ_金叉死叉'] + str(row['k']) + '\n')
                    f.close()
                if row['KDJ_金叉死叉'] == '金叉' and row['d'] < 30:
                    f = open('code'+ str(index) +'.txt','a+')
                    f.read()
                    f.write(str(name) + i + row['KDJ_金叉死叉'] + str(row['k']) + '\n')
                    f.close()
                # print(row)
    # print(kdj_df)
# plt.show()