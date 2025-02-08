import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data():
    # 获取所有A股股票代码列表
    stock_info = ak.stock_info_a_code_name()
    
    # 获取当前日期和一年前的日期
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    all_stock_data = {}
    
    # 遍历每个股票获取数据
    for index, row in stock_info.iterrows():
        try:
            stock_code = row['code']
            stock_name = row['name']
            
            # 获取日线数据
            df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date)
            
            # 只保留收盘价
            df = df[['日期', '收盘']]
            df.columns = ['date', 'close']
            
            # 计算移动平均线
            df['ma50'] = df['close'].rolling(window=50).mean()
            df['ma150'] = df['close'].rolling(window=150).mean()
            
            # 计算斜率
            df['ma50_slope'] = df['ma50'].diff()
            df['ma150_slope'] = df['ma150'].diff()
            
            all_stock_data[stock_code] = {
                'name': stock_name,
                'data': df
            }
            
        except Exception as e:
            print(f"获取股票 {stock_code} 数据时出错: {str(e)}")
            continue
            
    return all_stock_data

def analyze_signals(all_stock_data):
    buy_signals = []
    sell_signals = []
    
    for stock_code, stock_info in all_stock_data.items():
        df = stock_info['data']
        name = stock_info['name']
        
        # 确保有足够的数据进行分析
        if len(df) < 150:
            continue
            
        # 获取最新的数据点
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 检查买入信号
        if (prev['ma50'] <= prev['ma150'] and latest['ma50'] > latest['ma150'] and  # 上穿
            latest['ma50_slope'] > 0 and latest['ma150_slope'] > 0 and  # 斜率向上
            latest['close'] > latest['ma50'] and latest['close'] > latest['ma150']):  # 价格在均线上方
            buy_signals.append((stock_code, name))
            
        # 检查卖出信号
        if (prev['ma50'] >= prev['ma150'] and latest['ma50'] < latest['ma150'] and  # 下穿
            latest['ma50_slope'] < 0 and latest['ma150_slope'] < 0 and  # 斜率向下
            latest['close'] < latest['ma50'] and latest['close'] < latest['ma150']):  # 价格在均线下方
            sell_signals.append((stock_code, name))
            
    return buy_signals, sell_signals

def main():
    print("开始获取股票数据...")
    all_stock_data = get_stock_data()
    
    print("开始分析信号...")
    buy_signals, sell_signals = analyze_signals(all_stock_data)
    
    print("\n买入信号:")
    for code, name in buy_signals:
        print(f"股票代码: {code}, 公司名称: {name}")
        
    print("\n卖出信号:")
    for code, name in sell_signals:
        print(f"股票代码: {code}, 公司名称: {name}")

if __name__ == "__main__":
    main()