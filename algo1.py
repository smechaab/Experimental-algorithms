import time
import krakenex

class assets:
	num_of_assets = 4
	names = ["XBT", "XRP", "XLM", "EOS"]
	rate_per_asset = 1 / num_of_assets
	initial_percentage_per_asset = 100 / num_of_assets
	

	def setup_assets(initial_invest):
		assets.values = {"XBT" : [assets.initial_percentage_per_asset, initial_invest * assets.rate_per_asset] , \
					"XRP" : [assets.initial_percentage_per_asset, initial_invest * assets.rate_per_asset], \
					"XLM" : [assets.initial_percentage_per_asset, initial_invest * assets.rate_per_asset], \
					"EOS" : [assets.initial_percentage_per_asset, initial_invest * assets.rate_per_asset]}

	def setup_balance(mock_balance):
		assets.balance = {"XBT" : mock_balance["XBT"], \
				"XRP" : mock_balance["XRP"], \
				"XLM" : mock_balance["XLM"], \
				"EOS" : mock_balance["EOS"]}

	def total():
		return sum([assets.values[a][1] for a in assets.values])
		
	def total_without_algorithm():
		return sum([api.mock_balance[a] * api.price[a] for a in assets.values])
	
	def get_asset_percentage(asset):
		return assets.values[asset][0]
	
	def update_percentage():
		new_perc = {}
		[ new_perc.update({a : tools.percentage(assets.values[a][1], assets.total()) }) for a in assets.values ]
		#print("new_perc : ", new_perc)
		
		for a in assets.values:
			assets.values.update({ a : [ new_perc[a], assets.values[ a ] [ 1 ] ] })
			
		print("Percentage in assets.values updated.")
		return 0

	def get_lowest_asset_and_perc():
		lowest_perc = 100
		for a in assets.values:
			if(assets.values[a][0] < lowest_perc):
				lowest_perc = assets.values[a][0]
				lowest_asset = a
		return lowest_asset, lowest_perc
		
	def get_highest_asset_and_perc():
		highest_perc = 0
		for a in assets.values:
			if(assets.values[a][0] > highest_perc):
				highest_perc = assets.values[a][0]
				highest_asset = a
		return highest_asset, highest_perc
		
	# def load_mock_balance(mock_balance, mock_price):
		# for a in mock_balance:
			# assets.values[a][1] = mock_balance[a] * mock_price[a]

class algo:
	#polling_rate = 24 * 60	#algo polling in minutes (1day)
	polling_rate = 60 # polling every 1 hour
	
	def setup_algo(initial_invest):
		print("Initiating algorithm parameters  on : ", assets.names, " - ", assets.initial_percentage_per_asset, " %")
		print("Initial invest amount : ", initial_invest)			
	
	def rebalance_data(asset_to_buy, asset_to_sell, trade_limit = 0):
		perc_diff = assets.initial_percentage_per_asset - assets.get_asset_percentage(asset_to_buy)
		print("algo.rebalance_data : perc_diff : ", perc_diff)
		amount_diff = (perc_diff * assets.total()) / 100
	
		asset_price_sell = api.price[asset_to_sell]
		asset_price_buy = api.price[asset_to_buy]
	
		print("algo.rebalance_data : Buying ", asset_to_buy," with ", asset_to_sell, "for an amount of ", amount_diff)
		
		api.buy(asset_to_buy, asset_to_sell, amount_diff)
	
		return 0
		
		# if (not api.buy(asset_to_buy, asset_to_sell)):
			# return 0
		# else:
			# api.sell(asset_to_sell, "XBT")
			# api.buy(asset_to_buy, "XBT")
		# return 0
	
	def compare_wallet():		
		#perc_diff_list = [ abs(new_perc[i] - assets.values[a][1])  for i, a in enumerate( assets.names ) ]
		
		if( assets.update_percentage() ):
			sys.exit("Warning : Error during percentage update in assets.")
		print (assets.values)
		
		asset_to_buy = assets.get_lowest_asset_and_perc()
		asset_to_sell = assets.get_highest_asset_and_perc()
		
		if( asset_to_sell[1] - asset_to_buy[1] > 2 ): # 2% tolerance
		
			print("Asset to buy : ", asset_to_buy[0], " with ", assets.values[asset_to_buy[0]][1], "USD - " , assets.values[asset_to_buy[0]][0], "%")
			print("Asset to sell : ", asset_to_sell[0], " with ", assets.values[asset_to_sell[0]][1], "USD - " , assets.values[asset_to_sell[0]][0], "%")
			
			return asset_to_buy[0], asset_to_sell[0]
			
		return None
	
	def run_algo_loop():
		assets_to_swap = algo.compare_wallet()
		print("asset_to_swap : ", assets_to_swap)
		while ( assets_to_swap ):		
			if( algo.rebalance_data(assets_to_swap[0], assets_to_swap[1]) ):
				sys.exit("Couldn't make trade between ", assets_to_swap[1], " and ", assets_to_swap[0])
			else:
				assets_to_swap = algo.compare_wallet()
				print("asset_to_swap : ", assets_to_swap)
		print("Algorithm done for this turn.")
				
class api:
	k = krakenex.API()
	k.load_key('kraken.key')
	price = {}
	#mock_price = {"XBT" : 8200, "XRP" : 0.41, "EOS" : 6.40, "XLM" : 1.00}
	mock_balance = {"XBT" : 0.1,\
					"XRP" : 3000,\
					"EOS" : 200,\
					"XLM" : 30}
	
	
	
	def query_and_store_asset_price(asset):
		data_price = api.k.query_public('Ticker',{'pair': asset+"USD",})
		if not data_price['error']:
			i = list( data_price['result'].keys() )[ 0 ]
			api.price.update({ asset : float( data_price['result'][ i ][ 'c' ][ 0 ] ) })
			assets.values[asset][1] = float( data_price['result'][ i ][ 'c' ][ 0 ] ) * assets.balance[asset]
	
				
		
	def refresh_api_data():
		for asset in assets.values:
			api.query_and_store_asset_price(asset)

				
		#print("api.price : ",api.price)
		return 0

	def buy(asset_to_buy, asset_to_sell, amount):
		print ("Buying ",asset_to_buy," with", asset_to_sell, "...")
		
		assets.values[asset_to_buy][1] += amount
		assets.balance[asset_to_buy] += (amount / api.price[asset_to_buy])
		
		assets.values[asset_to_sell][1] -= amount
		assets.balance[asset_to_sell] -= (amount / api.price[asset_to_sell])
		
		assets.update_percentage()
		
		return 0
	
	# def sell(asset_to_sell, asset_to_buy, amount):
		# print ("Selling ",asset_to_sell," with", asset_to_buy, "...")
		# return 0
		
class tools:
	def percentage(data, total_data):
		return (int(data)/int(total_data))*100	

def setup():
	print(tools.percentage(47, 940))

	initial_invest = 1000

	assets.setup_assets(initial_invest)

	print("Total assets amount AVANT : ", assets.total())

	algo.setup_algo(initial_invest)
	assets.setup_balance(api.mock_balance)
	#assets.load_mock_balance(api.mock_balance, api.mock_price) #debug
	#api.refresh_api_data() 

	
	
def run():
	print ("Polling rate : ", algo.polling_rate, "s.")
	
	while (True):
		api.refresh_api_data() 
		algo.run_algo_loop()
		
		year, month, day, hour, minute = time.strftime("%Y,%m,%d,%H,%M").split(',')
		print(hour+":"+minute,"-", day+"/"+month, "---------------- Total assets amount : ", assets.total(), "-------------------")
		print("Profit estimated with algorithm :", assets.total() - assets.total_without_algorithm())
		
		time.sleep(algo.polling_rate)
		
#------------------------------------------------------------------

setup()
run()

