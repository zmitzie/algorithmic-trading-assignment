import numpy as np  # import numpy as np, because np was used directly.
import matplotlib.pyplot as plt
def generate_stock_price(days, initial_price, volatility):
    '''
    Generates daily closing share prices for a company,
    for a given number of days.
    '''
    # Set stock_prices to be a zero array with length days
    stock_prices = np.zeros(days)
    # Set stock_prices in row 0 to be initial_price
    stock_prices[0] = initial_price
    # Set total_drift to be a zero array with length days
    totalDrift = np.zeros(days + 14) # This might go out of bounds at some point
    # For example, if on the last day we have a new news event with a duration
    # that exceeds the total number of days, when we add the drift to the totaldrift array, it will go out of bounds
    # since we try to add the drift on the days+1 element of the total drift array. By adding +14 in the number of days
    # when we initialize the totalDrift array, we are sure that in case that happens,
    # it won't cause an out of bounds error.
    # Set up the default_rng from Numpy
    rng = np.random.default_rng()
    # Loop over a range(1, days)
    for day in range(1, days):
        # Get the random normal increment
        inc = rng.normal()
        # Add stock_prices[day-1] to inc to get NewPriceToday
        NewPriceToday = stock_prices[day - 1] + inc # fix typo, not stock_price
        # Make a function for the news
        def news(chance, volatility):
            '''
            Simulate the news with %chance
            '''
            # Choose whether there's news today
            news_today = rng.choice([0, 1], p=[1 - chance,chance])
            # from numpy docs, p is a 1-d array with the probabilities of each outcome occuring,
            # so for 0 or false it is 1-0.01 and for 1 or true it is 0.01
            # https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html
            if news_today:
                # Calculate m and drift
                m = rng.normal(0,2)# instead of 0.3, m should be 2,
                # because of the standard deviation which we know is 2**2.
                drift = m * volatility
                # Randomly choose the duration
                duration = rng.integers(3, 14)  # should be between 3 days and 2 weeks from project descr., so 3,14.
                final = np.zeros(duration)
                for i in range(duration):
                    final[i] = drift
                return final
            else:
                return []  # wrong - return just an empty array instead. Quicker and less complex.
                # Also, duration is out of scope and we get an error.
        # Get the drift from the news
        d = news(0.01, volatility)  # the chance should be 0.01 (1%) instead of 1
        # Get the duration
        duration = len(d)
        # Add the drift to the next days
        totalDrift[day:day + duration] = d  # might go out of bounds, that is why we set it +14 days when we define it
        # Add today's drift to today's price
        NewPriceToday += totalDrift[day]
        # Set stock_prices[day] to NewPriceToday or to NaN if it's negative
        if NewPriceToday <= 0:
            stock_prices[day] = np.nan
        else:
            stock_prices[day] = NewPriceToday
    return stock_prices

def get_data(method='read', initial_price=None, volatility=None):
    '''
        Generates or reads simulation data for one or more stocks over 5 years,
        given their initial share price and volatility.

        Input:
            method (str): either 'generate' or 'read' (default 'read').
                If method is 'generate', use generate_stock_price() to generate
                    the data from scratch.
                If method is 'read', use Numpy's loadtxt() to read the data
                    from the file stock_data_5y.txt.

            initial_price (list): list of initial prices for each stock (default None)
                If method is 'generate', use these initial prices to generate the data.
                If method is 'read', choose the column in stock_data_5y.txt with the closest
                    starting price to each value in the list, and display an appropriate message.

            volatility (list): list of volatilities for each stock (default None).
                If method is 'generate', use these volatilities to generate the data.
                If method is 'read', choose the column in stock_data_5y.txt with the closest
                    volatility to each value in the list, and display an appropriate message.

            If no arguments are specified, read price data from the whole file.

        Output:
            sim_data (ndarray): NumPy array with N columns, containing the price data
                for the required N stocks each day over 5 years.

        Examples:
            Returns an array with 2 columns:
                >>> get_data(method='generate', initial_price=[150, 250], volatility=[1.8, 3.2])

            Displays a message and returns None:
                >>> get_data(method='generate', initial_price=[150, 200])
                Please specify the volatility for each stock.

            Displays a message and returns None:
                >>> get_data(method='generate', volatility=[3])
                Please specify the initial price for each stock.

            Returns an array with 2 columns and displays a message:
                >>> get_data(method='read', initial_price=[210, 58])
                Found data with initial prices [210, 100] and volatilities [1.2, 3.4].

            Returns an array with 1 column and displays a message:
                >>> get_data(volatility=[5.1])
                Found data with initial prices [380] and volatilities [5.2].

            If method is 'read' and both initial_price and volatility are specified,
            volatility will be ignored (a message is displayed to indicate this):
                >>> get_data(initial_price=[210, 58], volatility=[5, 7])
                Found data with initial prices [210, 100] and volatilities [1.2, 3.4].
                Input argument volatility ignored.

            No arguments specified, all default values, returns price data for all stocks in the file:
                >>> get_data()
    '''
    if method == 'generate':
        # if we don't have the same number of elements in the lists
        if len(initial_price) != len(volatility):
            if len(initial_price) == 0:
                print("Please specify the initial price for each stock.")
                return
            if len(volatility) == 0:
                print("Please specify the volatility for each stock.")
                return
        N = len(initial_price)
        stock_prices = np.zeros((1825, N))
        # Generating the initial price of the stock data for every company, one at a time
        for i in range(N):
            stock_prices[:, i] = generate_stock_price(1825, initial_price[i], volatility[i])
        return stock_prices
    else:
        # Load the txt in a temp_array, to search for the closest values
        # Use numpy's loadtxt function to load the data, skipping the first row which are strings.
        # Default delimiter is whitespace
        temp_array = np.loadtxt("stock_data_5y.txt")

        volatilities = []
        initial_prices = []
        indices = []
        # if we are given an initial price array
        if initial_price:
            # search based on the initial price
            # search for every company in the initial_price array
            for i in range(len(initial_price)):
                # search in all the companies from the txt file,
                # search only the 1st row for all columns (initial prices)
                abs_diff = 500 # we set a big number of difference at first
                closest_price = 0
                closest_volatility = 0
                index = 0
                for j in range(temp_array.shape[1]):
                    # loop over all the p0 values and check if one is closest than the previous one
                    if abs(temp_array[1,j]-initial_price[i]) < abs_diff:
                        # if the current difference is bigger than the current element we examine,
                        # update the absolute difference variable and set the closest price & volatility we found,
                        # and the index of that position
                        abs_diff = abs(temp_array[1,j]-initial_price[i])
                        closest_price = temp_array[1,j]
                        closest_volatility = temp_array[0,j]
                        index = j
                # At this point we have found the closest initial value for one company,
                # so we add the closest_price we found and volatility to the corresponding arrays.
                initial_prices.append(closest_price)
                volatilities.append(closest_volatility)
                indices.append(index)
            print(f"Found data with initial prices {initial_prices}, and volatilities {volatilities}")
            # If we have an initial_prices array and a volatility array.
            if volatility:
                print("Input argument volatility ignored.")

        # if we are given a volatility array:
        # Will only run if we haven't specified initial_price
        elif volatility and not initial_price:
            # we set "and not initial_price" because if we are given both arrays,
            # the code would run again after the first if.
            # search based on the volatility and for every company
            for i in range(len(volatility)):
                # search in all the companies from the txt file
                abs_diff = 500 # we set a big number of difference at first
                closest_price = 0
                closest_volatility = 0
                index = 0
                for j in range(temp_array.shape[1]):
                    # same logic as before, except this time we are checking the volatility array
                    if abs(temp_array[0,j]-volatility[i]) < abs_diff:
                        abs_diff = abs(temp_array[0, j] - volatility[i])
                        closest_volatility = temp_array[0, j]
                        closest_price = temp_array[1, j]
                        index = j
                initial_prices.append(closest_price)
                volatilities.append(closest_volatility)
                indices.append(index)
            print(f"Found data with initial prices {initial_prices}, and volatilities {volatilities}")
        if len(volatilities) == 0 and len(initial_prices) == 0:
            # the user didn't provide any input params
            # return the initial array we used to search for the closest value to the user,
            # but without the volatilities for every stock (skiprows =1)
            return np.loadtxt("stock_data_5y.txt", skiprows=1)
        else:
            #get the data with the specific indices of the closest initial prices or volatilities provided.
           return np.loadtxt("stock_data_5y.txt", usecols=indices, skiprows=1)