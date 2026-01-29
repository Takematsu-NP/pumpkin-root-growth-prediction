# Pumpkin Root Growth Prediction Project
(カボチャ根の成長予測システム)

2025年度 卒業論文「タイムラプス画像解析と統計的時系列モデルを用いたカボチャ根の成長予測」で使用したプログラムコードです。
本プロジェクトは、Raspberry Piを用いた自動撮影システムと、Windows環境での画像解析・成長予測モデルの2つのパートで構成されています。

## 📂 Repository Structure (ファイル構成)

### 1. Data Analysis & Prediction (データ解析・予測)
**Environment:** Windows (Jupyter Notebook)

* **`thesis_CreateData.ipynb`** (データセット作成・前処理)
    * 画像処理から数値データの生成までを行うツール群です。
    * **画像切り取り**: 撮影画像から解析対象範囲を切り出す処理
    * **前処理**: 色差計算 `(R+G)-B` を用いた根の強調・二値化処理
    * **半自動計測**: 根の領域を手動/自動で抽出し、面積を算出
    * **データ補正**: 時系列データのノイズ除去（単調増加補正）
    * **単位変換**: 画素数(pixels)から実面積(mm²)への変換

* **`thesis_final_model.ipynb`** (成長予測モデル)
    * 作成した時系列データを用いて学習・予測を行うプログラムです。
    * **Prophet**: ロジスティック成長曲線を用いた統計的予測（グリッドサーチによる最適化を含む）
    * **LSTM**: 双方向LSTM (Bidirectional LSTM) を用いた深層学習による予測

### 2. Experiment Control (実験環境制御)
**Environment:** Raspberry Pi (Python Scripts)

* **`timelapse_capture.py`** (自動撮影メインシステム)
    * 複数のUSBカメラを制御し、定期的に植物の画像を撮影してメール送信を行うプログラムです。
    * `uhubctl` を用いたUSB電源制御により、省電力化と長期運用の安定化を図っています。

* **`setup_view.py`** (カメラ設置補助ツール)
    * カメラの画角調整や動作確認を行うためのプレビュー用ツールです。
    * 接続された各カメラの映像をリアルタイムで確認し、設置位置を調整できます。

## 🛠️ Requirements (必要ライブラリ)

### Analysis (Windows)
* Python 3.9.18
* pandas, numpy, matplotlib
* opencv-python
* prophet
* tensorflow, scikit-learn
* japanize-matplotlib

### Experiment (Raspberry Pi)
* Python 3.11.2
* opencv-python
* python-dotenv
* `uhubctl` (System package for USB power control)

## 🚀 Usage (Raspberry Pi Scripts)

実験環境（Raspberry Pi）での実行方法は以下の通りです。

### 1. カメラ位置の調整
まず、以下のコマンドでカメラの映像を確認し、位置を調整します。

```bash
python setup_view.py
```

* `←` `→` キー: カメラ切り替え
* `q` キー: 終了

### 2. 自動撮影の開始
位置合わせ完了後、以下のコマンドで自動撮影を開始します。

```bash
python timelapse_capture.py
```

※ 実行には `.env` ファイルへのGmail設定が必要です（`.env.example` 参照）。

## 📊 Note
個人情報（メールアドレス等）および実験の生画像データの一部は、プライバシー保護のため本リポジトリには含まれていません。
