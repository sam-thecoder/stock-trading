import sys
import pandas as pd
df = None
from matplotlib import pyplot as plt
from matplotlib import style
style.use('ggplot')

from sklearn.externals import joblib
clf = joblib.load('data/bitcoin-predictor.pkl') 

main_key = 0
game_record = {}

predictions = {
    2: {'loss': 0, 'profit': 0, 'draw': 0},
    1: {'loss': 0, 'profit': 0, 'draw': 0},
    0: {'loss': 0, 'profit': 0, 'draw': 0},
    -1: {'loss': 0, 'profit': 0, 'draw': 0},
    -2: {'loss': 0, 'profit': 0, 'draw': 0}
}

past_predictions  = {
    2: {'loss': 0, 'profit': 0, 'draw': 0},
    1: {'loss': 0, 'profit': 0, 'draw': 0},
    0: {'loss': 0, 'profit': 0, 'draw': 0},
    -1: {'loss': 0, 'profit': 0, 'draw': 0},
    -2: {'loss': 0, 'profit': 0, 'draw': 0}
}

dataframes = {
    'apple': 'data/AAPL-edited.csv',
    'amazon': 'data/AMZN-edited.csv',
    'disney': 'data/EOD-DIS-edited.csv',
    '3M': 'data/EOD-MMM-edited.csv',
    'microsoft': 'data/EOD-MSFT-edited.csv',
    'V': 'data/EOD-V-edited.csv',
    'facebook': 'data/FB-edited.csv',
    'google': 'data/GOOG-edited.csv',
    'netflix': 'data/NFLX-edited.csv',
    'tesla': 'data/TSLA-edited.csv',
    'bitcoin': 'data/BTC-USD-edited.csv',
}

def choose_df():
    global df, dataframes

    print('Available options: "{0}"'.format(', '.join(dataframes.keys())))

    wait = True
    while wait:
        #handles input if your using python 3
        if sys.version.startswith('3'):
            info = input('Please Specify the name of the dataframe: ')
            
        #handles input if you are using python 2
        elif sys.version.startswith('2'):
            info = raw_input('Please Specify the name of the dataframe: ')

        if info in dataframes.keys():
            df = pd.read_csv(dataframes[info])
            print('Dataframe set')
            return df
        elif info == 'n' or info == 'N':
            break
        else:
            print('"{0}" not in the available options'.format(info))
            print('Available options: "{0}"'.format(', '.join(dataframes.keys())))
            print('If you want to exit type in N/n')

    return None

def stock_game(user_key=None, amount=1000, start_date=None, invest_amount=None, withdraw_amount=None):
    global main_key, game_record, predictions, past_predictions
    
    if user_key == None:
        player_name = 'player_{0}'.format(main_key)
        user_key = main_key
        main_key += 1
        
        if start_date != None:
            result = df[df['Date'] == start_date].index.tolist()
            
            #find start date by index
            if result:
                start_index = result[0]
            
            #if date isn't found because of wrong date format or something reverts to default start index
            else:
                start_index = 0
                print('Start Date Not Found. First Date is {0}'.format(df['Date'][0]))
        
        else:
            start_index = 0
        
        if player_name not in game_record.keys():
            print('Player ID not Found, new record being created.')
            player_record = game_record[player_name] = {
                'dys_without_activity': 0,
                'amount': amount,
                'last_game': 0,
                'game_history': {},
                'invested': 0,
                'investment_break_down': {}, #buying price & amount investment, day_id
                'withdraw_breakdown': {}, #day_id withdraw, withdraw amount, stock price
                'start_index': start_index,
                'current_date': start_index,
                'invest_history': [],
                'amount_history': [],
            }
            
        else:
            print('Old Player ID Found, data will be appended to it.)
            player_record = game_record[player_name]
        
        
        #get day's info
        day_info = df.iloc[0]
        
        player_record['current_date'] += 1
        
        #player_name, day_info, amount, profit, loss, game end (boolean)
        return (user_key, day_info, amount, 0, 0, 0, False)
    
    elif user_key != None:
        player_name = 'player_{0}'.format(user_key)
        if player_name in game_record.keys():
            
            print('Old Player ID Found, data will be appended to it.)
            player_record = game_record[player_name]
        else:
            
            print('Player ID not Found, new record being created.')
            player = game_record[player_name] = {
                'dys_without_activity': 0,
                'amount': amount,
                'last_game': 0,
                'game_history': {},
                'invested': 0,
                'investment_break_down': {}, #buying price & amount investment, day_id
                'withdraw_breakdown': {}, #day_id withdraw, withdraw amount, stock price
                'start_index': start_index,
                'current_date': start_index,
                'invest_history': [],
                'amount_history': [],
            }
        
        #move one day into the future
        player_record['current_date'] += 1

        current_date = player_record['current_date']
        
        if current_date > df.shape[0]-1: #last row
            print('Reached the final day, game ending')
            
            day_info = df.iloc[current_date - 1]
            prev_day_info = df.iloc[current_date - 2]
            
            prev_price = prev_day_info[1]
            today_price = day_info[1]

            if player_record['invested']:
                #pct_change = (today_price*100)/prev_price
                new_invest = round( (today_price * player_record['invested'])/prev_price, 2)

                if new_invest > player_record['invested']:
                    profit = new_invest - player_record['invested']
                    loss = 0
                else:
                    loss = player_record['invested'] - new_invest
                    profit = 0
            
            player_record['last_game'] += 1
            return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, True)
        
        day_info = df.iloc[current_date]
        prev_day_info = df.iloc[current_date - 1]
        
        prev_price = prev_day_info[1]
        today_price = day_info[1]
        
        if player_record['invested']:
            #pct_change = (today_price*100)/prev_price
            #new_invest = (player_record['invested'] * pct_change)
            new_invest = round( (today_price * player_record['invested'])/prev_price, 2)
            
            if new_invest > player_record['invested']:
                profit = new_invest - player_record['invested']
                loss = 0
            else:
                loss = player_record['invested'] - new_invest
                profit = 0
            
            player_record['invest_history'].append(player_record['invested'])
            player_record['invested'] = new_invest
        else:
            profit = 0
            loss = 0

        if player_record['amount'] == 0 and player_record['invested'] == 0:
            print("Something went terribly wrong, you're broke... bye!")
            player_record['last_game'] += 1
            return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, True)
        
        if invest_amount == None and withdraw_amount == None and player_record['dys_without_activity'] < 5:
            player_record['dys_without_activity'] += 1
        
        if player_record['invested'] == 0 and player_record['dys_without_activity'] == 5:
            print('You have not invested for 5 consecutive days and have 0 investments, game ending')
            
            player_record['last_game'] += 1
            #end game
            return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, True)
        
        player_record['amount_history'].append(player_record['amount'])
        if invest_amount:
            #1. Check amount to invest exists i.e. <  player amount
            #2. If above passes reset dys_without_activity
            if player_record['amount'] > invest_amount:
                player_record['amount'] -= invest_amount
                player_record['invested'] += invest_amount
                
                player_record['investment_break_down'][current_date] = {
                    'buying_price': today_price,
                    'amount_invested': invest_amount
                }
                
                player_record['dys_without_activity'] = 0
                return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, False)
            else:
                print('You have {0} to invest, the invest amount {1} exceeds this, try again with a smaller amount'.format(player_record['amount'], invest_amount))
                return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, False)
            
        if withdraw_amount:
            #1. If amount invested < withdraw amount
            #2. Reset dys_without_activity
            if player_record['invested'] > withdraw_amount:
                player_record['amount'] += withdraw_amount
                player_record['invested'] -= withdraw_amount
                
                player_record['withdraw_breakdown'][current_date] = {
                    'withdraw_amount': withdraw_amount,
                    'stock_price': today_price
                }
                
                player_record['dys_without_activity'] = 0
                return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, False)
            else:
                print('You have {0} invested, you want to withdraw {1} which exceeds the amount available, try again with a smaller amount'.format(player_record['invested'], withdraw_amount))
                return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, False)
    
    return (user_key, day_info, player_record['amount'], player_record['invested'], profit, loss, False)

#there is one "unrealistic part" of this predictor, it does multiple daily investments in a single loop                 
def player_2(start_date=None, sleep=False, sleep_time=1, plot=False, output=True, miss_output=False, miss_plot=False, show_exception=True, kind='line'):
    user_key, day_info, amount, invested, profit, loss, game_finished = stock_game(start_date=start_date)

    peak_price = day_info[1]
    min_price = day_info[4]
    max_price = day_info[5]
    mean_price = day_info[6]
    invest = None

    total_profit = 0
    max_profit = 0

    week_counter = 0
                  
    #[-1] is the last item on the list the Prediction -2 to 2 values
    week_predictions = [day_info[-1]]

    dys_with_loss = 0
    dys_with_profit = 0

    hold = True
    withdrawn = False
    prev_predict = day_info[-1]
    miss_colors = ['g']

    while game_finished == False:
        if invest == None:
            invest = initial_investment = amount/2
            user_key, day_info, amount, invested, profit, loss, game_finished = stock_game(user_key=user_key, invest_amount=invest)

            if game_finished == True:
                break
        elif hold == True:
            user_key, day_info, amount, invested, profit, loss, game_finished = stock_game(user_key=user_key)

            if game_finished == True:
                break
        elif hold == False:
            user_key, day_info, amount, invested, profit, loss, game_finished = stock_game(user_key=user_key, invest_amount=amount/4)

            if game_finished == True:
                break
        if day_info[1] > peak_price:
            #remember the highest price seen, ever.
            peak_price = day_info[1]

        if profit > 0:
            dys_with_profit += 1
            dys_with_loss = 0
        elif loss > 0:
            dys_with_profit = 0
            dys_with_loss += 1

        if invested > max_profit:
            #remember maximum profit ever made
            max_profit = invested
            amount_lost = 0
            hold = False
        else:
            #hold as a value to act as a deterent
            amount_lost = max_profit - invested
            hold = True

        total_profit += (profit - loss)
        if total_profit > max_profit:
            max_profit = total_profit

        count_dips = len([x for x in week_predictions if x < 0])
        count_ups = len([x for x in week_predictions if x >= 0])

        loss_25 = amount_lost > (initial_investment/4)
        loss_10 = amount_lost > (initial_investment/10)

        if loss_25:
            #withdraw 25%
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, withdraw_amount=invested/4)

            if game_active == True:
                break

            max_profit = invested
            withdrawn = True
        elif withdrawn and loss_10 and dys_with_profit > 3:
            #invest 25%
            withdrawn = False
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/4)

            if game_active == True:
                break

        if count_ups > count_dips and dys_with_profit > 3:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/4)

            if game_active == True:
                break
        elif count_ups > count_dips and dys_with_profit > 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/10)

            if game_active == True:
                break
        elif count_dips < count_ups and dys_with_loss > 3:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, withdraw_amount=invested/4)

            if game_active == True:
                break
        elif count_dips < count_ups and dys_with_loss > 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, withdraw_amount=invested/10)

            if game_active == True:
                break
        elif count_dips == count_ups and dys_with_profit > 3:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/4)

            if game_active == True:
                break
        elif count_ups == count_dips and dys_with_profit > 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/10)

            if game_active == True:
                break
        elif count_ups == count_dips and dys_with_profit == 0 and dys_with_loss == 0:
            pass
        elif count_ups > count_dips and dys_with_profit == 0 and dys_with_loss == 0:
            pass
        elif count_ups < count_dips and dys_with_profit > 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/10)

            if game_active == True:
                break
        elif count_ups == count_dips and dys_with_loss > 0:
            pass
        elif count_ups < count_dips and dys_with_loss > 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, withdraw_amount=invested/10)

            if game_active == True:
                break
        
        #a way to view the inside trends.
        if show_exception:
            print('Ups in Week', count_ups, 'Downs in week', count_dips, 'Days with Profit', dys_with_profit, 'Days with Loss', dys_with_loss)
        

        week_counter += 1
        if week_counter == 7:
            week_counter = 0
            week_predictions = []
        else:
            #add last prediction to week predictions
            week_predictions.append(day_info[-1])

        if output:
            print('day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))

        prev_predict = day_info[-1]
        
        if loss > 0 and profit == 0:
            predictions[day_info[-1]]['loss'] += 1
        elif profit > 0 and loss == 0:
            predictions[day_info[-1]]['profit'] += 1
        elif profit == 0 and loss == 0:
            predictions[day_info[-1]]['draw'] += 1
        else:
            #this is a unicorn event
            print('No match: day', day_info[0])
            print('day: {0} profit: {1.2f} loss: {2.2f} amount: {3.2f} invested: {4.2f} predict: {5.2f}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))
        
        if prev_predict != None:
            if loss > 0 and profit == 0:
                past_predictions[prev_predict]['loss'] += 1
            elif profit > 0 and loss == 0:
                past_predictions[prev_predict]['profit'] += 1
            elif profit == 0 and loss == 0:
                past_predictions[prev_predict]['draw'] += 1
            else:
                #another unicorn event
                print('No match: prev day', prev_predict[0])
                print('day: {0} profit: {1.2f} loss: {2.2f} amount: {3.2f} invested: {4.2f} predict: {5.2f}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))
        
        if miss_plot:
            low_ball = day_info[-1] < 0
            high_ball = day_info[-1] >= 0
            
            if low_ball and profit > 0 or high_ball and loss > 0:
                miss_colors.append('r')
            else:
                miss_colors.append('g')
        
        if miss_output:
            low_ball = day_info[-1] < 0
            high_ball = day_info[-1] >= 0

            if low_ball and profit > 0:
                print('profit day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))
            elif high_ball and loss > 0:
                print('loss day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))            

        #so I can easily assess what's going on
        if sleep:
            time.sleep(sleep_time)    
        
    if not output: #only one output
        print('day: {0} profit: {1} loss: {2} amount: {3} invested: {4}'.format(day_info[0], profit, loss, amount, invested))

    if plot or miss_plot:
        if start_date:
            result = df[df['Date'] == start_date].index.tolist()
            if result:
                start_index = result[0]
            else:
                start_index = 0
        else:
            start_index = 0
        
        df_copy = df[df.index >= start_index].copy()
        df_copy['time'] = pd.to_datetime(df_copy['Date'], format='%m/%d/%Y')

        player_record = game_record['player_{0}'.format(user_key)]

    miss_colors.append('g')
    if miss_plot:
        #make plot bigger
        plt.rcParams['figure.figsize'] = (40,20)
        
        index = []
        count = 0
        for color in miss_colors:
            if color == 'r':
                index.append(count)
            count+=1
        #colors = ['r']*miss_colors.count('r')
        
        #df_copy.plot(kind='scatter', x=df_copy.index.tolist(), y='amount', figsize=(20, 20), colormap=miss_colors)
        #plt.plot(x=df_copy.index, y=df_copy['Value USD'])
        
        plt.scatter(x=index, y=df_copy.iloc[index]['Value USD'], c='r', s=80)
        plt.plot(df_copy.index, df_copy['Value USD'], 'g')
        plt.show()

    if plot:
        try:
            #the len seems to be off by 3
            extended_invest = player_record['invest_history']
            extended_invest.extend([extended_invest[-1]]*3)

            extended_amount = player_record['amount_history']
            extended_amount.extend([extended_amount[-1]]*2)
            
            df_copy['investment'] = extended_invest
            df_copy['amount'] = extended_amount
            if kind == 'scatter':
                df_copy.reset_index().plot(kind=kind, x='index', y=['investment', 'amount', 'Value USD'], figsize=(20, 20))
            
            else:
                df_copy.plot(kind=kind, x='time', y=['investment', 'amount', 'Value USD'], figsize=(20, 20))
        except Exception as e:
            print(str(e))
            print('df copy shape', df_copy.shape)
            print('investment len', len(extended_invest))
            print('amount len', len(extended_amount))
        

def player_3(start_date=None, sleep=False, sleep_time=1, plot=False, output=True, miss_output=False, miss_plot=False, kind='line'):
    user_key, day_info, amount, invested, profit, loss, game_active = stock_game(start_date=start_date)

    miss_colors = ['g']

    while game_active == False:
        predict = clf.predict(day_info[['Value USD', 'Max 7', 'Min 7', 'Change', 'Mean Change 7', 'Drop 7', 'Up 7']].values.reshape(1, -1))[0]
        state = abs(day_info['Predict'])
        
        if state == 0:
            state = 1

        if state == 1:
            state /= 8

        else:
            state /= 4

        if invested == 0:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount/2)

        elif predict == 1:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, invest_amount=amount*state)
        else:
            user_key, day_info, amount, invested, profit, loss, game_active = stock_game(user_key=user_key, withdraw_amount=invested*state)
        
        if output:
            print('day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))

        if miss_plot:
            low_ball = day_info['Predict'] < 0
            high_ball = day_info['Predict'] > 0
            
            if low_ball and profit > 0 or high_ball and loss > 0:
                miss_colors.append('r')
            else:
                miss_colors.append('g')
        
        if miss_output:
            low_ball = day_info['Predict'] < 0
            high_ball = day_info['Predict'] > 0
            if low_ball and profit > 0:
                print('profit day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))
            elif high_ball and loss > 0:
                print('loss day: {0} profit: {1} loss: {2} amount: {3} invested: {4} predict: {5}'.format(day_info[0], profit, loss, amount, invested, day_info[-1]))            

        #so I can easily assess what's going on
        if sleep:
            time.sleep(sleep_time)    
        
    if not output: #only one output
        print('day: {0} profit: {1} loss: {2} amount: {3} invested: {4}'.format(day_info[0], profit, loss, amount, invested))

    if plot or miss_plot:
        if start_date:
            result = df[df['Date'] == start_date].index.tolist()
            if result:
                start_index = result[0]
            else:
                start_index = 0
        else:
            start_index = 0
        
        df_copy = df[df.index >= start_index].copy()
        df_copy['time'] = pd.to_datetime(df_copy['Date'], format='%m/%d/%Y')

        player_record = game_record['player_{0}'.format(user_key)]

    miss_colors.append('g')
    if miss_plot:
        #make plot bigger
        plt.rcParams['figure.figsize'] = (40,20)
        
        index = []
        count = 0
        for color in miss_colors:
            if color == 'r':
                index.append(count)
            count+=1
        #colors = ['r']*miss_colors.count('r')
        
        #df_copy.plot(kind='scatter', x=df_copy.index.tolist(), y='amount', figsize=(20, 20), colormap=miss_colors)
        #plt.plot(x=df_copy.index, y=df_copy['Value USD'])
        plt.scatter(x=df_copy.iloc[index].index, y=df_copy.iloc[index]['Value USD'], c='r', s=80)
        plt.plot(df_copy.index, df_copy['Value USD'], 'g')
        plt.show()

    if plot:
        try:
            #the len seems to be off by 3
            extended_invest = player_record['invest_history']
            extended_invest.extend([extended_invest[-1]]*3)
            extended_amount = player_record['amount_history']
            extended_amount.extend([extended_amount[-1]]*2)
            
            df_copy['investment'] = extended_invest
            df_copy['amount'] = extended_amount
            if kind == 'scatter':
                df_copy.reset_index().plot(kind=kind, x='index', y=['investment', 'amount', 'Value USD'], figsize=(20, 20))
            else:
                df_copy.plot(kind=kind, x='time', y=['investment', 'amount', 'Value USD'], figsize=(20, 20))
        except Exception as e:
            print(str(e))
            print('df copy shape', df_copy.shape)
            print('investment len', len(extended_invest))
            print('amount len', len(extended_amount))