### The main reason of selling option trades is due to theta decay. 
# A reasonable target is to have a theta decay of 0.1% of the account value per day.
# Since there are 250 trading days in a year, the annual theta decay is 25% of the account value.
# This file is used to analyze the theta decay of the options in an account.
from datetime import datetime, timedelta

from configs.utils import theta_scatter_plot

class ThetaAnalyzer:
    def __init__(self, client, options: list, ticker_to_stock_map: dict) -> None:
        self.options = options
        self.ticker_to_stock_map = ticker_to_stock_map
        # The sum of the theta of all the puts and calls in the account;
        self.total_theta = 0
        # The sum of the strike prices of all the puts and calls in the account;
        self.total_principal = 0
        # The theta decay rate of the account;
        self.total_theta_decay_percentage = 0
        for option in self.options:
            stock = self.ticker_to_stock_map.get(option.ticker)
            if stock is None:
                continue
            option_chains = stock.get_option_chains(client)
            delta = option_chains.get_delta_from_option_symbol(option.option_symbol)
            option.set_delta(delta)
            theta = option_chains.get_theta_from_option_symbol(option.option_symbol)
            option.set_theta(theta)
            if option.theta:
                option.theta_decay_percentage = - option.theta * 100 / option.strike_price
        return None
    
    def analyze(self):
        for option in self.options:
            if option.theta is None:
                print(f"Option {option.option_symbol} has no theta value.")
                continue
            self.total_theta += option.theta * option.short_quantity * 100
            self.total_principal += option.strike_price * option.short_quantity * 100
        self.total_theta_decay_percentage = - self.total_theta * 100 / self.total_principal
        print(f"Total principal: {self.total_principal}, Total theta: {self.total_theta}, Theta decay percentage: {self.total_theta_decay_percentage}")
        predicted_return_per_year = self.total_theta_decay_percentage * 250 * self.total_principal / 100
        print(f"With this setting, even if the stock price does not change, the account value will increase ${predicted_return_per_year} in a year.")

        # Find the top 5 options with the highest theta decay percentage,
        # and the top 5 options with the lowest theta decay percentage;
        theta_decay_percentage_list = [(option.option_symbol, option.theta_decay_percentage) for option in self.options if option.theta is not None]
        theta_decay_percentage_list.sort(key=lambda x: x[1], reverse=True)
        print("Top 5 options with the highest theta decay percentage:")
        for i in range(5):
            print(theta_decay_percentage_list[i])
        print("Top 5 options with the lowest theta decay percentage:")
        for i in range(1, 6):
            print(theta_decay_percentage_list[-i])
        # print("Any option with theta decay percentage < 0.05%:")
        # for tuple in theta_decay_percentage_list:
        #     if tuple[1] < 0.05:
        #         print(tuple)
        return self.total_theta_decay_percentage

    def scatter_plot(self):
        import matplotlib.pyplot as plt
        """
        Scatter plot all the options in the account, with x_axis delta and y_axis theta/strike_price.
        """
        # x_axis is delta, y_axis is theta/strike_price; plot the scatter plot;
        deltas = [option.delta for option in self.options if option.theta is not None ]
        theta_decay_percentages = [option.theta_decay_percentage for option in self.options if option.theta is not None]
        strike_prices = [option.strike_price for option in self.options if option.theta is not None]
        expiration_dates = [option.expiration_date for option in self.options if option.theta is not None]
        tickers = [option.ticker for option in self.options if option.theta is not None]


        # plot 1x2 subplots;
        fig, ax = plt.subplots(2, 1, figsize=(10, 10))
        subtitle = f"Scatte Plot for All Positions"
        ax[0] = theta_scatter_plot(ax=ax[0], 
                                   deltas=deltas, 
                                   theta_decay_percentages=theta_decay_percentages, 
                                   strike_prices=strike_prices, 
                                   expiration_dates=expiration_dates, 
                                   tickers=tickers,
                                   subtitle=subtitle)
        
        till_60_days = datetime.now().date() + timedelta(days=60)
        deltas = [option.delta for option in self.options if option.theta is not None and option.expiration_date <= till_60_days]
        theta_decay_percentages = [option.theta_decay_percentage for option in self.options if option.theta is not None and option.expiration_date <= till_60_days]
        strike_prices = [option.strike_price for option in self.options if option.theta is not None and option.expiration_date <= till_60_days]
        expiration_dates = [option.expiration_date for option in self.options if option.theta is not None and option.expiration_date <= till_60_days]
        tickers = [option.ticker for option in self.options if option.theta is not None and option.expiration_date <= till_60_days]
        subtitle = f"Scatter Plot for Positions Before {till_60_days}"
        ax[1] = theta_scatter_plot(ax=ax[1], 
                                   deltas=deltas, 
                                   theta_decay_percentages=theta_decay_percentages, 
                                   strike_prices=strike_prices, 
                                   expiration_dates=expiration_dates, 
                                   tickers=tickers,
                                   subtitle=subtitle)

        fig.suptitle(f"Total Theta Decay Percentage: {round(self.total_theta_decay_percentage, 2)}")
        plt.show()
        return None