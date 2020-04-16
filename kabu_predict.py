import sys
import os
import csv

# カブ価関連情報を保持するクラス
class kabu_log:
    days = ('月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')
    def __init__(self, data):
        if(tuple(data.keys()) != ('名前', '先週', '日曜', '月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')):
            raise Exception("csvファイルのタイトル行が間違っています")

        self.username = data['名前']
        self.base = int(data['日曜'])
        self.prices = dict()
        self.types = dict()

        for day in self.days:
            if(data[day] == ''):
                self.prices[day] = 0
            else:
                self.prices[day] = int(data[day])

        if(data['先週'] == "波型"):
            self.types = {"波型" : 0.20, "減少型" : 0.15, "跳ね小型" : 0.35, "跳ね大型" : 0.30}
        elif(data['先週'] == "減少型"):
            self.types = {"波型" : 0.25, "減少型" : 0.05, "跳ね小型" : 0.25, "跳ね大型" : 0.45}
        elif(data['先週'] == "跳ね小型"):
            self.types = {"波型" : 0.45, "減少型" : 0.15, "跳ね小型" : 0.15, "跳ね大型" : 0.25}
        elif(data['先週'] == "跳ね大型"):
            self.types = {"波型" : 0.50, "減少型" : 0.20, "跳ね小型" : 0.25, "跳ね大型" : 0.05}
        else:
            self.types = {"波型" : 0.25, "減少型" : 0.25, "跳ね小型" : 0.25, "跳ね大型" : 0.25}

# kabu_logに変動型判定機能を追加したクラス
class kabu_judge(kabu_log):
    def __init__(self,data):
        super().__init__(data)
        self.pre_price = None # 1個前の売値
        self.rate_acc = [0.0, 0.0] # 累積した補正倍率、[0]=最低値、[1]=最高値
        self.phase = None # 変動の段階
        self.len = 0 # 変動の長さ
    
    def reset(self):
        self.pre_price = None
        self.rate_acc = [0.0, 0.0]
        self.phase = None
        self.len = 0 # 変動の長さ
    
    def judge_dec(self, price, baserate, rate1, rate2, length):
        min_price = self.base * (baserate[0] + rate1 + rate2[0] + self.rate_acc[0])
        max_price = self.base * (baserate[1] + rate1 + rate2[1] + self.rate_acc[1])
        if((price >= min_price) and (price <= max_price) and (self.len < length[1])):
            # 減少フェーズ継続
            self.len += 1
            if((self.pre_price is None) or (self.rate_acc==[0.0,0.0])):
                self.rate_acc = rate1+rate2
            else:
                self.rate_acc += (price - self.pre_price) / self.base
        elif(self.len >= length[0]):
            # 次フェーズに移行
            len_tmp = self.len
            self.len = 0
            self.rate_acc = [0.0, 0.0]
            return True, len_tmp            
        else:
            return False, None
        return True, None

    def judge_high(self, price, baserate, length):
        min_price = self.base * baserate[0]
        max_price = self.base * baserate[1]
        if((price >= min_price) and (price <= max_price) and (self.len < length[1])):
            # 増加フェーズ継続
            self.len += 1
        elif(self.len >= length[0]):
            # 次フェーズに移行
            len_tmp = self.len
            self.len = 0
            self.rate_acc = [0.0, 0.0]
            return True, len_tmp  
        else:
            return False, None
        return True, None       


    # 波型
    def fluctuating(self):
        self.reset()
        self.phase = "high1"
        for day in self.days:
            if(self.prices[day] == 0): break
            if(self.phase == "high1"): # 1回目の増加フェーズ
                high = self.judge_high(price=self.prices[day], baserate=[0.9,1.4], length=[0,6])
                if(not high[0]):
                    self.types.pop("波型")
                    break
                if(high[1] is not None):
                    # 減少フェーズに移行 
                    hiPhaseLen2 = 7 - high[1]
                    self.phase = "decreasing1" 
            if(self.phase == "decreasing1"): # 1回目の減少フェーズ
                dec = self.judge_dec(price=self.prices[day], baserate=[0.6,0.8], rate1=-0.04, rate2=[-0.06,0.0], length=[2,3])
                if(not dec[0]):
                    self.types.pop("波型")
                    break
                if(dec[1] is not None):
                    # 増加フェーズに移行 
                    decPhaseLen2 = 5 - dec[1]
                    self.phase = "high2"                                 
            if(self.phase == "high2"): # 2回目の増加フェーズ
                high = self.judge_high(price=self.prices[day], baserate=[0.9,1.4], length=[1,hiPhaseLen2])
                if(not high[0]):
                    self.types.pop("波型")
                    break
                if(high[1] is not None):
                    # 減少フェーズに移行 
                    self.phase = "decreasing2"
            if(self.phase == "decreasing2"): # 2回目の減少フェーズ
                dec = self.judge_dec(price=self.prices[day], baserate=[0.6,0.8], rate1=-0.04, rate2=[-0.06,0.0], length=[decPhaseLen2,decPhaseLen2])
                if(not dec[0]):
                    self.types.pop("波型")
                    break
                if(dec[1] is not None):
                    # 増加フェーズに移行 
                    self.phase = "high3"
            if(self.phase == "high3"): # 3回目の増加フェーズ
                high = self.judge_high(price=self.prices[day], baserate=[0.9,1.4], length=[12,12])
                if(not high[0]):
                    self.types.pop("波型")
                    break                                      
            self.pre_price = self.prices[day]                    

    # 減少型
    def decreasing(self):
        self.reset()
        for day in self.days:
            if(self.prices[day] == 0): break
            dec = self.judge_dec(price=self.prices[day], baserate=[0.85,0.90], rate1=-0.03, rate2=[-0.02,0.0], length=[12,12])
            if(not dec[0]):
                self.types.pop("減少型")
                break
            self.pre_price = self.prices[day]
    
    # 跳ね小型
    def smallspike(self):
        self.reset()
        self.phase = "decreasing1"
        for day in self.days:
            if(self.prices[day] == 0): break
            if(self.phase == "decreasing1"): # 1回目の減少フェーズ
                dec = self.judge_dec(price=self.prices[day], baserate=[0.4,0.9], rate1=-0.03, rate2=[-0.02,0.0], length=[0,7])
                if(not dec[0]):
                    self.types.pop("跳ね小型")
                    break
                if(dec[1] is not None):
                    # 跳ね12フェーズに移行 
                    self.phase = "spike12"    
            if(self.phase == "spike12"): # 跳ね12フェーズ
                high = self.judge_high(price=self.prices[day], baserate=[0.9,1.4], length=[2,2])
                if(not high[0]):
                    self.types.pop("跳ね小型")
                    break
                if(high[1] is not None):
                    # 跳ね3フェーズに移行 
                    self.phase = "spike3"
            if(self.phase == "spike3"): # 跳ね3フェーズ
                price_spike3=self.prices[day]
                high = self.judge_high(price=self.prices[day], baserate=[1.4,1.999], length=[1,1])
                if(not high[0]):
                    self.types.pop("跳ね小型")
                    break
                if(high[1] is not None):
                    # 跳ね4フェーズに移行 
                    self.phase = "spike4"
            if(self.phase == "spike4"): # 跳ね4フェーズ
                price_spike4=self.prices[day]
                high = self.judge_high(price=self.prices[day], baserate=[1.4,2.0], length=[1,1])
                if((not high[0]) or (price_spike4 < price_spike3)):
                    self.types.pop("跳ね小型")
                    break
                if(high[1] is not None):
                    # 跳ね5フェーズに移行 
                    self.phase = "spike5"
            if(self.phase == "spike5"): # 跳ね5フェーズ
                price_spike5=self.prices[day]
                high = self.judge_high(price=self.prices[day], baserate=[1.4,1.999], length=[1,1])
                if((not high[0]) or (price_spike4 < price_spike5)):
                    self.types.pop("跳ね小型")
                    break
                if(high[1] is not None):
                    # 減少フェーズに移行 
                    self.phase = "decreasing2"
            if(self.phase == "decreasing2"): # 2回目の減少フェーズ
                dec = self.judge_dec(price=self.prices[day], baserate=[0.4,0.9], rate1=-0.03, rate2=[-0.02,0.0], length=[12,12])
                if(not dec[0]):
                    self.types.pop("跳ね小型")
                    break                                                                                           
            self.pre_price = self.prices[day]

    # 跳ね大型
    def largespike(self):
        pass
    
    def judge(self):
        self.fluctuating()
        self.decreasing()
        self.smallspike()
        self.largespike()

        types_sum = 0.0
        for p in self.types.values(): types_sum += p

        print(self.username + " : ", end='')
        for key in self.types: 
            self.types[key] /= types_sum
            p = self.types[key]*100
            print(key + f" = {p:.1f}%, ", end='')
        print('')        




if __name__ == '__main__':
    args = sys.argv
    if(len(args) != 2):
        print("エラー：引数が正しくありません。以下のような形式で実行してください。", file=sys.stderr)
        print("$ python " + os.path.basename(__file__) + " hoge.csv")     
        sys.exit(1)  
    if(os.path.splitext(args[1])[1] != ".csv"):
        print("エラー：引数が正しくありません。csvファイルを指定してください。", file=sys.stderr)
        sys.exit(1)

    log = list()
    with open(args[1], 'r') as f:
        for row in csv.DictReader(f):
            log.append(kabu_judge(row))

    for user in log:
        user.judge()

