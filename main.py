# =========================================
# 芝麻交易所多合约 AI APP（可视化自主学习版）
# 特点：
#   - BTC/ETH 多合约行情显示
#   - 历史价格显示（最近10条）
#   - AI 决策显示为纯英文：BUY / SELL / HOLD / TP / SL
#   - 仿真止盈/止损
#   - 自主学习：根据盈亏微调买卖阈值
#   - 阈值可视化：显示BUY/SELL阈值变化
#   - 日志记录 log.txt
#   - 安卓手机完全兼容，无乱码
# =========================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime
import requests

# -----------------------------
# 配置
# -----------------------------
SYMBOLS = ["BTC_USDT", "ETH_USDT"]
INTERVAL = 3                     # 更新间隔（秒）
TAKE_PROFIT = 0.01               # 止盈比例
STOP_LOSS   = 0.005              # 止损比例
LOG_FILE = "log.txt"             # 日志文件
LEARNING_FACTOR = 0.0005         # 阈值微调步长

# -----------------------------
# 日志记录函数
# -----------------------------
def write_log(symbol, price, action, extra=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {symbol} | Price: {price:.2f} | Action: {action} | {extra}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

# -----------------------------
# AI 决策（移动平均 + 自主学习）
# -----------------------------
def ai_decision_learn(price, history, thresholds, position=None, entry_price=None):
    if len(history) < 5:
        return "HOLD"
    short_avg = sum(history[-3:])/3
    long_avg = sum(history[-5:])/5
    decision = "HOLD"

    # 仿真止盈/止损优先
    if position == "LONG" and entry_price is not None:
        if price >= entry_price*(1+TAKE_PROFIT):
            return "TP"
        elif price <= entry_price*(1-STOP_LOSS):
            return "SL"
    elif position == "SHORT" and entry_price is not None:
        if price <= entry_price*(1-TAKE_PROFIT):
            return "TP"
        elif price >= entry_price*(1+STOP_LOSS):
            return "SL"

    # 根据阈值决定买卖
    if short_avg > long_avg * thresholds['BUY']:
        decision = "BUY"
    elif short_avg < long_avg * thresholds['SELL']:
        decision = "SELL"
    return decision

# -----------------------------
# 自主学习更新阈值
# -----------------------------
def learn_from_trade(thresholds, position, entry_price, exit_price):
    if position is None or entry_price is None or exit_price is None:
        return
    profit_ratio = (exit_price - entry_price)/entry_price
    if position == "SHORT":
        profit_ratio = -profit_ratio

    if profit_ratio > 0:
        thresholds['BUY'] -= LEARNING_FACTOR
        thresholds['SELL'] += LEARNING_FACTOR
    elif profit_ratio < 0:
        thresholds['BUY'] += LEARNING_FACTOR
        thresholds['SELL'] -= LEARNING_FACTOR

# -----------------------------
# 主界面布局
# -----------------------------
class TradeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # 初始化数据
        self.labels = {}
        self.history = {s: [] for s in SYMBOLS}
        self.position = {s: None for s in SYMBOLS}
        self.entry_price = {s: 0 for s in SYMBOLS}
        self.thresholds = {s:{'BUY':1.002,'SELL':0.998} for s in SYMBOLS}

        # 创建 Label
        for symbol in SYMBOLS:
            lbl = Label(
                text=f"{symbol}: Waiting for data...",
                font_size=28,
                halign='left',
                valign='top',
                size_hint_y=None
            )
            lbl.bind(texture_size=lbl.setter('size'))
            self.labels[symbol] = lbl
            self.add_widget(lbl)

        # 定时更新
        Clock.schedule_interval(self.update_data, INTERVAL)

    # -------------------------
    # 获取芝麻交易所行情
    # -------------------------
    def get_gate_prices(self):
        try:
            r = requests.get("https://api.gateio.ws/api/v4/futures/usdt/tickers", timeout=5)
            data = r.json()
            prices = {}
            for item in data:
                contract = item.get("contract")
                last = item.get("last")
                try:
                    prices[contract] = float(last)
                except:
                    continue
            return prices
        except Exception as e:
            print("Error fetching prices:", e)
            return {}

    # -------------------------
    # 更新界面
    # -------------------------
    def update_data(self, dt):
        prices = self.get_gate_prices()
        for symbol in SYMBOLS:
            if symbol not in prices:
                self.labels[symbol].text = f"{symbol}: Failed to fetch"
                continue

            price = prices[symbol]
            self.history[symbol].append(price)
            self.history[symbol] = self.history[symbol][-50:]

            # AI 决策
            decision = ai_decision_learn(
                price,
                self.history[symbol],
                thresholds=self.thresholds[symbol],
                position=self.position[symbol],
                entry_price=self.entry_price[symbol]
            )

            # 风控逻辑
            if self.position[symbol] is None:
                if decision == "BUY":
                    self.position[symbol] = "LONG"
                    self.entry_price[symbol] = price
                    write_log(symbol, price, "OPEN_LONG")
                elif decision == "SELL":
                    self.position[symbol] = "SHORT"
                    self.entry_price[symbol] = price
                    write_log(symbol, price, "OPEN_SHORT")
            else:
                ep = self.entry_price[symbol]
                if decision in ["TP","SL"]:
                    # 学习阈值
                    learn_from_trade(self.thresholds[symbol], self.position[symbol], ep, price)
                    # 写日志
                    write_log(symbol, price, decision, f"Entry:{ep}")
                    # 清仓
                    self.position[symbol] = None

            # 显示历史+价格+AI决策+阈值
            history_text = "\n".join([f"{p:.2f}" for p in self.history[symbol][-10:]])
            thresholds_text = f"BUY Threshold: {self.thresholds[symbol]['BUY']:.4f} | SELL Threshold: {self.thresholds[symbol]['SELL']:.4f}"
            self.labels[symbol].text = f"{symbol}: Current {price:.2f}\nHistory:\n{history_text}\nAI: {decision}\n{thresholds_text}"

# -----------------------------
# APP入口
# -----------------------------
class TradeApp(App):
    def build(self):
        return TradeLayout()

if __name__ == '__main__':
    TradeApp().run()