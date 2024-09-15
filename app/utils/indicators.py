def add_indicators(data, sma_period=None, ema_period=None):
    if sma_period:
        data['SMA'] = data['Close'].rolling(window=sma_period).mean()
    if ema_period:
        data['EMA'] = data['Close'].ewm(span=ema_period, adjust=False).mean()
    return data
