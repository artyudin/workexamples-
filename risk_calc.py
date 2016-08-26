import numpy as np
import pandas as pd
from pandas_datareader import data
from datetime import date
from portfolio.models import Portfolio, Asset
from analysis.analysis_models import Risk


class RiskAnalysis:

    def __init__(self):
        self.start_date = None
        self.end_date = None
        self.period = None
        self.symbol = ''
        self.stock_returns = None
        self.sp_returns = None
        self.RAW_STOCK_RETURNS = None
        self.RAW_SP_RETURNS = None
        self.beta = None
        self.alpha = None
        self.get_data_raw_sp()

    def run_analysis(self, symbol):
        self.start_date = date(2014,12,31)
        self.end_date = date(2015,12,31)
        self.period = 12
        self.symbol = symbol
        self.calculate_returns()
        # self.stock_returns = self.calculate_stock_returns(symbol)
        # self.sp_returns = self.calculate_sp_returns()
        # return {'sp':self.sp_returns,'stock':self.stock_returns}
        self.beta = self.calculate_beta()
        self.alpha = self.calculate_alpha()
        return self.risk_report()

    def get_data_raw_stock(self):
        self.RAW_STOCK_RETURNS = data.DataReader(self.symbol, 'yahoo', self.start_date, self.end_date)

    def get_data_raw_sp(self):
        self.RAW_SP_RETURNS = data.DataReader('^GSPC', 'yahoo', self.start_date, self.end_date)

    def calculate_returns(self):
        self.get_data_raw_stock()
        new_index = self.RAW_SP_RETURNS.index.intersection(self.RAW_STOCK_RETURNS.index)
        self.stock_returns = pd.DataFrame(data={'stock_adj_close':self.RAW_STOCK_RETURNS['Adj Close']},index=new_index)
        self.sp_returns = pd.DataFrame(data={'sp_adj_close':self.RAW_SP_RETURNS['Adj Close']}, index=new_index)
        self.calculate_stock_returns()
        self.calculate_sp_returns()

    def calculate_stock_returns(self):
        self.stock_returns[['stock_returns']] = self.stock_returns[['stock_adj_close']]/self.stock_returns[['stock_adj_close']].shift(1)-1 
        self.stock_returns = self.stock_returns.dropna()
    
    def calculate_sp_returns(self):
        self.sp_returns[['sp_returns']] = self.sp_returns[['sp_adj_close']]/self.sp_returns[['sp_adj_close']].shift(1)-1 
        self.sp_returns = self.sp_returns.dropna()


    def compute_covariance(self):
        covariance = np.cov(self.stock_returns['stock_returns'], self.sp_returns['sp_returns'])
        # print(covariance)
        return covariance

    def calculate_beta(self):
        covariance = self.compute_covariance()
        # print('covariance:',covariance)
        beta = covariance[0,1]/covariance[1,1]
        # print('beta:', beta)
        return beta

    def calculate_alpha(self):
        alpha = np.mean(self.stock_returns['stock_returns']) - self.beta * np.mean(self.sp_returns['sp_returns'])
        return alpha
        
    def annualized_alpha(self):
        annualized_alpha = self.alpha*self.period
        return annualized_alpha

    def calculate_r_squared(self):
        covariance = self.compute_covariance()
        ypred = self.alpha + self.beta * self.sp_returns['sp_returns']
        ss_res = np.sum(np.power(ypred-self.stock_returns['stock_returns'],2))
        ss_tot = covariance[0,0]*(len(self.stock_returns)-1)
        r_squared = 1.-ss_res/ss_tot
        return r_squared

    def calculate_volatility(self):
        covariance = self.compute_covariance()
        volatility = np.sqrt(covariance[0,0])
        volatility = volatility*np.sqrt(self.period)
        return volatility

    def calculate_moment(self):
        momentum = np.prod(1+self.stock_returns['stock_returns'].tail(12).values)-1
        return momentum

    def risk_report(self):
        beta = self.beta
        annualized_alpha = self.annualized_alpha()
        r_squared = self.calculate_r_squared()
        volatility = self.calculate_volatility()
        risk_report = {'beta':round(beta,2), 
                        'alpha': round(annualized_alpha * 100,2), 
                        'r_squared':round(r_squared,2),
                        'volatility':volatility}
        return risk_report

class Analysis_portfolio():

    def anlaysis_portfolio(self,id):
        portfolio_object = Portfolio.objects.get(id=id)
        # bond = ContentType.objects.get_for_model(Bond)
        assets= Asset.objects.raw('''SELECT *, cost_basis * quantity as value 
            FROM portfolio_asset
            WHERE portfolio_asset.portfolio_id = %s ''',(id,))
        # print(assets)
        portfolio_value = 0 
        for asset in assets:
            portfolio_value += asset.value
        
        assets = [ asset.to_json(asset.value,portfolio_value) for asset in assets ]

        # assets = portfolio_object.asset_set.exclude(content_type=bond)

        # print(assets)
        risk = RiskAnalysis()
        # print(risk)
        stock_value = 0 
        bond_value = 0 
        etf_value  = 0 
        context = {}
        alpha = 0
        beta = 0
        r_squared = 0 
        for asset in assets:
            if asset["content_type"] != "bond":
                symbol = asset["content_object"]["symbol"]
                # print(asset["content_type"])
                stock = risk.run_analysis(symbol)
                # print(stock)
                print('*'*100)
                print(symbol,stock)
                print('*'*100)
                if asset["content_type"] == "stock":
                    stock_value += asset['value']
                else:
                    etf_value += asset['value']
            else:
                bond_value +=  asset['value']
                stock  = {'beta':0, 
                        'alpha':0, 
                        'r_squared':0,
                        'volatility':0}
            # context[symbol] = stock
            asset['analysis']=stock
            asset['analysis_total'] = {'beta':round(stock["beta"] * asset['weight'] /100,2), 
                                      'alpha':round(stock["alpha"] * asset['weight'] /100,2), 
                                      'r_squared':round(stock["r_squared"] * asset['weight'] / 100,2)
                                        }
            alpha += stock["alpha"] * asset['weight'] /100
            beta += stock["beta"] * asset['weight'] /100
            r_squared += stock["r_squared"] * asset['weight'] / 100 
            asset['weight'] =  round (asset['weight'],2)


        totals = {'portfolio_value' :portfolio_value,
                    'alpha': round(alpha,2), 
                    'beta' : round(beta,2),
                    'r_squared' : round(r_squared,2),
                    'stock_value':  int(stock_value / portfolio_value * 100 ),
                    'etf_value':  int(etf_value  / portfolio_value * 100) ,
                    'bond_value':  int(bond_value  / portfolio_value * 100 )
                    }



        # return JsonResponse({'response':assets,'total':totals,'portfolio':portfolio_object.to_json()})
        return dict(response = assets ,total = totals ,portfolio = portfolio_object.to_json())



class ModelPortfolio:


    def recommended_portfolio(self,request,user):

        risk = Risk.objects.get(user=user)
        score = risk.score
        if score in [16, 17, 18, 19, 20]:
            return_portfolio = 9
            # return "agressive"

        elif score in [11, 12, 13, 14, 15]:
            return_portfolio = 10
            # return "moderatly_aggressive"

        elif score in [6, 7, 8, 9, 10]:
            return_portfolio = 11
            # return "moderate"

        else:
            return_portfolio = 12
            # return "conservative"
        return return_portfolio
























