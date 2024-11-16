import pandas as pd

def add_indicators(data, sma_period=None, ema_period=None, target_column='Close'):
    """
    Adiciona indicadores técnicos (SMA e EMA) a um DataFrame.

    Args:
        data (pd.DataFrame): DataFrame contendo os dados históricos.
        sma_period (int, optional): Período para a Média Móvel Simples (SMA). Default: None.
        ema_period (int, optional): Período para a Média Móvel Exponencial (EMA). Default: None.
        target_column (str, optional): Coluna alvo para o cálculo dos indicadores. Default: 'Close'.

    Returns:
        pd.DataFrame: DataFrame com os indicadores adicionados.
    """
    # Validação: verificar se o DataFrame é válido
    if data is None or not isinstance(data, pd.DataFrame):
        raise ValueError("O parâmetro 'data' deve ser um DataFrame válido.")
    
    # Validação: verificar se a coluna alvo existe no DataFrame
    if target_column not in data.columns:
        raise ValueError(f"A coluna '{target_column}' não está presente no DataFrame.")
    
    # Calcular SMA, se solicitado
    if sma_period:
        data[f'SMA_{sma_period}'] = data[target_column].rolling(window=sma_period).mean()
    
    # Calcular EMA, se solicitado
    if ema_period:
        data[f'EMA_{ema_period}'] = data[target_column].ewm(span=ema_period, adjust=False).mean()
    
    # Tratar valores NaN gerados pelos indicadores
    data = data.dropna(subset=[f'SMA_{sma_period}' for sma_period in [sma_period] if sma_period] +
                                [f'EMA_{ema_period}' for ema_period in [ema_period] if ema_period])
    
    return data
