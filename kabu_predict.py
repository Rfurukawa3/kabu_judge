import sys
import os
import csv

days = ('月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')

# カブ価関連情報を保持するクラス
class kabu_log:
    def __init__(self, data):
        if(tuple(data.keys()) != ('名前', '先週', '日曜', '月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')):
            raise Exception("csvファイルのタイトル行が間違っています")

        self.username = data['名前']
        self.base = int(data['日曜'])
        self.prices = dict()
        self.types = dict()

        for day in days:
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
        self.magnification_acc = [0.0, 0.0] # 累積した補正倍率、[0]=最低値、[1]=最高値
        self.stage = None # 変動の段階
    
    def reset(self):
        self.pre_price = None
        self.magnification_acc = [0.0, 0.0]
        self.stage = None

    # 波型
    def fluctuating(self):
        pass    

    # 減少型
    def decreasing(self):
        self.reset()
        for day in days:
            if(self.prices[day] == 0): break
            min_price = self.base * (0.85 - 0.03 - 0.02 + self.magnification_acc[0])
            max_price = self.base * (0.90 - 0.03 + self.magnification_acc[1])
            if((self.prices[day] < min_price) or (self.prices[day] > max_price)):
                self.types.pop("減少型")
                break

            if((self.magnification_acc == [0.0, 0.0]) or (self.pre_price is None)):
                self.magnification_acc = [-0.05, -0.03]
            else:
                self.magnification_acc += (self.prices[day] - self.pre_price) / self.base
            self.pre_price = self.prices[day]

    # 跳ね小型
    def smallspike(self):
        pass

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

