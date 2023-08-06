import pandas as pd


def ConvertTimeZone(df):
    df = pd.to_datetime(df, errors='coerce')
    return df.apply(lambda x: pd.Timestamp(x, tz='Asia/Jakarta').tz_convert(tz='UTC').isoformat())