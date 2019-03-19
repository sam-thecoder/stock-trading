import pandas as pd
import random

from game import dataframes

class stock_gym():
	def __init__(self):
		self.df = None
		self.user_key = None
		self.activity = None
		self.amount = 1000
		self.action_space = range(self.amount)

	def update_action_space(self, new_range):
		self.action_space = new_range

	def action_space_sample(self):
		return random.choice(self.action_space)

	def make(self, stock_name):
		if stock_name in dataframes.keys():
			self.df = pd.read_csv(dataframes[stock_name])
		else:
			print('Invalid Input')

	def stock_game(self, start_date=None, invest_amount=None, withdraw_amount=None):
		if self.df ==  None:
			print('No Data Set')
			return None

		if start_date != None:
			if start_date != None:
				result = self.df[self.df['Date'] == start_date].index.tolist()
				if result:
					start_index = result[0]
				else:
					start_index = 0
			else:
				start_index = 0
	        
			self.activity = {
				'dys_without_activity': 0,
				'amount': self.amount,
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
	        
	        #get day's info
			day_info = self.df.iloc[0]
	        
			self.activity['current_date'] += 1
	        
	        #player_name, day_info, amount, profit, loss, game end (boolean)
			return (day_info, self.amount, 0, 0, 0, False)
	    
		elif start_date == None:
	        #print('found user key', user_key)
	        
	        #move one day into the future
	        #print(self.activity['current_date'])
			self.activity['current_date'] += 1
	        #print(self.activity['current_date'])
			current_date = self.activity['current_date']
	        
			if current_date > self.df.shape[0]-1: #last row
				print('Reached the final day, game ending')
	            
				day_info = self.df.iloc[current_date-1]
				prev_day_info = self.df.iloc[current_date-2]

				prev_price = prev_day_info[1]
				today_price = day_info[1]

				if self.activity['invested']:
					#pct_change = (today_price*100)/prev_price
					new_invest = round( (today_price * self.activity['invested'])/prev_price, 2)

					if new_invest > self.activity['invested']:
						profit = new_invest - self.activity['invested']
						loss = 0
					else:
						loss = self.activity['invested'] - new_invest
						profit = 0

				self.activity['last_game'] += 1
				return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, True)
	        
			day_info = self.df.iloc[current_date]
			prev_day_info = self.df.iloc[current_date-1]

			prev_price = prev_day_info[1]
			today_price = day_info[1]

			if self.activity['invested']:
				#pct_change = (today_price*100)/prev_price
				#new_invest = (self.activity['invested'] * pct_change)
				new_invest = round( (today_price * self.activity['invested'])/prev_price, 2)

				if new_invest > self.activity['invested']:
					profit = new_invest - self.activity['invested']
					loss = 0
				else:
					loss = self.activity['invested'] - new_invest
					profit = 0

				self.activity['invest_history'].append(self.activity['invested'])
				self.activity['invested'] = new_invest
			else:
				profit = 0
				loss = 0

			if self.activity['amount'] == 0 and self.activity['invested'] == 0:
				print("Something went terribly wrong, you're broke... bye!")
				self.activity['last_game'] += 1
				return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, True)
	        
			if invest_amount == None and withdraw_amount == None and self.activity['dys_without_activity'] < 5:
				self.activity['dys_without_activity'] += 1
	        
			if self.activity['invested'] == 0 and self.activity['dys_without_activity'] == 5:
				print('You have not invested for 5 consecutive days and have 0 investments, game ending')

				self.activity['last_game'] += 1
				#end game
				return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, True)
	        
			self.activity['amount_history'].append(self.activity['amount'])
			if invest_amount:
				#1. Check amount to invest exists i.e. <  player amount
				#2. If above passes reset dys_without_activity
				if self.activity['amount'] > invest_amount:
					self.activity['amount'] -= invest_amount
					self.activity['invested'] += invest_amount

					self.activity['investment_break_down'][current_date] = {
						'buying_price': today_price,
						'amount_invested': invest_amount
					}

					self.activity['dys_without_activity'] = 0
					return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, False)
				else:
					print('You have {0} to invest, the invest amount {1} exceeds this, try again with a smaller amount'.format(self.activity['amount'], invest_amount))
					return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, False)
	            
			if withdraw_amount:
				#1. If amount invested < withdraw amount
				#2. Reset dys_without_activity
				if self.activity['invested'] > withdraw_amount:
					self.activity['amount'] += withdraw_amount
					self.activity['invested'] -= withdraw_amount

					self.activity['withdraw_breakdown'][current_date] = {
						'withdraw_amount': withdraw_amount,
						'stock_price': today_price
					}

					self.activity['dys_without_activity'] = 0
					return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, False)
				else:
					print('You have {0} invested, you want to withdraw {1} which exceeds the amount available, try again with a smaller amount'.format(self.activity['invested'], withdraw_amount))
					return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, False)

		return (day_info, self.activity['amount'], self.activity['invested'], profit, loss, False)