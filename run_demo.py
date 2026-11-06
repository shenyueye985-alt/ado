"""Learning reproduction of the PyPortfolioOpt README example, not a backtest."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'work' / 'portfolio-packages'))
import json
import importlib.metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

prices = pd.read_csv(ROOT / 'stock_prices.csv', index_col='date', parse_dates=True)
mu = expected_returns.mean_historical_return(prices, frequency=252)
cov = risk_models.sample_cov(prices, frequency=252)
ef = EfficientFrontier(mu, cov)
ef.max_sharpe(risk_free_rate=0.0)
weights = ef.clean_weights()
performance = ef.portfolio_performance(risk_free_rate=0.0)
assert abs(sum(ef.weights) - 1) < 1e-6
assert min(ef.weights) >= -1e-6
assert np.isfinite(performance).all()
allocation, remaining = DiscreteAllocation(weights, get_latest_prices(prices), total_portfolio_value=10000).greedy_portfolio()
pd.Series(weights, name='weight').rename_axis('ticker').to_csv(ROOT / 'weights.csv')
result = {'source': 'https://github.com/PyPortfolio/PyPortfolioOpt',
 'library_version': importlib.metadata.version('pyportfolioopt'),
 'data_start':str(prices.index.min().date()), 'data_end':str(prices.index.max().date()),
 'rows':len(prices), 'assets':len(prices.columns),
 'risk_free_rate':0.0, 'annualization':252,
 'expected_annual_return':performance[0], 'annual_volatility':performance[1], 'sharpe_ratio':performance[2],
 'weights':weights, 'illustrative_budget':10000, 'shares':allocation, 'unallocated_cash':remaining,
 'note':'In-sample model estimates from historical example data; not realized future returns or a backtest. No trading fees. Missing histories retained as in upstream example.'}
(ROOT / 'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
positive = pd.Series(weights).loc[lambda s:s>0].sort_values()
fig, ax = plt.subplots(figsize=(9,5))
ax.barh(positive.index, positive.values*100, color='#167d9a')
ax.set_xlabel('Portfolio weight (%)')
ax.set_title('PyPortfolioOpt official example: maximum Sharpe allocation')
ax.spines[['top','right']].set_visible(False)
for i,v in enumerate(positive.values): ax.text(v*100+0.3,i,f'{v:.1%}',va='center')
ax.set_xlim(0,positive.max()*100+7)
fig.text(.08,.015,'Historical sample / in-sample estimates / risk-free rate = 0%',fontsize=9,color='#555555')
fig.tight_layout(rect=(0,.04,1,1))
fig.savefig(ROOT / 'allocation.png',dpi=160)
print(json.dumps(result,indent=2))
