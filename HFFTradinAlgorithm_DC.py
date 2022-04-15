import pandas as pd
import argparse
from pathlib import Path
import matplotlib.pyplot as plt



class TradingStrategy:

    def __init__(self,delta_up, delta_down, FXdatadf):
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.FXdata_df = FXdatadf

        #print("HELLO",FXdatadf,len(FXdatadf))
        self.record_events = list()
        self.ask_prices = list()
        self.date_time = list()
        self.record_prices = list()
        self.record_time = list()

    def set_values(self):
        self.ask_prices = self.FXdata_df['Asks'].tolist()
        self.date_time = self.FXdata_df['Date Time'].tolist()

    def get_mode(self, index) -> str:
        mode_numeric = self.ask_prices[index] - self.ask_prices[index-1]
        if(mode_numeric>=0):
            return "up"
        return "down"


    def implement_algorithm(self):
        #S_ext, S_IE = 0.0, 0.0
        mode = ""
        self.set_values()
        
        for i in range(len(self.FXdata_df)):
            S_tick = self.ask_prices[i]
            if i==0:
                S_ext = S_tick
                S_IE = S_tick
                self.record_events.append(0)
                self.record_prices.append(S_tick)
                self.record_time.append(self.date_time[i])
            if(i==1):
                mode = self.get_mode(i)
                #print("mode = ", mode)

            if( mode == "up"):
                if( (S_tick - S_ext) >= self.delta_up ):
                    mode = "down"
                    S_ext = S_tick
                    S_IE = S_tick
                    self.record_events.append(1)
                    self.record_prices.append(S_tick)
                    self.record_time.append(self.date_time[i])
                elif(S_tick < S_ext):
                    S_ext = S_tick
                    if((S_IE - S_ext)>=self.delta_down):
                        S_IE = S_tick
                        self.record_events.append(-2)
                        self.record_prices.append(S_tick)
                        self.record_time.append(self.date_time[i])
                        #continue
                    else:
                        self.record_events.append(0)
                        self.record_prices.append(S_tick)
                        self.record_time.append(self.date_time[i])
                        #continue
            
            elif( mode == "down"):
                if((S_ext - S_tick)>=self.delta_down):
                    mode = "up"
                    S_ext = S_tick
                    S_IE = S_tick
                    self.record_events.append(-1)
                    self.record_prices.append(S_tick)
                    self.record_time.append(self.date_time[i])
                    #continue
                elif(S_tick > S_ext):
                    S_ext = S_tick
                    if((S_ext - S_IE)>=self.delta_up):
                        S_IE = S_tick
                        self.record_events.append(2)
                        self.record_prices.append(S_tick)
                        self.record_time.append(self.date_time[i])
                        #continue
                    else:
                        self.record_events.append(0)
                        self.record_prices.append(S_tick)
                        self.record_time.append(self.date_time[i])
                        #continue
        #print(i)
        return self.record_events

class ImplementStrategies(TradingStrategy):
    def __init__(self, delta_up, delta_down, FXdatadf, value ):
        super().__init__(delta_up, delta_down, FXdatadf)
        self.portfolio_amount = value
        self.PnL = 0
        self.current_position = None
        self.buy_price = 0
        self.sell_price = 0

    def firstStrategy(self):
        for i in range(len(self.record_events)):
            #only open position if current position is closed or nothing
            if(self.current_position != "Open"):
                if(self.record_events[i] == 1):
                
                    self.current_position = "Open"
                    self.buy_price = self.record_prices[i]

                    #check if portfolio has enough value to buy the fx
                    if(self.portfolio_amount >= self.buy_price):
                        #update portfolio value
                        self.PnL -= self.buy_price

            #only close the portfolio if the position was open
            if(self.current_position == "Open"):
                if(self.record_prices[i] >= self.buy_price * (1+(self.delta_up/2))):
                    self.current_position = "Close"
                    self.sell_price = self.record_prices[i]
                    #update portfolio value
                    self.PnL += self.sell_price

                elif(self.record_prices[i] <= self.buy_price* (1-(self.delta_up/2))):
                    self.current_position = "Close"
                    self.sell_price = self.record_prices[i]
                    #update portfolio value after taking loss
                    self.PnL += self.sell_price





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)

    p = parser.parse_args()
    #print(p.file_path, type(p.file_path), p.file_path.exists())

    FXdatadf = pd.read_csv(p.file_path, sep = ",", header=None)
    
    FXdatadf.columns = ["Date Time", "Bids", "Asks", "Volume"]
    
    temp  = ImplementStrategies(0.01,0.01, FXdatadf, 100)
    events = temp.implement_algorithm()

    count = 0
    print("events length = ",len(temp.record_events))
    print("record price length = ",len(temp.record_prices))
    print("record time length = ",len(temp.record_time))
    for i in temp.record_events:
        #print("i", i)
        if(i == 1):
            count= count+1
    print(f"lenght of ask prices = {len(temp.ask_prices)}")
    print("count = ", count)

    temp.firstStrategy()
    print(f"Final Portfolio Value = {temp.PnL}")
    print(f"Final Portfolio Postion = {temp.current_position}")


    # x = ts.record_time
    # y = ts.record_prices
    # z_t = ts.date_time
    # z = ts.ask_prices
    # plt.plot(x, y)
    # plt.plot(z_t, z)

    plt.plot(temp.record_prices)
    # plt.plot(temp.ask_prices)
    plt.show()
    
   