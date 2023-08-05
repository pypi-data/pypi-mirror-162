import random
import pandas as pd
import numpy as np
import yfinance
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
plt.rcParams['axes.facecolor'] = 'lightblue'


def create_ts(params={'data': np.array([]), 'timestamps': pd.Series([1])}):
    '''
    input paramters:
    ------------------------------------------------
    params: dict (dictionary) containing the dates with column named "timestamps"
            and the data containing the data corresponding to the dates.

    >>>Example:
    >>>create_ts(params={'data': np.array([1, 2, 3]), 'timestamps': pd.Series(['2017-01-01', '2018-02-01', '2016-05-07'])})

    Returns: pd.Series with date as index and data.
    '''
    return pd.Series(params['data'], index=params['timestamps'].values)


def get_signal_strategy(stock_short, stock_long):
    '''
    input: Takes 2 parameters : short time period moving average, long time period moving average.

    Returns: Digital Signal of the Strategy
    '''
    arr = stock_short - stock_long
    signal = np.sign(arr)
    signal = np.nan_to_num(signal)

    return signal


def split_func(X, test_size=0.2):
    '''
    input: An array or list
    test_size = 0.2 (the size of test set)
                default value is 20%.
    '''
    train_size = 1 - test_size
    return X[:int(train_size*len(X))], X[int(train_size*len(X)):]


def get_strategy_aroon(up, down):
    '''
    input: up , down signals of Aroon indicator
    ---------------------------------------------------------------
    Parameters:
              up: Array Like
              down: Array Like
    Returns: digital output of the signal .
    '''

    signal = [0, 0]
    count = 0

    for i in range(2, len(up)):
        if up[i-2] < down[i-2] and up[i] > down[i]:
            signal.append(1)
        elif down[i-2] < up[i-2] and down[i] > up[i]:
            signal.append(-1)
        elif up[i] > 50 and down[i] < 50:
            signal.append(1)
        elif up[i] < 50 and down[i] > 50:
            signal.append(-1)
        else:
            signal.append(0)

    return signal


def sigmoid(x):
    '''
    input: Accepts a list or array like input
    outputs: scaled value between 0 and 1.
    >>>Example:
    >>>sigmoid([1])
    >>>[0.73]
    '''
    return np.around(1/(1 + np.e**(-x)), 2)


def digital_signal(super_indicator):
    '''
    input: Given a list or array like input converts it into a digital output
    Example:
    >>>digital_signal([1, 2, 3, 4, 5, 6, 7])
    >>>[1, 1, 1, 1, 1, 1, 1]
    '''
    signal = []

    for i in super_indicator:
        j = sigmoid(i)
        if j >= 0.5:
            signal.append(1)
        else:
            signal.append(-1)

    return signal


def signal_strategy_bollb(up, down, price):
    '''
    input: Takes 3 parameters : up, down and price (list or array)
    The 3 bands of the bollinger band
    ---------------------------------------------------------------
    Parameters:
              up: Array Like
              down: Array Like
              price: Array Like

    Returns: Digital Signal of the Strategy
    '''

    signal = []

    for i in range(len(price)):
        if (up[i] - price[i]) > (price[i] - down[i]):
            signal.append(1)
        elif (up[i] - price[i]) - (price[i] - down[i]) < 1:
            signal.append(0)
        else:
            signal.append(-1)

    return signal

# For Reinforcement Learning Environments
def summary(envF, env):
    '''
    Supply the train, test environment variables envF (training), env(testing).
    Make sure the environments contains a dataframe named "return_df" which contains the columns
    "action_t" - For action taken
    "reward_t" - Reward Received
    "price_t" - Price of stock (t - indicates t-th day).

    Example:
    price_t      reward_t     action_t
    20.00        100          10
    30.00        -100         10
    '''

    train = pd.DataFrame(envF.return_df)
    test = pd.DataFrame(env.return_df)

    # Time Periods
    train_period = (pd.to_datetime(envF.end) - pd.to_datetime(envF.start))//np.timedelta64(1, 'M')
    test_period = (pd.to_datetime(env.end) - pd.to_datetime(env.start))//np.timedelta64(1, 'M')

    # Daily Returns
    train['returns'] = (train['reward_t']/abs(train['action_t'])) / train['price_t']
    test['returns'] = (test['reward_t']/abs(test['action_t'])) / test['price_t']

    train.fillna(0, inplace=True)
    test.fillna(0, inplace=True)

    # Compounded Returns
    train['ret_cp'] = 0
    test['ret_cp'] = 0

    train.loc[0, 'ret_cp'] = train.loc[0, 'returns']
    train_ret = train['returns'].to_list()
    for t in range(1, len(train['returns'])):
        train.loc[t, 'ret_cp'] = (1 + train.loc[t-1, 'ret_cp']) * (1 + train_ret[t]) - 1

    test.loc[0, 'ret_cp'] = test.loc[0, 'returns']
    test_ret = test['returns'].to_list()
    for t in range(1, len(test['returns'])):
        test.loc[t, 'ret_cp'] = (1 + test.loc[t-1, 'ret_cp']) * (1 + test_ret[t]) - 1


    # Cumulative Rewards
    train['cum_reward'] = train['reward_t'].cumsum()
    test['cum_reward'] = test['reward_t'].cumsum()

    # The total df
    total_df = pd.concat([train, test], axis=0)
    total_df.reset_index(drop=True, inplace=True)

    train_index = len(train['returns'].values)

    # Total Reward
    total_reward_train = train['reward_t'].sum()
    total_reward_test = test['reward_t'].sum()

    # Return Per Period
    train_period_return = (train['ret_cp'].loc[len(train['ret_cp'])-1]/train_period) * 100
    test_period_return = (test['ret_cp'].loc[len(test['ret_cp'])-1]/test_period) * 100

    # Annualized Return
    train_annual_return = train_period_return * 12
    test_annual_return = test_period_return * 12

    # Volatility
    train_vol = np.std(train['returns']) * np.sqrt(252)
    test_vol = np.std(test['returns']) * np.sqrt(252)

    # Sharpe Ratio
    train_sharpe = (train['returns'].mean()/np.std(train['returns'])) * np.sqrt(252)
    test_sharpe = (test['returns'].mean()/np.std(test['returns'])) * np.sqrt(252)

    # Kurtosis
    train_kurtosis = (kurtosis(train['returns'], fisher=False))
    test_kurtosis = (kurtosis(test['returns'], fisher=False))

    # data for buy/sell points
    buy, sell, hold = [], [], []
    action_list = np.arange(len(total_df['action_t']))

    for i, j  in enumerate(action_list):
        if total_df.loc[i, 'action_t'] > 0:
            buy.append(j)
        elif total_df.loc[i, 'action_t'] < 0:
            sell.append(j)
        else:
            hold.append(j)


    # Legend Items
    green_triangle = mlines.Line2D([], [], color='green', marker='^', linestyle='None',
                          markersize=10, label='Buy')

    red_triangle = mlines.Line2D([], [], color='red', marker='v', linestyle='None',
                          markersize=10, label='Sell')




    # buy or sell points
    plt.figure(figsize=(15, 5))
    plt.title("Buy/Sell Points", fontweight="bold")
    plt.plot(total_df['price_t'].rolling(30).mean(), 'b-')
    plt.plot(buy, total_df.loc[buy, 'price_t'], 'g^')
    plt.plot(sell, total_df.loc[sell, 'price_t'], 'rv')
    plt.xlabel("Days", fontsize=13)
    plt.ylabel("Price in $", fontsize=13)
    plt.grid()
    plt.legend(handles=[green_triangle, red_triangle])

    plt.tight_layout()


    # cum_reward plot
    plt.figure(figsize=(15, 5))
    plt.title("Train vs Test Period Rewards (30 days Moving)", fontweight="bold")
    plt.plot(total_df['cum_reward'].loc[:train_index].rolling(30).mean(), 'g-')
    plt.plot(total_df['cum_reward'].loc[train_index:].rolling(30).mean(), 'r-')
    plt.xlim(0, 3000)
    plt.xlabel("Days", fontsize=13)
    plt.ylabel("Cumulative Rewards", fontsize=13)
    plt.grid()
    plt.legend(['Train', 'Test'], fontsize=13)

    plt.tight_layout()


    # Final DataFrame
    df = pd.DataFrame(data=[
                            [envF.start, env.start],
                            [envF.end, env.end],
                            [int(train_period), int(test_period)],
                            [total_reward_train, total_reward_test],
                            [train_period_return, test_period_return],
                            [train_annual_return, test_annual_return],
                            [train_vol, test_vol],
                            [train_sharpe, test_sharpe],
                            [train_kurtosis, test_kurtosis]
                            ] ,

                      columns=['Train', 'Test'],
                      index=['Start Date', 'End Date', 'Time Period (in Months)', 'Total Reward', 'Return/Month %', 'Annual Return %',
                             'Annual Volatility', 'Sharpe Ratio', 'Kurtosis'])

    return df


def financial_summary(df_rets, frequency='D'):
    '''
    Must supply a dataframe with date and daily retruns as columns
    Note - Don't supply daily returns as % .
    Example:
    date           returns
    2018-02-09     0.25
    2018-02-10     0.29

    frequency : Daily (D), Monthly(M) or Weekly(W), default - 'D'.
                Describes the frequency of data provided.

    Outputs: pd.DataFrame()
    '''
    if frequency == 'D':
        df_rets['c_ret'] = (1 + df_rets['returns']).cumprod() - 1
        days = (pd.to_datetime(df_rets.iloc[len(df_rets)-1, 0]) - pd.to_datetime(df_rets.iloc[0, 0])) // np.timedelta64(1, 'D')
        volatility = np.std(df_rets['returns']) * np.sqrt(252)
        returns = ((df_rets['c_ret'].values[-1])/(days)) * 252
        sharpe = returns/volatility

        return pd.DataFrame(data=[df_rets.iloc[0, 0],
                           df_rets.iloc[len(df_rets)-1, 0],
                           days,
                           np.around(returns*100, 2),
                           volatility,
                           sharpe,
                           kurtosis(df_rets['returns'], fisher=False),
                           drawdown(df_rets['returns'])['Drawdown'].min()],

                          columns=['Summary'],
                          index=['Start Date', 'End Date', 'Time Period (in Days)', 'Annual Return %',
                                 'Annual Volatility', 'Sharpe Ratio', 'Kurtosis', 'Max Drawdown'])

    elif frequency == 'M':
        df_rets['c_ret'] = (1 + df_rets['returns']).cumprod() - 1
        months = (pd.to_datetime(df_rets.iloc[len(df_rets)-1, 0]) - pd.to_datetime(df_rets.iloc[0, 0])) // np.timedelta64(1, 'M')
        volatility = np.std(df_rets['returns']) * np.sqrt(12)
        returns = ((df_rets['c_ret'].values[-1])/(months)) * 12
        sharpe = returns/volatility

        return pd.DataFrame(data=[df_rets.iloc[0, 0],
                           df_rets.iloc[len(df_rets)-1, 0],
                           months,
                           np.around(returns*100, 2),
                           volatility,
                           sharpe,
                           kurtosis(df_rets['returns'], fisher=False),
                           drawdown(df_rets['returns'])['Drawdown'].min()],

                          columns=['Summary'],
                          index=['Start Date', 'End Date', 'Time Period (in Months)', 'Annual Return %',
                                 'Annual Volatility', 'Sharpe Ratio', 'Kurtosis', 'Max Drawdown'])

    elif frequency == 'W':
        df_rets['c_ret'] = (1 + df_rets['returns']).cumprod() - 1
        weeks = (pd.to_datetime(df_rets.iloc[len(df_rets)-1, 0]) - pd.to_datetime(df_rets.iloc[0, 0])) // np.timedelta64(1, 'W')
        volatility = np.std(df_rets['returns']) * np.sqrt(52)
        returns = ((df_rets['c_ret'].values[-1])/(weeks)) * 52
        sharpe = returns/volatility
        
        return pd.DataFrame(data=[df_rets.iloc[0, 0],
                           df_rets.iloc[len(df_rets)-1, 0],
                           weeks,
                           np.around(returns*100, 2),
                           volatility,
                           sharpe,
                           kurtosis(df_rets['returns'], fisher=False),
                           drawdown(df_rets['returns'])['Drawdown'].min()],

                          columns=['Summary'],
                          index=['Start Date', 'End Date', 'Time Period (in Weeks)', 'Annual Return %',
                                 'Annual Volatility', 'Sharpe Ratio', 'Kurtosis', 'Max Drawdown'])


def drawdown(return_series: pd.Series):
    """Takes a time series of asset returns.
       returns a DataFrame with columns for
       the wealth index,
       the previous peaks, and
       the percentage drawdown
    """
    wealth_index = 1000*(1+return_series).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = (wealth_index - previous_peaks)/previous_peaks
    return pd.DataFrame({"Wealth": wealth_index,
                         "Previous Peak": previous_peaks,
                         "Drawdown": drawdowns})

def analyze_strategy(actions, df, frequency='D', plot=False):
    '''
    actions: a list , np.array or series of actions .
    plot: default-False, boolean
    df: prices_with_dates - a list of prices along with their respective dates (pd.DataFrame)
                            name of the price column should be "prices"
                            Example :
                            Date           prices
                            "2017-01-09"   22.87

    frequency : Daily (D), Monthly(M) or Weekly(W), default - 'D'.
                Describes the frequency of data provided.

    Example:
    >>> analyze_strategy([1, 1, 1, ..-1], df, 'D', True)
    actions : +1 , 0 or -1 . (Buy, Hold or Sell)

    outputs summary for the actions taken .
    '''

    df['actions'] = actions
    df['returns'] = df['prices'].pct_change() * df['actions'].shift(1)
    df['c_ret'] = (1 + df['returns']).cumprod() - 1
    df.fillna(0, inplace=True)

    if frequency == 'D':
        days = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'D')
        volatility = np.std(df['returns']) * np.sqrt(252)
        returns = ((df['c_ret'].values[-1])/(days)) * 252
        sharpe = returns/volatility
    elif frequency == 'M':
        months = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'M')
        volatility = np.std(df['returns']) * np.sqrt(12)
        returns = ((df['c_ret'].values[-1])/(months)) * 12
        sharpe = returns/volatility
    elif frequency == 'W':
        weeks = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'W')
        volatility = np.std(df['returns']) * np.sqrt(52)
        returns = ((df['c_ret'].values[-1])/(weeks)) * 52
        sharpe = returns/volatility

    if plot:
        dq = df.set_index(df.columns[0])
        plt.title("Returns over the years")
        dq['c_ret'].rolling(30).mean().plot(figsize=(12, 6))
        plt.xlabel("Days")
        plt.ylabel("Returns (Compounded)")


    return pd.DataFrame(data=[df.iloc[0, 0],
                           df.iloc[len(df)-1, 0],
                           days,
                           np.around(returns*100, 2),
                           volatility,
                           sharpe,
                           kurtosis(df['returns'], fisher=False),
                           drawdown(df['returns'])['Drawdown'].min()],

                          columns=['Summary'],
                          index=['Start Date', 'End Date', f'Time Period (in ({frequency}))', 'Annual Return %',
                                 'Annual Volatility', 'Sharpe Ratio', 'Kurtosis', 'Max Drawdown'])


def get_benchmark_result(ticker, start, end, price_col='Close', frequency='D', plot=False):
    '''
    start: start date
    end: end date
    ticker: symbol (of Benchmark index eg: ^NSEI for NIFTY)
    plot: default-False, boolean

    frequency : Daily (D), Monthly(M) or Weekly(W), default - 'D'.
                Describes the frequency of data provided.

    price : Open, High , Low or Close . Default = 'Close' .

    returns summary for the benchmark
    '''
    data = yfinance.download(tickers=ticker, start=start, end=end, interval='1d')

    if frequency == 'D':
        df = data.loc[:, price_col].reset_index().rename(columns={price_col: "prices"})
        df['returns'] = df['prices'].pct_change()
        df['c_ret'] = (1 + df['returns']).cumprod() - 1
        df.fillna(0, inplace=True)

        days = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'D')
        volatility = np.std(df['returns']) * np.sqrt(252)
        returns = ((df['c_ret'].values[-1])/(days)) * 252
        sharpe = returns/volatility
    elif frequency == 'M':
        data = data.resample('M').last()
        df = data.loc[:, price_col].reset_index().rename(columns={price_col: "prices"})
        df['returns'] = df['prices'].pct_change()
        df['c_ret'] = (1 + df['returns']).cumprod() - 1
        df.fillna(0, inplace=True)

        days = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'M')
        volatility = np.std(df['returns']) * np.sqrt(12)
        returns = ((df['c_ret'].values[-1])/(days)) * 12
        sharpe = returns/volatility
    elif frequency == 'W':
        data = data.resample('W').last()
        df = data.loc[:, price_col].reset_index().rename(columns={price_col: "prices"})
        df['returns'] = df['prices'].pct_change()
        df['c_ret'] = (1 + df['returns']).cumprod() - 1
        df.fillna(0, inplace=True)

        days = (pd.to_datetime(df.iloc[len(df)-1, 0]) - pd.to_datetime(df.iloc[0, 0]))//np.timedelta64(1, 'W')
        volatility = np.std(df['returns']) * np.sqrt(52)
        returns = ((df['c_ret'].values[-1])/(days)) * 52
        sharpe = returns/volatility

    if plot:
        dq = df.set_index("Date")
        plt.title("Returns over the years")
        dq['c_ret'].rolling(30).mean().plot(figsize=(12, 6))
        plt.xlabel("Days")
        plt.ylabel("Returns (Compounded)")


    return pd.DataFrame(data=[str(df.iloc[0, 0])[:10],
                           str(df.iloc[len(df)-1, 0])[:10],
                           days,
                           np.around(returns*100, 2),
                           volatility,
                           sharpe,
                           kurtosis(df['returns'], fisher=False),
                           drawdown(df['returns'])['Drawdown'].min()],

                          columns=['Benchmark Summary'],
                          index=['Start Date', 'End Date', f'Time Period (in ({frequency}))', 'Annual Return %',
                                 'Annual Volatility', 'Sharpe Ratio', 'Kurtosis', 'Max Drawdown'])


def MDD(rets):
    '''
    Input: Takes a return series and returns the maximum drawdown.
    '''
    final = rets
    maxdrwdn = (1+final).cumprod().diff().min()

    return maxdrwdn
