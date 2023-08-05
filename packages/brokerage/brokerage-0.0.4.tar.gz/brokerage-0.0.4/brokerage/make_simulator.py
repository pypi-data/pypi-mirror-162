
class Simulator:
    def __init__(self, random_state=42, speed=0.05):
        import numpy as np

        self.seed = random_state
        np.random.seed(self.seed)

        self.speed = speed
        self.ticks_per_day = int(1 // speed)
        assert self.ticks_per_day > 0, "speed must be < 1.0"
        self.sigma = 0.007
        self.data = []
        self.samples = [
            "2021-01-12,123.0,124.8,121.8,124.0\n",
            "2021-01-13,124.3,125.3,121.5,122.0\n",
        ]
        self.ticket_no = 0
        self.pending = []
        self.transacted = []
        self.cancelled = []

    def _check_instrument(self, instrument):
        from pathlib import Path
        if instrument == "FAKE":
            flag = "FAKE"
        elif (Path(f"{instrument}.csv")).exists():
            p = Path(f"{instrument}.csv")
            print(p.absolute(), p.exists())
            with open(p.absolute(), "r") as fhandle:
                header = fhandle.readline().split(",")
            if len(header) == 2:
                assert header == ["Date", "Price\n"], f"Unknown header:: {header}"
                flag = "ticks"
            elif len(header) == 5:
                assert header == [
                    "Date",
                    "Open",
                    "High",
                    "Low",
                    "Close\n",
                ], f"Unknown header:: {header}"
                flag = "ohlc"
            else:
                raise Exception("Unknown csv format")
        else:
            raise Exception("Unknown instrument")

        return flag

    def _set_tick_data(self, instrument):
        from datetime import datetime

        with open(f"{instrument}.csv", "r") as fhandle:
            header = fhandle.readline()
            data = []
            for line in fhandle:
                ts, p = line.strip().split(",")
                ts = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                data.append([ts, eval(p)])
            self.data = data

    def _gen_trading_time(self, date, start_time, end_time, n_ticks):
        import datetime as dt
        import random

        random.seed(self.seed)

        # FKLI 8:45-12:45, 2:30-5:15
        s = dt.datetime.combine(date, start_time)
        e = dt.datetime.combine(date, end_time)
        delta = e - s

        max_ticks = int(n_ticks * 1.2)
        min_ticks = int(n_ticks * 0.8)
        n_ticks = random.randint(min_ticks, max_ticks)
        ticks = sorted(random.sample(range(delta.seconds), n_ticks))
        trading_times = [s + dt.timedelta(seconds=t) for t in ticks]

        return trading_times

    def _gen_GBM(self, quote, n_ticks):
        import numpy as np

        ## generate quote data
        significant = max([item[::-1].find(".") for item in quote])
        o, h, l, c = [float(item) for item in quote]
        if n_ticks == 4:
            hl = [h, l]
            np.random.shuffle(hl)
            return [o, *hl, c]
        sigma = (h - l) / n_ticks
        dB = np.random.randn(n_ticks) / np.sqrt(n_ticks - 1)
        dB[0] = 0
        B = dB.cumsum()
        ticks = o * np.exp(-(sigma ** 2) / 2 + sigma * B)
        if ticks.max() > ticks.min():
            ticks = (ticks - ticks.min()) * (h - l) / (ticks.max() - ticks.min()) + l
        ticks = np.round(ticks, significant)
        ticks[0] = o
        ticks[-1] = c
        ticks[ticks[1:-1].argmax() + 1] = h
        ticks[ticks[1:-1].argmin() + 1] = l
        cond = ticks[0] == o, ticks.max() == h, ticks.min() == l, ticks[-1] == c
        if not all(cond):
            print(
                f"\033[35mWARNING:: [{o}, {h}, {l}, {c}] not equal [{ticks[0]}, {ticks.max()}, {ticks.min()}, {ticks[-1]}]\033[0m"
            )
        return ticks

    def _set_fake_data(self, samples):
        import datetime as dt
        import numpy as np

        np.random.seed(self.seed)
        n_ticks = int(self.ticks_per_day / 2)
        if n_ticks < 4:
            n_ticks = 4
        ticks_list = []
        dates_list = []
        for sample in samples:  # generate samples day-by-day
            date, o, h, l, c = sample.strip().split(",")
            date = dt.datetime.strptime(date, "%Y-%m-%d")
            am_session = self._gen_trading_time(
                date, dt.time(8, 45), dt.time(12, 45), n_ticks
            )
            pm_session = self._gen_trading_time(
                date, dt.time(14, 30), dt.time(17, 15), n_ticks
            )
            trading_times = am_session + pm_session
            ticks = self._gen_GBM([o, h, l, c], len(trading_times))
            dates_list.extend(trading_times)
            ticks_list.extend(ticks)
        self.data = zip(dates_list, ticks_list)

    def _set_daily_data(self, instrument):
        with open(f"{instrument}.csv", "r") as fhandle:
            header = fhandle.readline()
            data = fhandle.readlines()
            self._set_fake_data(data)

    def connect(self, exchange, instrument):
        print(f"Connecting to Instrument {instrument} ...")
        case_flag = self._check_instrument(instrument)

        if case_flag == "FAKE":
            print("\033[34mSimulator:: Generating FAKE data\033[0m")
            self._set_fake_data(self.samples)
        elif case_flag == "ticks":
            print("\033[34mSimulator:: Pushing ticks data\033[0m")
            self._set_tick_data(instrument)
        elif case_flag == "ohlc":
            print("\033[34mSimulator:: Generating data form ohlc file\033[0m")
            self._set_daily_data(instrument)
        else:
            raise Exception("You shouldn't see this")

    def fill_order(self, order, line):
        ts, price = line[0], line[1]
        order["transac_price"] = price
        order["transac_timestamp"] = ts
        self.transacted.append(order)
        self.pending.remove(order)
        print(f"\033[94m!!>> Order matched: {order}\033[0m", flush=True)

    def update_order(self, line):
        ts, price = line[0], line[1]
        for order in self.pending:
            if order["order_type"] == "Market":
                self.fill_order(order, line)
            elif order["order_type"] == "Limit":
                if order["action"] == "Buy":
                    if price <= order["order_price"]:
                        self.fill_order(order, line)
                elif order["action"] == "Sell":
                    if price >= order["order_price"]:
                        self.fill_order(order, line)
            elif order["order_type"] == "Stop":
                if order['action'] == "Buy":
                    if price >= order['stop_price']:
                        order['order_type'] = "Market"
                elif order['action'] == 'Sell':
                    if price <= order['stop_price']:
                        order['order_type'] = "Market"
            elif order["order_type"] == "Stop-Limit":
                if order['action'] == "Buy":
                    if price >= order['stop_price']:
                        order['order_type'] = "Limit"
                elif order['action'] == 'Sell':
                    if price <= order['stop_price']:
                        order['order_type'] = "Limit"
            else:
                print("Something wrong!")
                raise Exception()

    def data_stream(self):
        import time

        for line in self.data:
            time.sleep(0.01)
            self.update_order(line)
            yield line

    def cancel_order(self, ticket_no):
        for order in self.pending:
            if order["ticket_no"] == ticket_no:
                # print('cancel_order::', order)
                self.cancelled.append(order)
                self.pending.remove(order)
                print(f"\033[37m!!!> Order canceled: {order}\033[0m", flush=True)

    def submit_order(self, price, lot_size, order_type, action, stop_price=None):
        assert price > 0, "price cannot be negative"
        assert lot_size > 0, "lot size has to be greater than zero"
        assert type(lot_size) == int, "has to be integer lot"
        assert order_type in [
            "Market",
            "Limit",
            "Stop",
            "Stop-Limit",
        ], 'order type is either "Market", "Limit" "Stop" or "Stop-Limit"'
        assert action in ["Buy", "Sell"], 'action is either "Buy" or "Sell"'
        if order_type in ["Stop", "Stop-Limit"]:
            assert stop_price > 0, "stop price cannot be negative"

        order = {
            "order_price": price,
            "lot": lot_size,
            "order_type": order_type,
            "action": action,
            "ticket_no": self.ticket_no,
            "stop_price": stop_price,
        }
        self.ticket_no += 1
        self.pending.append(order)
        print(f"\033[32m!>> Submitted order: {order}\033[0m", flush=True)
        return self.ticket_no

    # Check portfolio
    def get_transactions(self, silence=False):
        if not silence:
            print("\033[01m\033[32m>>> -------  pending  ------\033[00m", flush=True)
            for r in self.pending:
                print("\033[32m>>>", r, "\033[00m", flush=True)
            print("\033[01m\033[94m>>> ------ transacted ------\033[00m", flush=True)
            for r in self.transacted:
                print("\033[94m>>>", r, "\033[00m", flush=True)
            print("\033[01m\033[37m>>> ------ cancelled  ------\033[00m", flush=True)
            for r in self.cancelled:
                print("\033[37m>>>", r, "\033[00m", flush=True)
        return (self.pending, self.transacted, self.cancelled)

    def logout(self):
        print("Logout: Bye!")

