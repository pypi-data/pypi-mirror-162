from abc import ABC, abstractmethod
from finlab.report import Report as ReportPyx


class Analysis(ABC):

    def is_market_info_supported(self, market_info):
        """Check if market info is supported

        Returns:
          (bool): True, support. False not support.
        """
        return True

    @staticmethod
    def calculate_trade_info(self, report):
        """Additional trade info can be calculated easily.

        User could override this function if additional trade info is required for later anlaysis.

        Examples:

          ``` py
          from finlab.analysis import Analysis

          class SomeAnalysis(Analysis):
            def calculate_trade_info(self, report):
              return [
                ['股價淨值比', data.get('price_earning_ratio:股價淨值比'), 'entry_sig_date']
              ]

          report.run_analysis(SomeAnalysis())
          trades = report.get_trades()

          assert '股價淨值比@entry_sig_date' in trades.columns

          print(trades)
          ```
        """
        return []

    def analyze(self, report):
        """Analyze trading report.

        One could assume self.caluclate_trade_info will be executed before self.analyze,
        so the `report.get_trades()` will contain the required trade info.
        """
        pass

    def display(self):
        """Display result

        When implement this function, returning Plotly figure instance is recommended.
        """
        pass


class Report(ReportPyx):
    def __init__(self, creturn, position, fee_ratio, tax_ratio, trade_at, next_trading_date, market_info):
        """策略回測基礎報告
        Args:
          creturn (pd.Series): 策略報酬率時間序列。
          position (pd.DataFrame): 策略報酬率時間序列。
          fee_ratio (float): 交易手續費率，預設為台灣無打折手續費 0.001425。可視個人使用的券商優惠調整費率。
          tax_ratio (float): 交易稅率，預設為台灣普通股一般交易交易稅率 0.003。若交易策略的標的皆為 ETF，記得設成 0.001。
          trade_at (str): 選擇回測之還原股價以收盤價或開盤價計算，預設為 close。可選 close 或 open。
          next_trading_date (str): 預期下期換股日。
          market_info (str or class(finlab.market_info.MarketInfo) ): 可選擇`'TWSTOCK', 'CRYPTO'`，分別為台股或加密貨幣，
                                                                     或繼承 `finlab.market_info.MarketInfo` 開發回測市場類別。
        Attributes:
          benchmark (pd.Series): 對標報酬率曲線的時間序列，用於 Report.display() 顯示策略報酬率比較標準。
          update_date (str): 用於 Report.display() 顯示策略對標的報酬率曲線。
          asset_type (str): 資產類別， tw_stock 或 crypto。
          last_trading_date (str): 最近產生交易訊號的日期。
        """
        super().__init__(creturn, position, fee_ratio, tax_ratio, trade_at, next_trading_date, market_info)

    def upload(self, name=None):
        """上傳回測報告資料到量化平台網站
        Args:
          name (str): 策略名稱。
        """
        return super().upload(name)

    def position_info(self):
        """取得近期持有部位與預期換股資訊
        Returns:
          (dict): 部位資訊
        """
        return super().position_info()

    def display(self):
        """顯示回測報酬率圖組
        Returns:
          (plotly.graph_objects.Figure): 圖組

        Examples:
          設定對標指數
          ```py
          from finlab import data
          ...
          report = sim(position, resample='Q',mae_mfe_window=30,mae_mfe_window_step=2)
          report.benchmark = data.get('benchmark_return:發行量加權股價報酬指數').squeeze()
          report.display()
          ```
          ![報酬率圖組](img/analysis/display.png)
        """
        return super().display()

    def get_mae_mfe(self):
        """取得 mae_mfe 時序資料

        Returns:
          (pd.DataFrame): 波動時序資料
        """
        return super().get_mae_mfe()

    def get_trades(self):
        """取得回測逐筆交易紀錄
        ## 重點欄位說明
        * exit_sig_date:進場訊號產生日。
        * entry_sig_date:出場訊號產生日。
        * entry_date:進場日。
        * exit_date:出場日。
        * position:持有佔比。
        * period:持有天數。
        * return:報酬率。
        * trade_price@entry_date:進場價。
        * trade_price@exit_date:出場價。
        * mae:持有期間最大不利報酬率幅度。
        * gmfe:持有期間最大有利報酬率幅度。
        * bmfe:mae發生前的最大有利報酬率幅度。
        * mdd:持有期間最大回撤。
        * pdays:處於獲利時的天數。
        * entry_volatility@entry_sig_date: 進場訊號產生日的股價真實波動率。

        Returns:
          (pd.DataFrame): 交易紀錄
        """
        return super().get_trades()

    def get_stats(self, resample='1d', riskfree_rate=0.02):
        """取得策略統計數據
        取得數據如夏普率、索提諾比率、最大回檔、近期報酬率統計...
        Args:
           resample (str): 報酬率檢測週期，其他常用數值為 W、 M 、Q（每週、每月、每季換股）。
           riskfree_rate (float): 無風險利率。
        Returns:
          (dict): 策略指標數據。
        """
        return super().get_stats(resample, riskfree_rate)

    def run_analysis(self, analysis, display=True, **kwargs):
        """執行策略分析外掛模組
        Args:
          analysis (str or object): `finlab.analysis`內的分析模組名稱，ex:`'liquidityAnalysis'`。
          display (bool): 是否顯示模組分析圖表。
          **kwargs (mapping, optional): 分析模組參數調整。
        Returns:
          (pd.DataFrame or plotly.graph_objects.Figure): 分析結果
        """
        return super().run_analysis(analysis, display=display, **kwargs)

    def display_mae_mfe_analysis(self, violinmode='group', mfe_scatter_x='mae', **kwargs):
        """ 顯示波動分析圖組

        [分析使用說明](https://www.finlab.tw/display_mae_mfe_analysis/)。
        Args:
          violinmode (str): violin 型態統計圖樣式，模式分為 group 與 overlay。
                            預設為 group，group 模式為將交易勝敗分群統計'，overlay 採取全數統計。
          mfe_scatter_x (str): 子圖 2-1、2-2 MFE 散點圖的X軸比較項目設定，可選`'mae' or 'return'`。
          **kwargs (dict): 其餘圖表外觀(layout)參數。
        Returns:
          (plotly.graph_objects.Figure): 波動分析圖組

        Examples:
          group :
          ![波動分析圖組](img/analysis/display_mae_mfe_group.png)

          overlay :
          ![波動分析圖組](img/analysis/display_mae_mfe_overlay.png)
        """
        return super().display_mae_mfe_analysis(violinmode, mfe_scatter_x, **kwargs)
