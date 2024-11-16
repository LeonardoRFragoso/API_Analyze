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
        sma_column_name = f'SMA_{sma_period}'
        data[sma_column_name] = data[target_column].rolling(window=sma_period, min_periods=1).mean()

    # Calcular EMA, se solicitado
    if ema_period:
        ema_column_name = f'EMA_{ema_period}'
        data[ema_column_name] = data[target_column].ewm(span=ema_period, adjust=False).mean()
    
    # Remover valores NaN (opcional: apenas onde os indicadores foram calculados)
    indicators_columns = []
    if sma_period:
        indicators_columns.append(f'SMA_{sma_period}')
    if ema_period:
        indicators_columns.append(f'EMA_{ema_period}')

    if indicators_columns:
        data = data.dropna(subset=indicators_columns)
    
    return data
