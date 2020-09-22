"""
Test the permance impact of analyst ratings
"""

import yfinance as yf
import pandas as pd
import numpy as np

def save_obj(obj, name):
    import pickle
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    import pickle
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

# either load from memory or download from yfinance again
def getData(tickers, dataSetName, data_refresh):
    if not data_refresh:
        [hist, reco]=load_obj(dataSetName)
    else:
        hist={}
        reco={}
        for ticker in tickers:   
            print(ticker)             
            tickerObj = yf.Ticker(ticker)
            hist[ticker] = tickerObj.history(period="5y")
            reco[ticker] = tickerObj.recommendations
        save_obj([hist, reco], dataSetName)
    return(hist, reco)


#%%

data_refresh=False

# some tickers to consider
tickerData=pd.read_csv('tradingStrategy_tickers.csv')
dataSetName='tradingStrategy_analystRecommendation'
tickers=tickerData["Symbol"]
tickers2=tickers.drop(tickers.index[[5, 6, 9]])
tickers2.reset_index(inplace=True, drop=True)
[hist, reco]=getData(tickers2[:4], dataSetName, data_refresh)

for i in range(4):    
    ticker=tickers2[i]    
    recoi=reco[ticker]
    recoi.index=recoi.index.normalize()
    histi=hist[ticker]
    
    # count buy signals
    r_buy=recoi.copy()
    r_buy=r_buy[r_buy['To Grade'].apply(lambda x: (x=='Buy')|(x=='Strong Buy'))] 
    r_buy['Buy']=1
    r_buy_count=r_buy['Buy'].groupby(r_buy.index).count()
    
    hist_buy=pd.merge(histi, r_buy_count, how='left', left_index=True, right_index=True) 
    # check the performance of the next number of days 
    
    numForwardDays=10 
    hist_buy['Forward Ave Close']=hist_buy['Close'][::-1].rolling(numForwardDays+1).mean()[::-1]
    hist_buy['Forward Close']=hist_buy['Close'].shift(-numForwardDays)
    
    hist_buy_subset=hist_buy[hist_buy['Buy']>0][['Close', 'Forward Ave Close', 'Forward Close']]
    hist_buy_subset['Forward Ave Gain%']=(hist_buy_subset['Forward Ave Close']-hist_buy_subset['Close'])/hist_buy_subset['Close']
    hist_buy_subset['Forward Gain%']=(hist_buy_subset['Forward Close']-hist_buy_subset['Close'])/hist_buy_subset['Close']
    
    print(ticker)
    print('Forward Ave Gain% - mean: ', round(hist_buy_subset['Forward Ave Gain%'].mean()*100,2))
    print('Forward Ave Gain%  - std: ', round(hist_buy_subset['Forward Ave Gain%'].std()*100, 2))
    
    print('Forward Gain% - mean: ', round(hist_buy_subset['Forward Gain%'].mean()*100, 2))
    print('Forward Gain% - std: ', round(hist_buy_subset['Forward Gain%'].std()*100,2), '\n')
