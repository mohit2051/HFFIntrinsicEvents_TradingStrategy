import pandas as pd
import argparse
from pathlib import Path
import matplotlib.pyplot as plt


class Algorithm:

    def __init__(self,delta_up, delta_down, FXdatadf):
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.FXdata_df = FXdatadf

        self.record_events = list()
        self.ask_prices = list()
        self.record_prices = list()
        self.mode = ""
        self.S_ext = 0
        self.S_IE = 0

        self.overshoot_end_prices = list()
        self.overshoot_index_values = list()

    def set_values(self) -> None:
        self.ask_prices = self.FXdata_df['Asks'].tolist()

    def get_mode(self, index: int) -> str:
        """
        returns the current mode of the time series
        """
        mode_numeric = self.ask_prices[index] - self.ask_prices[index-1]
        if(mode_numeric>=0):
            return "up"
        return "down"


    def implement_algorithm(self, index: int):
        """
        input: takes index of Ask prices
        output: if the funcitons encounters any intrinsic event then it returns that
        """
        S_tick = self.ask_prices[index]
        if index==0:
            self.S_ext = S_tick
            self.S_IE = S_tick
            self.record_events.append(0)
            self.record_prices.append(S_tick)
            #returns 0 for no event observed
            return 0
        if(index==1):
            self.mode = self.get_mode(index)
            print("mode = ", self.mode)

        if( self.mode == "up"):
            if( (S_tick - self.S_ext) >= self.delta_up ):
                self.mode = "down"
                self.S_ext = S_tick
                self.S_IE = S_tick
                self.record_events.append(1)
                self.record_prices.append(S_tick)
                #returns 1 for an upward directional change
                return 1
            elif(S_tick < self.S_ext):
                self.S_ext = S_tick
                if((self.S_IE - self.S_ext)>=self.delta_down):
                    self.S_IE = S_tick
                    self.record_events.append(-2)
                    self.record_prices.append(S_tick)
                    #tracking overshoot prices
                    self.overshoot_end_prices.append(S_tick)
                    self.overshoot_index_values.append(index)
                    #overshot intrinsic event
                    return -2
                else:
                    self.record_events.append(0)
                    self.record_prices.append(S_tick)
                    return 0
        
        elif( self.mode == "down"):
            if((self.S_ext - S_tick)>=self.delta_down):
                self.mode = "up"
                self.S_ext = S_tick
                self.S_IE = S_tick
                self.record_events.append(-1)
                self.record_prices.append(S_tick)
                #returns -1 for an downward directional change
                return -1
            elif(S_tick > self.S_ext):
                self.S_ext = S_tick
                if((self.S_ext - self.S_IE)>=self.delta_up):
                    self.S_IE = S_tick
                    self.record_events.append(2)
                    self.record_prices.append(S_tick)
                    #tracking overshoot prices
                    self.overshoot_end_prices.append(S_tick)
                    self.overshoot_index_values.append(index)
                    #overshot intrinsic event
                    return 2
                else:
                    self.record_events.append(0)
                    self.record_prices.append(S_tick)
                    return 0
        return None

class ImplementStrategies(Algorithm):
    def __init__(self, delta_up, delta_down, FXdatadf, value ):
        super().__init__(delta_up, delta_down, FXdatadf)
        self.portfolio_amount = value
        self.PnL_value = 0
        self.current_position = None
        self.buy_price = 0
        self.sell_price = 0

    def firstStrategy(self):
       # print("hello")
        self.set_values()
        for i in range(len(self.FXdata_df)):
            
            eventValue  = self.implement_algorithm(i)
            #only open position if current position is closed or nothing
            if(self.current_position != "Open"):
                if(eventValue == 1):
                    #print(f"i = {i}")
                    self.current_position = "Open"
                    self.buy_price = self.ask_prices[i]

                    #check if portfolio has enough value to buy the fx
                    if(self.portfolio_amount >= self.buy_price):
                        #update portfolio value
                        self.PnL_value -= self.buy_price

            #only close the portfolio if the position was open
            if(self.current_position == "Open"):
                if(self.ask_prices[i] >= self.buy_price * (1+(self.delta_up/2))):
                    self.current_position = "Close"
                    self.sell_price = self.ask_prices[i]
                    #update portfolio value
                    self.PnL_value += self.sell_price

                elif(self.ask_prices[i] <= self.buy_price* (1-(self.delta_up/2))):
                    self.current_position = "Close"
                    self.sell_price = self.ask_prices[i]
                    #update portfolio value after taking loss
                    self.PnL_value += self.sell_price





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)

    p = parser.parse_args()
    #print(p.file_path, type(p.file_path), p.file_path.exists())

    FXdatadf = pd.read_csv(p.file_path, sep = ",", header=None)
    
    FXdatadf.columns = ["Date Time", "Bids", "Asks", "Volume"]

    
    temp  = ImplementStrategies(0.005,0.005, FXdatadf, 100)
    temp.firstStrategy()

    ones, minus_ones, twos, minus_twos = 0,0,0,0
    print("events length = ",len(temp.record_events))
    for i in temp.record_events:
        #print("i", i)
        if(i == 1):
            ones= ones+1
        elif(i == 2):
            twos = twos+1
        elif(i == -1):
            minus_ones = minus_ones + 1
        elif(i == -2):
            minus_twos = minus_twos + 1
    print(f"lenght of ask prices = {len(temp.ask_prices)}")
    print(f"ones_count = {ones}, minus_ones_count = {minus_ones}, twos_count = {twos}, minus_twos_count = {minus_twos}")
    print(f"Final PnL Value = {temp.PnL_value}")
    print(f"Final Portfolio Postion = {temp.current_position}")

    
    ask_prices_index_values = FXdatadf.index.tolist()

    plt.figure(figsize=(15,10))
    plt.plot(ask_prices_index_values, temp.ask_prices,'b')
    plt.plot(temp.overshoot_index_values,temp.overshoot_end_prices, 'ro')
    plt.plot(temp.overshoot_index_values,temp.overshoot_end_prices, 'g-')
    plt.show()
    
    # plt.plot(ts.record_prices)
    # plt.plot(ts.ask_prices)
    # plt.show()
    
   