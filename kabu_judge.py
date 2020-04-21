import sys
import os
import csv
from math import ceil

# カブ価関連情報を保持するクラス
class kabu_log:
    days = ('月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')
    def __init__(self, data):
        if(tuple(data.keys()) != ('名前', '先週', '日曜', '月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')):
            raise Exception("csvファイルのタイトル行が間違っています")

        self.username = data['名前']
        self.prices = dict()
        self.types = dict()

        if(data['日曜'] == ''):
            self.base = 0
        else:
            self.base = int(data['日曜'])

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
    fluctuating_num0 = 56
    decreasing_num0 = 1
    smallspike_num0 = 8
    largespike_num0 = 7
    def __init__(self,data):
        super().__init__(data)
        self.fluctuating = []
        self.fluctuating_num = self.fluctuating_num0
        self.decreasing = []
        self.decreasing_num = self.decreasing_num0
        self.smallspike = []
        self.smallspike_num = self.smallspike_num0
        self.largespike = []
        self.largespike_num = self.largespike_num0        
        if(self.base == 0):
            self.base4gen = [90,110]
        else:
            self.base4gen = [self.base, self.base]

    # 波型の許容範囲を生成
    def gen_fluctuating(self):
        # 各フェーズの長さで場合分けして全パターン生成
        for hiPhaseLen1 in range(7):
            hiPhaseLen2and3 = 7 - hiPhaseLen1
            for hiPhaseLen2 in range(1, hiPhaseLen2and3+1):
                for decPhaseLen1 in (2,3):
                    prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
                    # 増加フェーズ
                    for i in range(hiPhaseLen1):     
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
                    # 減少フェーズ
                    price0 = [self.base4gen[0] * 0.6, self.base4gen[1] * 0.8]
                    for i in range(hiPhaseLen1, hiPhaseLen1+decPhaseLen1):        
                        prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                        if(self.prices[self.days[i]] == 0):    
                            price0 = [price0[0] + self.base4gen[0]*(-0.1), price0[1] + self.base4gen[1]*(-0.04)]
                        else:
                            price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.1), self.prices[self.days[i]] + self.base4gen[1]*(-0.04)]        
                    # 増加フェーズ
                    for i in range(hiPhaseLen1+decPhaseLen1, hiPhaseLen1+decPhaseLen1+hiPhaseLen2):
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)] 
                    # 減少フェーズ
                    price0 = [self.base4gen[0] * 0.6, self.base4gen[1] * 0.8]
                    for i in range(hiPhaseLen1+decPhaseLen1+hiPhaseLen2, hiPhaseLen1+hiPhaseLen2+5):       
                        prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]  
                        if(self.prices[self.days[i]] == 0):    
                            price0 = [price0[0] + self.base4gen[0]*(-0.1), price0[1] + self.base4gen[1]*(-0.04)]
                        else:
                            price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.1), self.prices[self.days[i]] + self.base4gen[1]*(-0.04)]        
                    # 増加フェーズ
                    for i in range(hiPhaseLen1+hiPhaseLen2+5, 12):
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]   
                    self.fluctuating.append(prices_rng)

    # 減少型の許容範囲を生成
    def gen_decreasing(self):
        prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        price0 = [self.base4gen[0] * 0.85, self.base4gen[1] * 0.9]
        for i in range(12):        
            prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
            if(self.prices[self.days[i]] == 0):    
                price0 = [price0[0] + self.base4gen[0]*(-0.05), price0[1] + self.base4gen[1]*(-0.03)]
            else:
                price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.05), self.prices[self.days[i]] + self.base4gen[1]*(-0.03)]                     
        self.decreasing.append(prices_rng)

    # 跳ね小型のの許容範囲を生成
    def gen_smallspike(self):
        for decPhaseLen1 in range(8):
            prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.4, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[0]*(-0.05), price0[1] + self.base4gen[1]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.05), self.prices[self.days[i]] + self.base4gen[1]*(-0.03)]
            # 跳ね12
            for i in range(decPhaseLen1, decPhaseLen1+2):
                prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)] 
            # 跳ね3
            if(self.prices[self.days[decPhaseLen1+3]] == 0):
                prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            else:
                prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 1.4), self.prices[self.days[decPhaseLen1+3]]]
            # 跳ね4
            prices_rng[decPhaseLen1+3] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね5
            if(self.prices[self.days[decPhaseLen1+3]] == 0):
                prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            else:
                prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 1.4), self.prices[self.days[decPhaseLen1+3]]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.4, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1+5, 12):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[0]*(-0.05), price0[1] + self.base4gen[1]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.05), self.prices[self.days[i]] + self.base4gen[1]*(-0.03)]        
            self.smallspike.append(prices_rng)
    
    # 跳ね大型の許容範囲を生成
    def gen_largespike(self):
        for decPhaseLen1 in range(1,8):
            prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.85, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[0]*(-0.05), price0[1] + self.base4gen[1]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[0]*(-0.05), self.prices[self.days[i]] + self.base4gen[1]*(-0.03)]
            # 跳ね1
            prices_rng[decPhaseLen1] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
            # 跳ね2
            prices_rng[decPhaseLen1+1] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね3
            prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 2.0), ceil(self.base4gen[1] * 6.0)]
            # 跳ね4
            prices_rng[decPhaseLen1+3] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね5
            prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
            # 減少フェーズ
            for i in range(decPhaseLen1+5, 12):     
                prices_rng[i] = [ceil(self.base4gen[0] * 0.4), ceil(self.base4gen[1] * 0.9)]
            self.largespike.append(prices_rng)            

    # 各変動型においてあり得るパターン数を返す関数
    def judge_each(self, pattern, pattern_num):
        FUDGE_FACTOR = 5
        for prices_rng in pattern:
            for price_rng, price in zip(prices_rng, self.prices.values()):
                if(price == 0):
                    pass
                elif((price < price_rng[0]-FUDGE_FACTOR) or (price > price_rng[1]+FUDGE_FACTOR)):
                    pattern_num -= 1
                    break
        return pattern_num

    def judge(self):
        self.gen_fluctuating()
        self.fluctuating_num = self.judge_each(self.fluctuating, self.fluctuating_num0)
        self.types["波型"] *= self.fluctuating_num / self.fluctuating_num0

        self.gen_decreasing()
        self.decreasing_num = self.judge_each(self.decreasing, self.decreasing_num0)
        self.types["減少型"] *= self.decreasing_num / self.decreasing_num0

        self.gen_smallspike()
        self.smallspike_num = self.judge_each(self.smallspike, self.smallspike_num0)
        self.types["跳ね小型"] *= self.smallspike_num / self.smallspike_num0

        self.gen_largespike()
        self.largespike_num = self.judge_each(self.largespike, self.largespike_num0)
        self.types["跳ね大型"] *= self.largespike_num / self.largespike_num0 

        for kabutype in ("波型", "減少型", "跳ね小型", "跳ね大型"):
            if(self.types[kabutype] <= 0): self.types.pop(kabutype)

        if(self.types):    
            types_sum = 0.0
            for p in self.types.values(): types_sum += p

            print(self.username + " : ", end='')
            for key in self.types: 
                self.types[key] /= types_sum
                p = self.types[key]*100
                print(key + f" = {p:.1f}%, ", end='')
            print('')  
        else:
            print(self.username + " : 判定不能")



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

