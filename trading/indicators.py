import numpy as np

def moving_average(stock_price, n=7, weights=[]):
    '''
    Calculates the n-day (possibly weighted) moving average for a given stock over time.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.

    Output:
        ma (ndarray): the n-day (possibly weighted) moving average of the share price over time.
    '''
    # If we are given am array of weights, multiply it with the stock price
    if len(weights):
        stock_price = np.multiply(stock_price, weights)
    # Used cumsum implementation from
    # https://stackoverflow.com/questions/14313510/how-to-calculate-moving-average-using-numpy/54628145
    ret = np.cumsum(stock_price, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def oscillator(stock_price, n=7, osc_type='stochastic'):
    '''
    Calculates the level of the stochastic or RSI oscillator with a period of n days.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.

    Output:
        osc (ndarray): the oscillator level with period $n$ for the stock over time.
    '''
    if osc_type == 'stochastic':
        loop_times = len(stock_price) - n
        stochastic = np.zeros(loop_times)
        for i in range(loop_times):
            # from -7 days to the current day we examine in the array.
            # calculate the max and min of the stock price from i (current date we examine) to i+n (i+ 7 days)
            maximum = max(stock_price[i:i + n])
            minimum = min(stock_price[i:i + n])
            delta = stock_price[i + n - 1] - minimum
            delta_max = maximum - minimum
            # Add the final value to the stochastic array
            stochastic[i] = (delta / delta_max)
        return stochastic
    else:
        loop_times = len(stock_price) - n
        rsi = np.zeros(loop_times)
        for i in range(loop_times):
            # get differences for consecutive days
            diffs = np.diff(stock_price[i:n + i])
            # split differences to positives and negatives
            positives = [n for n in diffs if n > 0]
            negatives = [n for n in diffs if n < 0]
            # calculate averages from the positives and negatives
            #If either the positives or the negatives array is empty,
            # this yields an error when calculating tha averages, so set to nan.
            if not len(positives):
                positives = np.nan
            if not len(negatives):
                negatives = np.nan
            avgs_positive = np.average(positives)
            avgs_negatives = abs(np.average(negatives))
            rs = float(avgs_positive) / float(avgs_negatives)
            # after additional information from correction.md:
            if np.isnan(rs):
                rs = 0
            # Add the final calculation to the rsi array
            rsi[i] = (1 - 1 / (1 + rs))
        return rsi