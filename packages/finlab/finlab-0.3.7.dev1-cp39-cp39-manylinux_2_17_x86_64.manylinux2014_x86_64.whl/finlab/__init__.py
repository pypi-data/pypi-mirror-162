import os
import time
import logging
import threading

# Get an instance of a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__version__ = '0.3.7.dev1'


class LoginPanel():

    def __init__(self):
        pass

    def gui_supported(self):
        try:
            from IPython.display import IFrame, display, clear_output
            return True
        except:
            return False

    def display_gui(self):

        from IPython.display import IFrame, display, HTML, clear_output
        iframe = IFrame(
            f'https://ai.finlab.tw/api_token/?version={__version__}', width=620, height=300)
        display(iframe)

        token = input('請從 https://ai.finlab.tw/api_token 複製驗證碼: \n')

        clear_output()
        self.login(token)

    def display_text_input(self):
        token = input('請從 https://ai.finlab.tw/api_token 複製驗證碼:\n')
        self.login(token)

    @staticmethod
    def login(token):
        # set token
        token = token[:token.index('#')]
        os.environ['finlab_id_token'] = token
        print('輸入成功!')


def login(api_token=None):
    """登錄量化平台。

    可以至 [api_token查詢頁面](https://ai.finlab.tw/api_token/) 獲取api_token，傳入函數後執行登錄動作。
    之後使用Finlab模組的會員功能時，系統就不會自動跳出請求輸入api_token的[GUI頁面](https://ai.finlab.tw/api_token/)。
    若傳入的api_toke格式有誤，系統會要求再次輸入。

    Args:
        api_token (str): FinLab api_token
    """
    if api_token is None:
        lp = LoginPanel()
        if lp.gui_supported():
            lp.display_gui()
        else:
            lp.display_text_input()
    else:
        LoginPanel.login(api_token)


def get_token():
    """取得登錄會員的finlab_id。

    若未登錄過，會跳出登錄頁面請求登錄。

    Returns:
        (str): finlab_id_token
    """
    if 'finlab_id_token' not in os.environ:
        login()

    return os.environ['finlab_id_token']
