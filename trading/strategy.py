# Functions to implement our trading strategy.
import numpy as np
import trading.process as proc
import trading.data as data
import trading.indicators as stock_indicators
import matplotlib.pyplot as plt

def random(stock_prices, period=7, amount=5000, fees=20, ledger='ledger_random.txt'):
    '''
    Randomly decide, every period, which stocks to purchase,
    do nothing, or sell (with equal probability).
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        period (int, default 7): how often we buy/sell (days)
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        fees (float, default 20): transaction feesx
        ledger (str): path to the ledger file

    Output: None
    '''
    # check if array is not 2d (and thus contains only one stock). Because in 1d array .shape[1] would fail
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    shape_of_1 = 1
    if stock_prices.ndim == 2:
        shape_of_1 = stock_prices.shape[1]
    # create portfolio
    portfolio =  proc.create_portfolio([amount] * shape_of_1, stock_prices, fees, ledger)
    # initialize generator
    rng = np.random.default_rng()
    # The period provided is the step in the for loop
    for i in range(1, len(stock_prices), period):
        for j in range(shape_of_1):
            # generate a decision with equal probabilities for every outcome
            choice = rng.choice(['buy', 'sell', 'nothing'])
            if choice == 'buy':
                proc.buy(i, j, amount, stock_prices, fees, portfolio, ledger)
            elif choice == 'sell':
                proc.sell(i, j, stock_prices, fees, portfolio, ledger)
            #if the choice = 'nothing', then we don't have to specify an elif statement
    #after all the periods, we sell
    for j in range(shape_of_1):
        if portfolio[j] != 0:
            # -1 because arrays starts from zero
            proc.sell(len(stock_prices)-1, j, stock_prices, fees, portfolio, ledger)

def crossing_averages(stock_prices, sma_period=200, fma_period=50, weights=[] ,amount=5000, fees=20, ledger='ledger_crossing_averages.txt'):
    '''
        Finds the crossing points between the SMA with period sma_period,
        and the FMA with period fma_period to make buying or selling decisions.
        Uses the movingaverage() function as an indicator to calculate SMA and FMA
        Spends a maximum of amount on every purchase.

        Input:
            stock_prices (ndarray): the stock price data
            sma_period (int, default 200): the SMA period (days)
            fma_period (int, default 50): the FMA period (days)
            weights (list, default []): must be of length n if specified. Indicates the weights
                to use for the weighted average. If empty, return a non-weighted average.
            amount (float, default 5000): how much we spend on each purchase
                (must cover fees)
            fees (float, default 20): transaction fees
            ledger (str): path to the ledger file

        Output: None
    '''
    # check if array is not 2d (and thus contains only one stock). Because in 1d array .shape[1] would fail
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    shape_of_1 = 1
    if stock_prices.ndim == 2:
        shape_of_1 = stock_prices.shape[1]
    #create portfolio
    portfolio = proc.create_portfolio([amount] * shape_of_1, stock_prices, fees, ledger)
    diff = fma_period - sma_period
    #for every stock price in the portfolio
    for j in range(shape_of_1):
        #calc sma & fma
        # if shape_of_1 = 1 that means that we need to call sma and fma_full in a way that stock_prices is a 1d array
        sma = []
        fma_full = []
        if shape_of_1 == 1:
            sma = stock_indicators.moving_average(stock_prices[:], sma_period, weights)
            fma_full = stock_indicators.moving_average(stock_prices[:], fma_period, weights)
        else:
            sma = stock_indicators.moving_average(stock_prices[:,j], sma_period, weights)
            fma_full = stock_indicators.moving_average(stock_prices[:,j], fma_period, weights)
        # shrink the fma to have the same length as the sma
        fma = fma_full[:len(sma)]
        # uncomment to plot the sma and the fma to understand the moving averages
        #plt.plot(sma)
        #plt.plot(fma)
        #plt.show()
        # set a previous indicator param boolean = true. We use a boolean value
        # so that we won't buy the same stock again in the next day
        crossing_indicator = True
        for i in range(len(fma)): # loop until the fma data comes to an end
            # check if fma[i] > sma[i] (fma crosses from below) and indicator = False
            if (fma[i] > sma[i]) and crossing_indicator == False:
                # buy stocks & set the indicator to true so the next time it will sell if it crosses from above
                proc.buy(i, j, amount, stock_prices, fees, portfolio, ledger)
                crossing_indicator = True
            # check if fma[i] < sma[i] (fma crosses from above) and indicator = True
            elif (fma[i] < sma[i]) and crossing_indicator == True:
                #sell & set to false
                proc.sell(i, j, stock_prices, fees, portfolio, ledger)
                crossing_indicator = False
    # sell everything at the end
    for j in range(shape_of_1):
        if portfolio[j] != 0:
            # sell at the last recorded stock date.
            # -1 because arrays starts from zero.
            proc.sell(stock_prices.shape[0]-1, j, stock_prices, fees, portfolio, ledger)

def momentum(stock_prices, osc_type='stochastic', period = 7,low_threshold=0.25, high_threshold=0.75, cool_down_period=14, amount=5000, fees=20, ledger='ledger_momentum.txt'):
    '''
        Makes buying or selling decisions using an oscilator (stochastic or RSI)
        with period n depending on a low and a high threshold. Uses a cool down period
        before mmaking another transaction
        Spends a maximum of amount on every purchase.

        Input:
            stock_prices (ndarray): the stock price data
            osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
            period (int, default 7): period of the moving average (in days).
            low_threshold (float, default 0.25):  The low threshold used for the oscilator
            high_threshold (float, default 0.75): The high threshold used for the oscilator
            cool_down_period (int, default 14): The cooldown period before making a new buy or sell order
            amount (float, default 5000): how much we spend on each purchase
                (must cover fees)
            fees (float, default 20): transaction fees
            ledger (str): path to the ledger file

        Output: None
    '''
    # check if array is not 2d (and thus contains only one stock). Because in 1d array .shape[1] would fail
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    shape_of_1 = 1
    if stock_prices.ndim == 2:
        shape_of_1 = stock_prices.shape[1]
    portfolio = proc.create_portfolio([amount] * shape_of_1, stock_prices, fees, ledger)
    for j in range(shape_of_1): #for every company
        # calculate the oscilator
        # if shape_of_1 = 1 that means that we need to call sma and fma_full in a way that stock_prices is a 1d array
        oscilator = []
        if shape_of_1 == 1:
            oscilator = stock_indicators.oscillator(stock_prices[:], n=period, osc_type=osc_type)
        else:
            oscilator = stock_indicators.oscillator(stock_prices[:,j], n=period, osc_type=osc_type)
        # the index to revisit and buy or sell, after the cool down period has passed
        revisit_buy = 0
        revisit_sell = 0
        # -period because the oscilator length is the total days - period
        loop_times = stock_prices.shape[0]-period
        for i in range(loop_times):
            if low_threshold >= oscilator[i] and i > revisit_buy:
                # buy the stock for the current date + period (because we deducted in in the loop times
                proc.buy(i + period, j, amount, stock_prices, fees, portfolio, ledger)
                # set the index of when to buy again, after the cool down period
                revisit_buy = i + cool_down_period
            if high_threshold <= oscilator[i] and i > revisit_sell:
                # sell & revisit
                proc.sell(i+ period, j, stock_prices, fees, portfolio, ledger)
                revisit_sell = i + cool_down_period
    # sell everything at the end
    for j in range(shape_of_1):
        if portfolio[j] != 0:
            # sell at the last recorded stock date.
            # -1 because arrays starts from zero.
            proc.sell(stock_prices.shape[0]-1, j, stock_prices, fees, portfolio, ledger)