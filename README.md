# Pumpkin Root Growth Prediction Project
(カボチャ根の成長予測システム)

2025年度 卒業論文「タイムラプス画像解析と統計的時系列モデルを用いたカボチャ根の成長予測」で使用したプログラムコードです。

## 📂 Repository Structure (ファイル構成)

### 1. `thesis_CreateData.ipynb` (データセット作成・前処理)
画像処理から数値データの生成までを行うツール群です。
* **画像切り取り**: 撮影画像から解析対象範囲を切り出すツール
* **前処理**: 色差計算 `(R+G)-B` を用いた根の強調・二値化処理
* **半自動計測**: 根の領域を手動/自動で抽出し、面積を算出するツール
* **データ補正**: 時系列データのノイズ除去（単調増加補正）
* **単位変換**: 画素数(pixels)から実面積(mm²)への変換

### 2. `thesis_final_model.ipynb` (成長予測モデル)
作成した時系列データを用いて学習・予測を行うプログラムです。
* **Prophet**: ロジスティック成長曲線を用いた統計的予測（グリッドサーチによる最適化を含む）
* **LSTM**: 双方向LSTM (Bidirectional LSTM) を用いた深層学習による予測

## 🛠️ Requirements (必要ライブラリ)
本研究のコードを実行するには、以下のライブラリが必要です。

* Python 3.9.18
* pandas
* numpy
* matplotlib
* opencv-python
* prophet
* tensorflow
* scikit-learn
* japanize-matplotlib (グラフの日本語表示用)

## 📊 Note
個人情報および実験の生画像データの一部は、プライバシー保護のため本リポジトリには含まれていません。
