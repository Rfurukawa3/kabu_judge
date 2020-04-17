# kabu_judge

## 概要

あつ森のカブ価の変動型を判定します。

複数人のカブ価を一気に判定することができます。

## 実行環境

* Python 3.7.7

## 使い方

sample.csvのような形式でカブ価を記録したcsvファイルを用意して以下のコマンドを実行してください。

```bash
python kabu_judge.py sample.csv
```

## 注意点

* 一度データが抜けてしまうとそれ以降のデータも無視されてしまいます。
* csvファイルの1行目と変動型の名称はsample.csvの通りにしてください。ここが変わると動きません。
* 自島でカブ未購入の場合の特殊な仕様には未対応です。

## 参考URL

カブ価変動のアルゴリズム及び変動型の名称は以下のwebサイトの情報を元にしています。

<https://hyperts.net/acnh-algorithm/>

<https://gist.github.com/Treeki/85be14d297c80c8b3c0a76375743325b>
