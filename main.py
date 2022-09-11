from re import U
import pandas as pd
import yfinance as yf
pd.options.mode.chained_assignment = None

def get_nasdaq():
    # pretty printing of pandas dataframe
    pd.set_option('expand_frame_repr', False)
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # There are 5 tables on the Wikipedia page
    # we want the last table

    payload=pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    return payload[4]

def get_avg(df, column):
    data = df.rolling(3).mean()[column]
    #data = data.shift(periods=1)[:-1]
    return data

def get_buy_action(df):
    df["AvgMin"] = get_avg(df, "Low")
    df["AvgMax"] = get_avg(df, "High")
    df["Action"] = df.apply(lambda x: "Buy" if x.Close < x.AvgMin else "Sell" if x.Close > x.AvgMax else "", axis=1)
    return df["Action"]

def apply_filter_action(df):
    buy_count = 2
    count = 0
    for ind, action in df.iteritems():
        if action == "Buy": 
            if count < buy_count:
                count +=1
                df[ind] = 1
            else:
                df[ind] = 0
        else:
            if count > 0:
                df[ind] = -1*count
                count = 0
            else:
                df[ind] = 0
    return df

def apply_calculation(df):
    initial = 1000
    units = 0
    for ind, value in df.iterrows():
        if value.Action > 0: 
            units = units + (initial * value.Action)/value.Close
        elif value.Action < 0:
            initial = (units * value.Close)/(value.Action * -1)
            units = 0
    return initial

if __name__ == '__main__':
    nasdaq100 = get_nasdaq()
    final = []
    for ind, stocks in nasdaq100.iterrows():
        ticker = stocks["Ticker"]
        data = yf.download(ticker,'2017-01-01','2022-09-09')[["High", "Low", "Close"]]
        
        data["Action"] = get_buy_action(data)
        data["Action"] = apply_filter_action(data["Action"])
        if data["Action"].sum() == 0:
            calc = apply_calculation(data)
            final.append([ticker, calc])
    print(pd.DataFrame(final))
    print((pd.DataFrame(final)[1].sum()/(100*1000) - 1)*100)