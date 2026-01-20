# GLS Helper

**GLS Helper** は、大規模な Gate Netlist (Verilog) と Standard Delay Format (SDF) ファイルを解析し、クリティカルパスや特定の経路遅延を高速に特定するための Python 製コマンドラインツールです。

## WHAT - これは何か

メモリに収まりきらない巨大な回路データ（数GB〜10GBクラス）を扱うための解析アシスタントです。

* **ストリーミング解析**: ファイルを行単位で読み込み、メモリ使用量を最小限に抑えます。
* **グラフデータベース**: 回路の接続構造（Node/Edge）と遅延情報を SQLite に格納し、永続化します。
* **パス探索**: SQLite の再帰クエリ (Recursive CTE) を活用し、Python 側のメモリを圧迫することなく、DB エンジン内で高速に最大遅延経路（クリティカルパス）を探索します。

## WHY - なぜ作ったか

既存の EDA ツールや単純な Python スクリプトでは、以下のような課題がありました。

1. **メモリ不足 (OOM)**: 10GB を超える SDF やネットリストを全件メモリ上のオブジェクトに変換すると、一般的なワークステーションではメモリが枯渇する。
2. **遅い解析**: 巨大なグラフ構造を Python のループで探索すると時間がかかりすぎる。
3. **複雑な依存**: 商用ツールはライセンスが必要で、手軽なデバッグや CI 環境での自動チェックに向かない。

**GLS Helper** は、「**Five Lines of Code**」や「**Clean Architecture**」の原則に基づいて設計されており、軽量・高速・保守性の高い解析環境を提供します。

## HOW - 使い方

### 前提条件 (Prerequisites)

* Python 3.13 以上
* SQLite3

### インストール (Installation)

リポジトリをクローンし、編集可能モードでインストールします。

```bash
git clone <repository-url>
cd gls-helper
pip install -e .
```

> **Note**: VS Code をお使いの場合は、付属の `.devcontainer` を使用することで、環境構築済みの Docker コンテナ内で即座に開発・実行が可能です。

### コマンド実行 (Commands)

解析は以下の 3 ステップで行います。

#### 1. Verilog のインポート (グラフ構築)

Gate Netlist ファイルを読み込み、ピン（Node）と接続（Edge）のグラフ構造を DB に構築します。

```bash
# 構文: import-verilog <VERILOG_FILE> --db <DB_PATH>
python3 -m src.interface.cli import-verilog design.v --db gls.db
```

#### 2. SDF のインポート (遅延情報の付与)

SDF ファイルを読み込み、構築済みのグラフに対して遅延情報（Delay Rise/Fall）をマージします。
※ 事前に Verilog のインポートが必要です。

```bash
# 構文: import-sdf <SDF_FILE> --db <DB_PATH>
python3 -m src.interface.cli import-sdf delay.sdf --db gls.db
```

#### 3. パス解析 (トレース)

DB 上のグラフを探索し、経路と累積遅延を表示します。

**A. 特定の始点から終点までの最大遅延経路を探す**
デバッグ用途で、特定のピン間のタイミングを確認したい場合に使用します。

```bash
# 構文: trace-path <START_NODE> <END_NODE> --db <DB_PATH>
python3 -m src.interface.cli trace-path "u_cell_1.A" "u_cell_99.Z" --db gls.db
```

**B. クリティカルパス探索 (始点指定)**
終点を省略すると、指定した始点から到達可能なすべてのノードの中で、最も遅延が大きい経路（クリティカルパス）を自動的に特定して表示します。

```bash
# 構文: trace-path <START_NODE> --db <DB_PATH>
python3 -m src.interface.cli trace-path "input_port_A" --db gls.db
```

---

### 出力例

```text
Path found from input_port_A to output_port_Z:
  1. input_port_A -> u_buf_1.A (Rise: 0.00010, Fall: 0.00010)
  2. u_buf_1.Z -> u_logic_2.A1 (Rise: 0.00025, Fall: 0.00020)
  ...
  15. u_last.ZN -> output_port_Z (Rise: 0.00010, Fall: 0.00010)
----------------------------------------
Total Edges: 15
Total Delay: Rise=1.23456, Fall=1.10000

```