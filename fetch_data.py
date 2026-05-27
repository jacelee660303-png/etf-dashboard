import yfinance as yf
import json
from datetime import datetime
 
TICKERS = [
    ('QQQ',  'Nasdaq 100',      '#2563eb'),
    ('EWY',  'Korea (MSCI)',    '#16a34a'),
    ('GLD',  'Gold',            '#d97706'),
    ('IEF',  '7-10Y Treasury',  '#7c3aed'),
    ('TLT',  '20Y+ Treasury',   '#dc2626'),
    ('SOXX', 'Semiconductor',   '#0891b2'),
]
 
result = {
    'date': datetime.utcnow().strftime('%Y-%m-%d'),
    'etfs': []
}
 
for ticker, name, color in TICKERS:
    try:
        data = yf.download(ticker, period='1y', interval='1wk',
                           progress=False, auto_adjust=True)
 
        # yfinance 최신버전 대응: MultiIndex 컬럼 처리
        if hasattr(data.columns, 'levels'):
            close_col = ('Close', ticker)
            if close_col in data.columns:
                series = data[close_col]
            else:
                series = data['Close']
        else:
            series = data['Close']
 
        series = series.dropna()
        closes = [float(v) for v in series.values]
        dates  = [str(d.date()) for d in series.index]
 
        if len(closes) < 10:
            raise ValueError(f'Too few data: {len(closes)}')
 
        cur = closes[-1]
        n   = len(closes)
 
        def ret_at(wk):
            idx = max(0, n - 1 - round(wk))
            return round((cur - closes[idx]) / closes[idx] * 100, 2)
 
        tp = closes[-13:] if n >= 13 else closes
        td = dates[-13:]  if n >= 13 else dates
        base = tp[0]
        trend = [{'date': d, 'idx': round(c / base * 100, 2)}
                 for d, c in zip(td, tp)]
 
        result['etfs'].append({
            'ticker': ticker, 'name': name, 'color': color,
            'cur':    round(cur, 2),
            'prev6m': round(closes[max(0, n - 27)], 2),
            'ret3m':  ret_at(13),
            'ret6m':  ret_at(26),
            'ret9m':  ret_at(39),
            'ret12m': ret_at(min(51, n - 1)),
            'trend':  trend
        })
        print(f'✓ {ticker}  6M={ret_at(26):+.1f}%')
 
    except Exception as e:
        print(f'✗ {ticker}: {e}')
 
with open('data.json', 'w') as f:
    json.dump(result, f, indent=2)
 
print(f'\nSaved {len(result["etfs"])} ETFs → data.json')
