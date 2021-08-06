# Functions to process transactions.
import numpy as np

def log_transaction(transaction_type, date, stock, number_of_shares, price, fees, ledger_file):
    '''
    Record a transaction in the file ledger_file. If the file doesn't exist, create it.
    
    Input:
        transaction_type (str): 'buy' or 'sell'
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we buy or sell (the column index in the data array)
        number_of_shares (int): the number of shares bought or sold
        price (float): the price of a share at the time of the transaction
        fees (float): transaction fees (fixed amount per transaction, independent of the number of shares)
        ledger_file (str): path to the ledger file
    
    Output: returns None.
        Writes one line in the ledger file to record a transaction with the input information.
        This should also include the total amount of money spent (negative) or earned (positive)
        in the transaction, including fees, at the end of the line.
        All amounts should be reported with 2 decimal digits.

    Example:
        Log a purchase of 10 shares for stock number 2, on day 5. Share price is 100, fees are 50.
        Writes the following line in 'ledger.txt':
        buy,5,2,10,100.00,-1050.00
            >>> log_transaction('buy', 5, 2, 10, 100, 50, 'ledger.txt')
    '''
    # Create file if it doesn't exists or open the file with append
    file = open(ledger_file, "a")
    new_price = float(price) * number_of_shares
    number_of_shares = int(number_of_shares)
    # Convert the amount to negative or positive if it is a sell or buy order accordingly
    if transaction_type == 'buy':
        new_price = -abs(new_price + fees)
    elif transaction_type == 'sell':
        new_price = abs(new_price - fees)
    # Use str.format() to report amount with 2 decimal digits
    # \n is used to go to the next line
    file.writelines('\n' + transaction_type + "," + str(date) + "," + str(stock) + "," + str(
        number_of_shares) + "," + "{:.2f}".format(price) + "," + "{:.2f}".format(new_price))
    file.close()

def buy(date, stock, available_capital, stock_prices, fees, portfolio, ledger_file):
    '''
    Buy shares of a given stock, with a certain amount of money available.
    Updates portfolio in-place, logs transaction in ledger.
    
    Input:
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we want to buy
        available_capital (float): the total (maximum) amount to spend,
            this must also cover fees
        stock_prices (ndarray): the stock price data
        fees (float): total transaction fees (fixed amount per transaction)
        portfolio (list): our current portfolio
        ledger_file (str): path to the ledger file
    
    Output: None

    Example:
        Spend at most 1000 to buy shares of stock 7 on day 21, with fees 30:
            >>> buy(21, 7, 1000, sim_data, 30, portfolio)
    '''
    # check if array is not 2d (and thus contains only one stock). Because 1d arrays require different handling
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    stock_price = []
    if stock_prices.ndim == 2:
        stock_price = stock_prices[date, stock]
    else:
        stock_price = stock_prices[date]
    #calculate the available amount after deducting fees
    capital_after_fees = available_capital - fees
    shares = capital_after_fees // stock_price
    #remaining_capital = capital_after_fees - shares * capital_after_fees
    # Add the number of stocks we can buy with the amount we are given to the portfolio
    portfolio[stock] += shares
    log_transaction("buy", date, stock, shares, stock_price, fees, ledger_file)

def sell(date, stock, stock_prices, fees, portfolio, ledger_file):
    '''
    Sell all shares of a given stock.
    Updates portfolio in-place, logs transaction in ledger.
    
    Input:
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we want to sell
        stock_prices (ndarray): the stock price data
        fees (float): transaction fees (fixed amount per transaction)
        portfolio (list): our current portfolio
        ledger_file (str): path to the ledger file
    
    Output: None

    Example:
        To sell all our shares of stock 1 on day 8, with fees 20:
            >>> sell(8, 1, sim_data, 20, portfolio)
    '''
    # check if array is not 2d (and thus contains only one stock). Because 1d arrays require different handling
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    stock_price = []
    if stock_prices.ndim == 2:
        stock_price = stock_prices[date, stock]
    else:
        stock_price = stock_prices[date]
    # Get the amount of shares we have for the specific stock
    shares = portfolio[stock]
    # Update portfolio (because we sell all stocks)
    portfolio[stock] = 0
    log_transaction("sell", date, stock, shares, stock_price, fees, ledger_file)

def create_portfolio(available_amounts, stock_prices, fees, ledger_file):
    '''
    Create a portfolio by buying a given number of shares of each stock.
    
    Input:
        available_amounts (list): how much money we allocate to the initial
            purchase for each stock (this should cover fees)
        stock_prices (ndarray): the stock price data
        fees (float): transaction fees (fixed amount per transaction)
    
    Output:
        portfolio (list): our initial portfolio

    Example:
        Spend 1000 for each stock (including 40 fees for each purchase):
        >>> N = sim_data.shape[1]
        >>> portfolio = create_portfolio([1000] * N, sim_data, 40)
    '''
    # check if array is not 2d (and thus contains only one stock). Because in 1d array .shape[1] would fail
    # https://stackoverflow.com/questions/21299798/check-if-numpy-array-is-multidimensional-or-not
    shape_of_1 = 1
    if stock_prices.ndim == 2:
        shape_of_1 = stock_prices.shape[1]
    N = shape_of_1
    # create an initial portfolio to pass it over to the buy() function
    portfolio = np.zeros(N)
    # loop over the number of stocks we want to buy.
    for i in range(N):
        buy(0, i, available_amounts[i], stock_prices, fees, portfolio, ledger_file)
    return portfolio

