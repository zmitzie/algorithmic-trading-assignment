import numpy as np
import matplotlib.pyplot as plt

def read_ledger(ledger_file="ledger_crossing_averages_eval.txt"):
    '''
    Reads and reports useful information from ledger_file.

    Input:
        ledger (str): path to the ledger file to read

    Output: None
    '''
    data = np.loadtxt(ledger_file, delimiter=",", dtype='str')
    print("The total number of transactions performed are:", data.shape[0])
    #calculate total amount spent and earned:
    total_buy_value = 0
    total_sell_value = 0
    for i in range(data.shape[0]):
        if data[i,0] == 'buy':
            total_buy_value += float(data[i,-1])
        else:
            total_sell_value += float(data[i, -1])
    print("Overall profit from all stocks:", round(total_sell_value+total_buy_value,2))
    print("Total amount spent for all stocks:",round(abs(total_buy_value),2))
    print("total amount earned for all stocks:", round(total_sell_value,2))
    #get all the differences in an array and plot it
    indices = []
    stocks = 0
    #understand how many different stocks are in the portfolio from the initial buys
    for i in range(len(data)):
        if data[i,0] == 'buy' and data[i,1] == '0':
            stocks += 1
        else: #if there aren't any more, then stop the loop
            break
    print("The different number of stocks in the portfolio are: ", stocks)
    #From the way that we have implemented the indicators and the strategies, we know that at first we look one stock every time
    #so we will check the first one, then the second one.
    #loop over all the stocks
    portfolio_status = []
    for i in range(stocks):
        indices = np.where(data[:,2] == str(i))
        #calculate portfolio status before the last day for every stock at a time and display it at the end.
        before_last_day_stocks_held = 0
        for k in reversed(indices[0][0:-1]): #reverse array to get access to the indices from the end, to get the last buy orders
            # skip first loop (in the reversed array, this is when we sell in the last day)
            if data[k,0] == 'sell': #break if we see a sell order (not the sell order before the last day)
                #that means that we will stop the loop if we get to a sell order
                # (that means that we sold any remaining stocks at that day).
                break
            else: # add up all the buy orders
                before_last_day_stocks_held += (int(data[k,3]))
        portfolio_status.append(before_last_day_stocks_held)
        #loop over the indices and calculate value
        total_buys = 0
        total_sells = 0
        overall = [0.0] # initialize with 0 at day -1
        dates_of_transactions = [-1] # we set it to -1 to get the day before we buy the first stocks
        buys = 0
        # the way we calculate the amount of money we had over time is the following:
        # we assume that we get money when we sell the stock, so we add up all the buy orders we make until
        # the moment we sell, and that's when we record the money we have at that point. We also mark the dates
        # that we sell so we can display the dates on the graph
        for j in indices[0]:
            if data[j,0] == 'buy':
                buys += abs(float(data[j,-1]))
                total_buys += abs(float(data[j, -1]))
                overall.append(float(data[j, -1]))
            elif data[j,0] == 'sell':
                total_sells += float(data[j, -1])
                overall.append(float(data[j, -1]) - buys)
                #reset the counter so the next time we sell we know what amount we have bought in the meantime
                buys = 0
            dates_of_transactions.append(int(data[j,1]))
        print("Amount earned from trading the stock number ", i, " is ", round(total_sells,2), "by spending ", round(total_buys,2))
        print("Profit overall from trading the stock number ",i, " is shown in the graph below:")
        plt.plot(dates_of_transactions,overall)
        plt.show()
    for i in range(stocks):
        print(f'The portfolio before the last day for stock {i} had {portfolio_status[i]} stocks')