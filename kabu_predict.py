import sys
import os
import csv


def judge_fluctuating():
    pass

# 減少型がありえるかを判定する、base=買値、price=売値、price0=1個前の売値、magnification_acc=累積した補正倍率
def judge_decreasing(base, price, price0=None, magnification_acc=[0.0, 0.0]):
    # magnification_acc[0]=ありえる最低の累積倍率、magnification_acc[1]=ありえる最高の累積倍率
    min_price = base * (0.85 - 0.03 - 0.02 + magnification_acc[0])
    max_price = base * (0.90 - 0.03 + magnification_acc[1])
    if((price >= min_price) and (price <= max_price)):
        judge = True
    else:
        judge = False

    if((magnification_acc == [0.0, 0.0]) or (price0 is None)):
        magnification_acc = [-0.05, -0.03]
    else:
        magnification_acc += (price - price0) / base
    
    return judge, magnification_acc

def judge_smallspike():
    pass

def judge_largespike():
    pass


days = ('月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')

class kabu_log:
    def __init__(self, data):
        if(tuple(data.keys()) != ('名前', '先週', '日曜', '月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')):
            raise Exception("csvファイルのタイトル行が間違っています")

        self.username = data['名前']
        self.base = int(data['日曜'])

        self.prices = dict()
        for day in days:
            if(data[day] == ''):
                self.prices[day] = 0
            else:
                self.prices[day] = int(data[day])

        self.types = dict()
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


    
    def judge(self):
        magnification_acc = [0.0, 0.0]
        price0 = None
        judge = True
        for day in days:
            if(self.prices[day] == 0): break
            judge, magnification_acc = judge_decreasing(self.base, self.prices[day], price0, magnification_acc)
            price0 = self.prices[day]
            if(not judge):
                self.types.pop("減少型")
                break

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
            log.append(kabu_log(row))

    for user in log:
        user.judge()

