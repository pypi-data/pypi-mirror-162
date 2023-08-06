import re
import warnings
import datetime
import numpy as np
import pandas as pd
from typing import Union
from pandas.tseries.offsets import DateOffset
from pandas.tseries.frequencies import to_offset

import finlab
from finlab import data, market_info, report
from finlab import mae_mfe as maemfe
from finlab.utils import check_version, requests, set_global
from finlab.backtest_core import backtest_, get_trade_stocks
from finlab.dataframe import FinlabDataFrame

def warning_resample(resample):

  if '+' not in resample and '-' not in resample:
      return

  if '-' in resample and not resample.split('-')[-1].isdigit():
      return

  if '+' in resample:
      r, o = resample.split('+')
  elif '-' in resample:
      r, o = resample.split('-')

  warnings.warn(f"The argument sim(..., resample = '{resample}') will no longer support after 0.1.37.dev1.\n"
                f"please use sim(..., resample='{r}', offset='{o}d')", DeprecationWarning)



def download_backtest_encryption_function_factory():

    encryption_time = datetime.datetime.now()
    encryption = ''

    def ret():

        nonlocal encryption_time
        nonlocal encryption

        if datetime.datetime.now() < encryption_time + datetime.timedelta(days=1) and encryption:
            return encryption

        res = requests.get('https://asia-east2-fdata-299302.cloudfunctions.net/auth_backtest',
                {'api_token': finlab.get_token(), 'time': str(datetime.datetime.now())})

        if not res.ok:
            try:
                result = res.json()
            except:
                result = None

            print(result)
            return ''

        d = res.json()

        if 'v' in d and 'v_msg' in d and finlab.__version__ < d['v']:
            print(d['v_msg'])

        if 'msg' in d:
            print(d['msg'])

        encryption_time = datetime.datetime.now()
        encryption = d['encryption']

        return encryption
    return ret

download_backtest_encryption = download_backtest_encryption_function_factory()

def arguments(price, high, low, open_, position, resample_dates=None):
    resample_dates = price.index if resample_dates is None else resample_dates
    resample_dates = pd.Series(resample_dates).view(np.int64).values

    position = position.astype(float).fillna(0)
    price = price.astype(float)

    return [price.values,
            high.values,
            low.values,
            open_.values,
            price.index.view(np.int64),
            price.columns.astype(str).values,
            position.values,
            position.index.view(np.int64),
            position.columns.astype(str).values,
            resample_dates
            ]

def sim(position: Union[pd.DataFrame, pd.Series], resample=None, resample_offset=None, trade_at_price='close',
        position_limit=1, fee_ratio=1.425/1000,
        tax_ratio=3/1000, name=None, stop_loss=None,
        take_profit=None, touched_exit=False, live_performance_start=None,
        mae_mfe_window=0, mae_mfe_window_step=1, market='AUTO', upload=True):

    """Simulate the equity given the stock position history. 回測模擬股票部位所產生的淨值報酬率。

    Args:

        position (pd.DataFrame or pd.Series): Dataframe of the stock market position where index is date and columns are stock_id. Each row represents a stock portfolio, where the values are perentages. Negative values represent short position. If any sum of row is larger than 1, the normalization is perform, i.e., (1, 2) becomes (0.33, 0.66).

            買賣訊號紀錄。True 為持有， False 為空手。 若選擇做空position，只要將 sim(position) 改成負的 sim(-position.astype(float))即可做空。 系統預設使用資料為台股與加密貨幣，若要使用美股或其他市場，將資料格式設定同為台股範例即可，index為datetime格式，column為文字格式的標的代號，注意每日自動更新服務不適用台股與加密貨幣的資料。

        resample (str or None): rebalance position only on specified frequency.

            交易週期。將 position 的訊號以週期性的方式論動股票，預設為每天換股。其他常用數值為 W、 M 、 Q （每週、每月、每季換股一次），也可以使用 W-Fri 在週五的時候產生新的股票清單，並且於下週交易日下單。

            - `W`: Weekly
            - `W-Wed`: Every Wednesday
            - `M`: Monthly
            - `MS`: Start of every month
            - `ME`: End of every month
            - `Q`: Quaterly
            - `QS`: Start of every month
            - `QE`: End of every month

        resample_offset (str or None): add time offset to resample the position.
            交易週期的時間位移，例如。

            - '1D': 位移一天
            - '1H': 位移一小時
        trade_at_price (str or pd.DataFrame): rebalance on market 'close' or 'open'.

            選擇回測之還原股價以收盤價或開盤價計算，預設為'close'。可選'close'或'open'。
        position_limit (float): maximum amount of investing a stock.

            單檔標的持股比例上限，控制倉位風險。預設為None。範例：0.2，代表單檔標的最多持有 20 % 部位。
        fee_ratio (float): fee ratio of buying or selling a stock.

            交易手續費率，預設為台灣無打折手續費 0.001425。可視個人使用的券商優惠調整費率。
        tax_ratio (float): tax ratio of selling a stock.

            交易稅率，預設為台灣普通股一般交易交易稅率 0.003。若交易策略的標的皆為ETF，記得設成 0.001。
        name (str): name of the strategy.

            策略名稱，預設為 未指名。策略名稱。相同名稱之策略上傳會覆寫。命名規則:全英文或開頭中文，不接受開頭英文接中文。
        stop_loss (float): exit when stock return smaller than a specific amount. i.e., 0.2 means -20%
            停損基準，預設為None，不執行停損。範例：0.1，代表成本價虧損 10% 時產生出場訊號。
        take_profit (float): exit when stock return larger than a specific amount. i.e., 0.3 means +30%
            停利基準，預設為None，不執行停利。範例：0.1，代表成本價獲利 10% 時產生出場訊號。
        touched_exit (bool): `True`: exit immediately whenever stop loss or take profit price is touched. `False`: exit tomorrow if the price touches stop loss or take profit. 是否在回測時，使用觸價停損停利？
        mae_mfe_window (int): 計算mae_mfe於進場後於不同持有天數下的數據變化，主要應用為edge_ratio (優勢比率)計算。預設為0，則Report.display_mae_mfe_analysis(...)中的edge_ratio不會顯現。
        mae_mfe_window_step (int): 與mae_mfe_window參數做搭配，為時間間隔設定，預設為1。若mae_mfe_window設20，mae_mfe_window_step設定為2，相當於python的range(0,20,2)，以2日為間距計算mae_mfe。
        market (str or class(finlab.market_info.MarketInfo)): 可選擇`'TWSTOCK', 'CRYPTO'`，分別為台股或加密貨幣，
                                                              或繼承 finlab.market_info.MarketInfo 開發回測市場類別。
        upload (bool): 上傳策略至finlab網站，預設為True，上傳策略。範例： False，不上傳，可用 finlab.backtest.sim(position, upload=False, ...).display() 快速檢視策略績效。
    Returns:
        (finlab.analysis.Report):回測數據報告
    Examples:
        Assume the history of portfolio is construct as follows: When market close on 2021-12-31, the portfolio {B: 0.2, C: 0.4} is calculated. When market close on 2022-03-31, the portfolio {A:1} is calculated.

        |            | Stock 2330 | Stock 1101 | Stock 2454 |
        |------------|------------|------------|------------|
        | 2021-12-31 | 0%         | 20%        | 40%        |
        | 2022-03-31 | 100%       | 0          | 0          |

        With the portfolio, one could backtest the equity history as follows:

        ``` py
        import pandas as pd
        from finlab import backtest

        position = pd.DataFrame({
            '2330': [0, 1],
            '1101': [0.2, 0],
            '2454': [0.4, 0]
        }, index=pd.to_datetime(['2021-12-31', '2022-03-31']))

        report = backtest.sim(position)
        ```


    """

    # check version
    check_version()

    # auto detect market type
    if market == 'AUTO':
        market = 'TWSTOCK'

        if isinstance(position, pd.DataFrame) and (position.columns.str.find('USDT') != -1).any():
            market = 'CRYPTO'
        if isinstance(position, pd.Series) and 'USDT' in position.name:
            market = 'CRYPTO'

    # get market position according to market type
    if isinstance(market, str):
        assert market in ['TWSTOCK', 'CRYPTO']
        market = {
            'TWSTOCK': market_info.TWMarketInfo,
            'CRYPTO': market_info.CryptoMarketInfo,
        }[market]

    # determine trading price
    price = trade_at_price
    if isinstance(trade_at_price, str):
        price = market.get_price(trade_at_price, adj=True)

    if isinstance(trade_at_price, pd.DataFrame) and touched_exit:
        print('**WARNING: Using trade_at_price as dataframe without high, and low price. Candle information is not completed.')
        print('           The backtest result can be incorrect when touched_exit=True.')
        print('           If the complete backtest result is required, please implement MarketInfo with get_price function.')
        print('           MarketInfo details: https://doc.finlab.tw/reference/market_info/')
        print('           And use backtest.sim(..., market=MarketInfo) during backtest, so that the correct information is accessable from backtest.sim().')

    high = price
    low = price
    open_ = price
    if touched_exit:
        high = market.get_price('high', adj=True).reindex_like(price)
        low = market.get_price('low', adj=True).reindex_like(price)
        open_ = market.get_price('open', adj=True).reindex_like(price)

    # check position types
    if isinstance(position, pd.Series):
        if position.name in price.columns:
            position = position.to_frame()
        else:
            raise Exception('Asset name not found. Please asign asset name by "position.name = \'2330\'".')

    # check name is valid
    if name:
        head_is_eng = len(re.findall(
            r'[\u0041-\u005a|\u0061-\u007a]', name[0])) > 0
        has_cn = len(re.findall('[\u4e00-\u9fa5]', name[1:])) > 0
        if head_is_eng and has_cn:
            raise Exception('Strategy Name Error: 名稱如包含中文，需以中文當開頭。')
        for c in '()[]+-|!@#$~%^={}&*':
            name = name.replace(c, '_')

    # check position is valid
    if position.abs().sum().sum() == 0 or len(position.index) == 0:
        raise Exception('Position is empty and zero stock is selected.')

    # format position index
    if isinstance(position.index[0], str):
        position = FinlabDataFrame(position).index_str_to_date()

    # if position date is very close to price end date, run all backtesting dates
    assert len(position.shape) >= 2
    delta_time_rebalance = position.index[-1] - position.index[-3]
    backtest_to_end = position.index[-1] + \
        delta_time_rebalance > price.index[-1]

    position = position[position.index <= price.index[-1]]
    backtest_end_date = price.index[-1] if backtest_to_end else position.index[-1]

    # resample dates
    dates = None
    next_trading_date = position.index[-1].tz_localize(None)
    if isinstance(resample, str):

        warning_resample(resample)

        # add additional day offset
        offset_days = 0
        if '+' in resample:
            offset_days = int(resample.split('+')[-1])
            resample = resample.split('+')[0]
        if '-' in resample and resample.split('-')[-1].isdigit():
            offset_days = -int(resample.split('-')[-1])
            resample = resample.split('-')[0]

        # generate rebalance dates
        dates = pd.date_range(
            position.index[0], position.index[-1]+ datetime.timedelta(days=720), freq=resample, tz=position.index.tzinfo)
        dates += DateOffset(days=offset_days)
        if resample_offset is not None:
            dates += to_offset(resample_offset)
        dates = [d for d in dates if position.index[0]
                 <= d and d <= position.index[-1]]

        # calculate the latest trading date
        next_trading_date = min(
                set(pd.date_range(position.index[0],
                    datetime.datetime.now(position.index.tzinfo)
                    + datetime.timedelta(days=720),
                    freq=resample)) - set(dates))

        if dates[-1] != position.index[-1]:
            dates += [next_trading_date]
    elif resample == None:
        # user set resample to None. Rebalance everyday might cause over transaction.
        # remove rebalance date if portfolio is the same.
        position = position.loc[position.diff().abs().sum(axis=1) != 0]

    if stop_loss is None or stop_loss == 0:
        stop_loss = 1

    if take_profit is None or take_profit == 0:
        take_profit = np.inf

    if dates is not None:
        position = position.reindex(dates, method='ffill')

    encryption = download_backtest_encryption()

    if encryption == '':
      return

    creturn_value = backtest_(*arguments(price, high, low, open_, position, dates),
                              encryption=encryption,
                              fee_ratio=fee_ratio, tax_ratio=tax_ratio,
                              stop_loss=stop_loss, take_profit=take_profit,
                              touched_exit=touched_exit, position_limit=position_limit,
                              mae_mfe_window=mae_mfe_window, mae_mfe_window_step=mae_mfe_window_step)

    total_weight = position.abs().sum(axis=1)

    position = position.div(total_weight.where(total_weight!=0, np.nan), axis=0).fillna(0)
    position = position.clip(-abs(position_limit), abs(position_limit))

    creturn = pd.Series(creturn_value, price.index)
    creturn = creturn[(creturn != 1).cumsum().shift(-1, fill_value=1) != 0]
    creturn = creturn.loc[:backtest_end_date]
    if len(creturn) == 0:
        creturn = pd.Series(1, position.index)

    trades, operation_and_weight = get_trade_stocks(position.columns.astype(str).values, price.index.view(np.int64))
    trades = pd.DataFrame(trades)
    m = pd.DataFrame()

    if len(trades) != 0:

        trades.columns = ['stock_id', 'entry_date', 'exit_date',
                     'entry_sig_date', 'exit_sig_date',
                     'position', 'period', 'entry_index', 'exit_index']

        trades.index.name = 'trade_index'

        for col in ['entry_date', 'exit_date', 'entry_sig_date', 'exit_sig_date']:
            trades[col] = pd.to_datetime(trades[col])
            trades[col] = trades[col].dt.tz_localize(None)

        trades.loc[trades.exit_index == -1, ['exit_date', 'exit_sig_date']] = pd.NaT

        m = pd.DataFrame(maemfe.mae_mfe)
        nsets = int((m.shape[1]-1) / 6)

        metrics = ['mae', 'gmfe', 'bmfe', 'mdd', 'pdays', 'return']

        tuples = sum([[(n, metric) if n == 'exit' else (n * mae_mfe_window_step, metric)
                       for metric in metrics] for n in list(range(nsets)) + ['exit']], [])

        m.columns = pd.MultiIndex.from_tuples(
            tuples, names=["window", "metric"])
        m.index.name = 'trade_index'
        m[m == -1] = np.nan

        trades['return'] = m.iloc[:, -1]

        if touched_exit:
            trades['return'] = trades['return'].clip(-abs(stop_loss), abs(take_profit))

    r = report.Report(
        creturn=creturn,
        position=position,
        fee_ratio=fee_ratio,
        tax_ratio=tax_ratio,
        trade_at=trade_at_price,
        next_trading_date=next_trading_date,
        market_info=market)

    r.resample = resample
    r.stop_loss = stop_loss
    r.take_profit = take_profit
    r.live_performance_start = live_performance_start

    if len(trades) != 0:
        r.trades = trades
        r.add_trade_info('trade_price', market.get_price(trade_at_price, adj=False), ['entry_date', 'exit_date'])

    if len(m) != 0:
        r.mae_mfe = m

        # clip max loss and profit to stop_loss and take_profit if touched_exit is on
        if touched_exit and len(r.mae_mfe) > 0 and 'exit' in r.mae_mfe.columns:
            exit = r.mae_mfe.exit.copy()
            r.mae_mfe['exit'] = (exit
                .assign(gmfe=exit.gmfe.clip(-abs(stop_loss), abs(take_profit)))
                .assign(bmfe=exit.bmfe.clip(-abs(stop_loss), abs(take_profit)))
                .assign(mae=exit.mae.clip(-abs(stop_loss), abs(take_profit)))
                .assign(mdd=exit.mdd.clip(-abs(stop_loss), abs(take_profit))))

    if len(operation_and_weight['actions']) != 0:

        # find selling and buying stocks
        actions = pd.Series(operation_and_weight['actions'])
        actions.index = r.position.columns[actions.index]
        r.actions = actions

        sell_sids = actions[actions == 'exit'].index
        buy_sids = actions[actions == 'enter'].index

        if len(trades):
            r_position = set(trades.stock_id[trades.exit_sig_date.isnull()])

            # check if the sell stocks are in the current position
            assert len(set(sell_sids) - r_position) == 0

            # fill exit_sig_date and exit_date
            trades.loc[trades.stock_id.isin(sell_sids), 'exit_sig_date'] = \
                trades.loc[trades.stock_id.isin(sell_sids), 'exit_sig_date'].fillna(r.position.index[-1].tz_localize(None))
            trades.loc[trades.stock_id.isin(sell_sids), 'exit_date'] = \
                trades.loc[trades.stock_id.isin(sell_sids), 'exit_date']

            final_trades = pd.concat([trades, pd.DataFrame({
              'stock_id': buy_sids,
              'entry_date': pd.NaT,
              'entry_sig_date': r.position.index[-1].tz_localize(None),
              'exit_date': pd.NaT,
              'exit_sig_date': pd.NaT,
            })], ignore_index=True)

            r.trades = final_trades
    else:
        r.actions = pd.Series(dtype=object)

    # add mae mfe to report
    if hasattr(r, 'trades') and hasattr(r, 'mae_mfe'):
        trades = r.trades
        mae_mfe = r.mae_mfe
        exit_mae_mfe = mae_mfe['exit'].copy()
        exit_mae_mfe = exit_mae_mfe.drop(columns=['return'])
        r.trades = pd.concat([trades, exit_mae_mfe], axis=1)
        r.trades.index.name = 'trade_index'

    # calculate r.current_trades
    # find trade without end or end today
    maxday = r.trades.entry_sig_date.max()
    r.current_trades = r.trades[(r.trades.entry_sig_date == maxday ) | (r.trades.exit_sig_date == maxday) | (r.trades.exit_sig_date.isnull())].set_index('stock_id')
    r.next_trading_date = max(r.current_trades.entry_sig_date.max(), r.current_trades.exit_sig_date.max())

    r.current_trades['weight'] = 0
    if len(operation_and_weight['weights']) != 0:
        r.weights = pd.Series(operation_and_weight['weights'])
        r.weights.index = r.position.columns[r.weights.index]
        r.current_trades['weight'] = r.weights.reindex(r.current_trades.index).fillna(0)

    r.current_trades['next_weights'] = 0
    if len(operation_and_weight['next_weights']) != 0:
        r.next_weights = pd.Series(operation_and_weight['next_weights'])
        r.next_weights.index = r.position.columns[r.next_weights.index]

        # normalize weight
        total_weight = r.next_weights.abs().sum()

        if total_weight > 1:
          r.next_weights /= total_weight

        r.current_trades['next_weights'] = r.next_weights.reindex(r.current_trades.index).fillna(0)

    # fill stock id to trade history
    if len(trades) != 0:
        snames = market.get_asset_id_to_name()
        r.trades['stock_id'] = r.trades.stock_id.map(lambda sid: f"{sid + ' ' + snames[sid] if sid in snames else sid}")
        r.current_trades.index = r.current_trades.index.map(lambda sid: f"{sid + ' ' + snames[sid] if sid in snames else sid}")

    if hasattr(r, 'actions') and len(r.actions) != 0:
        snames = market.get_asset_id_to_name()
        r.actions.index = r.actions.index.map(lambda sid: f"{sid + ' ' + snames[sid] if sid in snames else sid}")

    if hasattr(r, 'weights') and len(r.weights) != 0:
        snames = market.get_asset_id_to_name()
        r.weights.index = r.weights.index.map(lambda sid: f"{sid + ' ' + snames[sid] if sid in snames else sid}")

    set_global('backtest_report', r)

    if not upload:
        return r

    r.upload(name)
    return r
