# 2023-11-29 定义常量
# 2024-01-18 使用os, 以兼容Win和Ubuntu

'''
Ubuntu 设置PYTHONPATH环境变量：
你也可以通过设置PYTHONPATH环境变量来修改Python的搜索路径。PYTHONPATH环境变量是一个包含若干路径的列表，Python会在这些路径中搜索模块。
打开你的~/.bashrc文件并在其中添加以下行：
export PYTHONPATH="${PYTHONPATH}:/path/to/your/module"

然后运行source ~/.bashrc以更新你的会话以引入新的变量。
注意/path/to/your/module应该被替换为放置constants.py的目录的绝对路径。
请注意，上述两种方法都需要把constants.py所在的目录添加到路径中，而不是constants.py文件本身。 (已编辑)

有没有其他方法可以让Python找到常量文件而不需要修改搜索路径？

可以直接在Python脚本中导入constants.py文件吗？

'''

import os
homedir = os.path.expanduser('~')
pythondir = os.path.join(homedir,'Trading')

LOG_DIR = os.path.join(pythondir, "Log")
DATA_DIR = os.path.join(pythondir, "Data")

# Log Files
DATA_LOG_FILE = os.path.join(LOG_DIR,"data.log")
TRADING_LOG_FILE = os.path.join(LOG_DIR,"trading.log")
MarketMonitor_LOG_FILE = os.path.join(LOG_DIR,"marketmonitor.log")
StockHistory_LOG_FILE = os.path.join(LOG_DIR,"StockHistory.log")

# File Names
JSL_DATA_FILE = os.path.join(DATA_DIR,"JSL")
CB_OF_TODAY_FILE = os.path.join(DATA_DIR,"CBofToday")
CB_OF_TODAY_CONV_BIAS = os.path.join(DATA_DIR,"CBofTodayConvBias")
#持有封基文件
CYFJ_FILE = os.path.join(DATA_DIR,"CYFJ.xlsx") 

STRATEGY_FILE = os.path.join(DATA_DIR,"StrategyBascket")
Position_FILE = os.path.join(DATA_DIR,"Position")

STRATEGY_CONV_BIAS = 'CONV_BIAS'            
STRATEGY_LOW_PREM = 'LOW_PREM'

#MarketMonitor
StockInventoryFile = os.path.join(DATA_DIR, "持仓净值.xlsx")
CBMonitorFile = os.path.join(DATA_DIR, "cbwatchlist.xlsx")
CONV_PREM_LEVEL = 0.01                                          #溢价率偏离大于3%告警
THS_HOT_CB_FILE = os.path.join(DATA_DIR,"THS_HOT_CB")
