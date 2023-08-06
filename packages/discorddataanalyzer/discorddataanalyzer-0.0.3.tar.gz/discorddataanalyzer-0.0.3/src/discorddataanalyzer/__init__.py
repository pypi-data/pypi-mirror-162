import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import time
import pytz
import json
import os
from tzlocal import get_localzone_name
import emoji

to_time = lambda s: dt.datetime(
    int(s[:4]),
    int(s[5:7]),
    int(s[8:10]),
    int(s[11:13]),
    int(s[14:16])
)

dm = lambda n: 'Direct Message with ' + n

msg_path = lambda n: os.path.join("messages", f"c{n}", "messages.csv")

class Data:
    def __init__(self, path: str = ''):
        self.path = path
    def get(self, *paths: str) -> str:
        new_path = self.path
        for path in paths:
            new_path = os.path.join(new_path, path)
        return new_path
            
class Timezone:
    def __init__(self, name: str = '', offset: dt.timedelta = dt.timedelta(0)):
        if name == 'LOCAL':
            name = self.local_name()
            offset = self.local_offset()
        self.offset = offset
        self.name = name
        
    def offset_time(self, utc_time: dt.datetime = dt.datetime.now(pytz.timezone('UTC'))) -> dt.datetime:
        return utc_time + self.offset
    
    def local_offset(self, utc_time: dt.datetime = dt.datetime.now()) -> dt.timedelta:
        timezone = pytz.timezone(self.local_name())
        offset = timezone.localize(utc_time).strftime('%z')
        offset = int(offset)
        hrs, mins = offset//100, offset % 100
        return dt.timedelta(hours = hrs, minutes = mins)
        
    def local_name(self) -> str:
        return get_localzone_name()

class Index:
    def __init__(self, data: Data = Data()):
        self.index = json.load(open(data.get('messages', 'index.json')))                               
        self.IDs = {val: key for key, val in self.index.items()}
        self.IDs.pop(None)
    def search(self, channel_name: str, DM: bool = False) -> int:
        if DM:
            return self.IDs[dm(channel_name)]
        else:
            return self.IDs[channel_name]

class Chat:
    def __init__(self, channel_name: str, DM: bool = False, data: Data = Data(), tz: Timezone = Timezone()):
        if DM:
            self.channel_name = dm(channel_name)
        else:
            self.channel_name = channel_name
        self.DM = channel_name.startswith('Direct Message with ')
        self.ID = Index(data).search(self.channel_name)
        self.path = msg_path(self.ID)
        self.data = pd.read_csv(data.get(self.path))
        self.tz = tz
        
    def messages(self, tz: Timezone = None) -> pd.DataFrame:
        if tz is None:
            tz = self.tz
        data = self.data.drop(columns = ['ID'])
        data['Timestamp'] = [tz.offset_time(to_time(s)) for s in data.Timestamp]
        data['dates'] = [s.date() for s in data.Timestamp]
        data['times'] = [s.time() for s in data.Timestamp]
        return data
    
    def count(self, gaps: bool = True, dr: tuple = None, data: pd.DataFrame = None, tz: Timezone = Timezone()) -> pd.DataFrame:
        if data is None:
            data = self.messages(tz)        
        data = data.value_counts('dates').to_frame().sort_values('dates')
        if dr is None:
            a, b = data.index[0], data.index[-1]
        else:
            a, b = dr
        if gaps:
            missing = [i.date() for i in pd.date_range(a, b) 
               if i.date() not in data.index]
            data = pd.DataFrame(list(data[0]) + [0] * len(missing),
                               list(data.index) + missing).sort_index()
        return data
    
    def total_msgs(self) -> int:
        return len(self.data)
    
    def plot(self):
        plt.figure()
        plt.plot(self.count().index, self.count()[0])
        plt.title(f'{self.channel_name}')
        plt.xticks(rotation=45, ha="right")
        plt.show()
    
    def __str__(self):
        return f'Channel: {self.channel_name}\nID: {self.ID}'
    
    # [FOR DOCUMENTATION Channels.DF_3D] if real is True the the dataframe will be produced using a heavy algorithm that will take much longer to run, in theory. however, it will produce a 'real' three-dimensional dataframe, in that the data will be represented as a rectangular prism. if real is false, the algorithm will produce a pseudo-three-dimensional dataframe, in that all the features part of the Channels class will be able to run properly, but it wont be a rectangular prism. this means that many external operations that would work on a real 3D dataframe, namely slicing, would not function properly on the pseudo-df 
    
class Channels:
    def __init__(self, tz: Timezone = Timezone(), channels: list = None, data: Data = Data()):
        if channels is None:
            channels = Index(data).IDs
        self.objects = [Chat(channel, data = data) for channel in channels]
        self.tz = tz    
    def DF_3D(self, real: bool = False) -> dict: #mins arg only matters if real
        new_df = {}
        if real:        
            freq = pd.tseries.offsets.DateOffset(minutes = 1)            
            earliest, latest = self.date_range()
            date_range = pd.date_range(earliest, latest, freq = freq)

            for chat in self.objects:
                data = chat.messages(self.tz)
                for i in date_range:
                    if i not in data.Timestamp:
                        data.iloc[-1] = [i, np.nan, np.nan, i.date(), i.time()]
                        data.index += 1                
                new_df[chat.channel_name] = data.sort_values('Timestamp')
        else:
            for chat in self.objects:
                new_df[chat.channel_name] = chat.messages(tz = self.tz).sort_values('Timestamp')
        return new_df
    
    def date_range(self) -> tuple:
        earliest, latest = None, None        
        found = False
        #beautiful
        for chat in self.objects:
            ts = list(chat.messages(self.tz).Timestamp)
            if len(ts) == 0:
                continue
            if not found:
                earliest, latest = ts[-1], ts[0]
                found = True
                continue
            if ts[-1] < earliest:
                earliest = ts[-1]
            if ts[0] > latest:
                latest = ts[0]
        return earliest, latest

class Plots:
    def __init__(self, *chats: Chat):
        self.frames = [i.count() for i in chats]
    def plot(self):
        plt.figure()
        for i in self.frames:
            plt.plot(i.index, i[0])
        plt.title('Comparison')
        plt.xticks(rotation=45, ha="right")
        plt.show()
        
class Analyzer:
    def __init__(self, tz: Timezone = Timezone(), period: tuple = None, channels: Channels = None, data: Data = Data()):
        self.tz = tz
        if channels is None:
            channels = Channels(tz = self.tz, data = data)
        self.channels = channels
        if period is None:
            period = self.channels.date_range()
        self.period = period
        
    def filter_period(self, channel: Chat, reset_index: bool = False) -> pd.DataFrame:
        earliest, latest = self.period
        data = channel.messages(self.tz)
        if len(data) > 0:
            data = data[(data['Timestamp'] <= latest) & (data['Timestamp'] >= earliest)] #not inclusive
        if reset_index:
            data = data.reset_index()
        return data
          
    def analyze(self):# interacts with the console
        # show time perod
        e, l = self.period
        print(f"Time period of {e} to {l}.")
        print()
        # show channels
        print("The channels considered are the following:")
        print()
        for channel in self.channels.objects:
            print(channel, end = '\n-\n')
        print()
        # show messages number
        print(f'Messages rank during selected time period:')
        print()
        nm = self.num_msgs()
        nums = nm['nums']
        counter = 1
        while len(nums) > 0:
            m = max(nums, key = nums.get)
            print(f"{counter}. {m.channel_name}")
            print(f"Count: {nums[m]}")
            print()
            nums.pop(m)
            counter += 1
        self.plot_msgs()
        print()
        self.plot_wc()
        print()
        self.plot_emoji_count()       
        
    def num_msgs(self) -> dict:
        nums = {channel:len(self.filter_period(channel)) for channel in self.channels.objects}  
        return {'nums': nums, 'max': max(nums, key = nums.get)}
    
    def daily_count(self) -> pd.DataFrame:
        df = None
        for obj in self.channels.objects:
            d = self.filter_period(obj, reset_index = True)
            dtf = obj.count(dr = self.period, data = d, tz = self.tz)
            if df is None:
                df = dtf
                continue
            df += dtf
        return df
    
    def plot_msgs(self):
        df = self.daily_count()
        plt.figure()
        plt.plot(df.index, df[0])
        plt.title('Messages sent per day')
        plt.xticks(rotation=45, ha="right")
        plt.show()
    
    def word_count(self, allow: list = [], disallow: list = [], allow_all: bool = False, just_words: bool = False): #allow *always* overrides disallow
        punc = [',', '.', '!', '?', '/', '>', '<', '\'', '"', ';', '(', ')', '-', '~', '#', '$', '%', '^', '&', '*', '[', ']', '{', '}', '=', '+', ':', "_", "|", "@"]
        cwords = ['the','at','there','my','of','than','and','this','an','a','to','from','which','in','or','is','had','by','their','has','its','it','if','but','was','not','for','what','on','all','are','were','as'] + disallow
        if allow_all:
            cwords = []        
        cwords = [i for i in cwords if i not in allow]
        punc = [i for i in punc if i not in allow]
        words = []
        for channel in self.channels.objects:
            msgs = self.filter_period(channel)
            for i in msgs.Contents:
                for j in str(i).split(' '):
                    string = ''
                    for k in j:
                        if k not in punc:
                            string += k  
                    if string != '' and string.lower() not in cwords:
                        words.append(string.lower())
        df = pd.DataFrame(words)
        if just_words:
            return words
        return df.value_counts().to_frame()
    
    def emoji_count(self, just_emojis: bool = False):
        emojis = []
        for channel in self.channels.objects:
            msgs = self.filter_period(channel)
            for i in msgs.Contents:
                for j in str(i).split(' '):
                    for k in j:
                        if emoji.is_emoji(k):
                            emojis.append(k)
        df = pd.DataFrame(emojis)
        if just_emojis:
            return emojis
        return df.value_counts().to_frame()
    
    def plot_wc(self, percentile = 0.9996, wc_args = {}):
        wc = self.word_count(**wc_args)
        wc = wc[wc[0].quantile(percentile) < wc[0]]
        plt.figure()
        plt.title("Occurences of Words")
        plt.pie(x = wc[0], labels = [i[0] for i in wc.index], autopct='%1.1f%%', startangle=90)
        plt.show()
        
    def plot_emoji_count(self, percentile = 0.99, ec_args = {}):
        ec = self.emoji_count(**ec_args)
        ec = ec[ec[0].quantile(percentile) < ec[0]]
        plt.figure()
        plt.title("Occurences of Emojis")
        plt.pie(x = ec[0], labels = [i[0] for i in ec.index], autopct='%1.1f%%', startangle=90)
        plt.show()