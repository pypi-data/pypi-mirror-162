# -*- coding: utf-8 -*-
# @Time    : 18/3/2021 9:47 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: event_engine.py
# @Software: PyCharm

"""
Copyright (C) 2020 Joseph Chen - All Rights Reserved
You may use, distribute and modify this code under the
terms of the JXW license, which unfortunately won't be
written for another century.

You should have received a copy of the JXW license with
this file. If not, please write to: josephchenhk@gmail.com
"""

import os
import pickle
from time import sleep
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import shutil

import pandas as pd

from qtrader.core.constants import TradeMode, Direction, Offset, OrderType
from qtrader.core.data import Bar
from qtrader.core.engine import Engine
from qtrader.core.security import Security
from qtrader.core.strategy import BaseStrategy
from qtrader.core.utility import timeit
from qtrader.config import TIME_STEP, IGNORE_TIMESTEP_OVERFLOW


class BarEventEngineRecorder:
    """Record variables in bar event-engine"""

    def __init__(self, **kwargs):
        self.recorded_methods = {
            "datetime": "append",
            "portfolio_value": "append",
            "strategy_portfolio_value": "append",
            "action": "append"
        }
        self.datetime = []
        self.portfolio_value = []
        self.strategy_portfolio_value = []
        self.action = []
        for k, v in kwargs.items():
            if v is None:
                self.recorded_methods[str(k)] = "override"
            elif isinstance(v, list) and len(v) == 0:
                self.recorded_methods[str(k)] = "append"
            else:
                raise ValueError(
                    f"Input param `{k}` for BarEventEngineRecorder is "
                    f"{type(v)}, only [] or None is valid!")
            setattr(self, k, v)

    def get_recorded_fields(self):
        return list(self.recorded_methods.keys())

    def write_record(self, field, value):
        record = getattr(self, field, None)
        if self.recorded_methods[field] == "append":
            record.append(value)
        elif self.recorded_methods[field] == "override":
            setattr(self, field, value)

    def save_csv(self, file_name: str = "result", path: str = None):
        """save all variables to csv"""
        vars = [attr for attr in dir(self) if not callable(
            getattr(self, attr)) and not attr.startswith("__")]
        assert "datetime" in vars, "`datetime` is not in the recorder!"
        assert "portfolio_value" in vars, (
            "`portfolio_value` is not in the recorder!")
        assert "strategy_portfolio_value" in vars, (
            "`strategy_portfolio_value` is not in the recorder!")
        assert "action" in vars, "`action` is not in the recorder!"
        if path is None:
            path = "results"
        if path not in os.listdir():
            os.mkdir(path)
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H-%M-%S.%f')
        os.mkdir(f"{path}/{now}")

        dt = getattr(self, "datetime")
        pv = getattr(self, "portfolio_value")
        spv = getattr(self, "strategy_portfolio_value")
        act = getattr(self, "action")
        df = pd.DataFrame(
            [dt, pv, spv, act],
            index=["datetime",
                   "portfolio_value",
                   "strategy_portfolio_value",
                   "action"]
        ).T
        for var in vars:
            if var in (
                "datetime",
                "portfolio_value",
                "strategy_portfolio_value",
                "action",
                "recorded_methods"
            ):
                continue
            v = getattr(self, var)
            if self.recorded_methods[var] == "append":
                df[var] = v
            elif self.recorded_methods[var] == "override":
                df[var] = None
                if (
                    isinstance(v, list)
                    and len(v) > 0
                    and isinstance(v[0][0], datetime)
                    and isinstance(v[0][1], str)
                ):
                    for i in range(len(v)):
                        date_time = v[i][0]
                        idx = df[df["datetime"] == date_time].index[0]
                        if df.loc[idx, var] is None:
                            df.loc[idx, var] = v[i][1]
                        elif isinstance(df.loc[idx, var], str):
                            df.loc[idx, var] = (
                                df.loc[idx, var] + "; " + v[i][1]
                            )
                else:
                    df.iloc[len(dt) - 1, df.columns.get_loc(var)] = str(v)
        df.to_csv(f"{path}/{now}/{file_name}.csv", index=False)
        return f"{os.getcwd()}/{path}/{now}/{file_name}.csv"


class BarEventEngine:
    """
    Bar Event Engine
    """

    def __init__(
            self,
            strategies: Dict[str, BaseStrategy],
            recorders: Dict[str, BarEventEngineRecorder],
            engine: Engine,
            start: datetime = None,
            end: datetime = None
    ):
        self.strategies = strategies
        self.recorders = recorders
        # bind strategies to engine
        setattr(engine, "strategies", strategies)
        self.engine = engine
        self.trade_modes = {}
        starts = {}
        ends = {}
        for gateway_name in engine.gateways:
            # mode could be either Backtest, Simulate, or Livetrade
            self.trade_modes[gateway_name] = engine.gateways[gateway_name].trade_mode
            # After setting trade_mode, try to synchronized account balance and
            # positions with broker
            engine.sync_broker_balance(gateway_name=gateway_name)
            engine.sync_broker_position(gateway_name=gateway_name)
            # Output the info
            engine.log.info(
                engine.get_balance(gateway_name=gateway_name)
            )
            engine.log.info(
                engine.get_all_positions(gateway_name=gateway_name)
            )
            # Different gateways might have different start and end time
            if engine.gateways[gateway_name].start:
                starts[gateway_name] = engine.gateways[gateway_name].start
            if engine.gateways[gateway_name].end:
                ends[gateway_name] = engine.gateways[gateway_name].end

        # backtest mode can not coexist with livetrade/simulate mode
        backtest_livetrade = (
            TradeMode.BACKTEST in self.trade_modes.values()
            and TradeMode.LIVETRADE in self.trade_modes.values()
        )
        backtest_simulate = (
            TradeMode.BACKTEST in self.trade_modes.values()
            and TradeMode.SIMULATE in self.trade_modes.values()
        )
        if backtest_livetrade or backtest_simulate:
            raise ValueError(
                "Error: backtest mode can not coexist with livetrade/simulate "
                "mode!")

        # Determine start and end time
        if start is None:
            start = datetime.now()
            for gateway_name in starts:
                if starts[gateway_name] < start:
                    start = starts[gateway_name]
        self.start = start
        if end is None:
            if TradeMode.BACKTEST in self.trade_modes.values():
                end = datetime(1970, 1, 1, 0, 0, 0)
            else:
                end = datetime.now() + timedelta(minutes=2)
            for gateway_name in ends:
                if ends[gateway_name] > end:
                    end = ends[gateway_name]
        self.end = end

    @timeit
    def run(self):
        engine = self.engine
        plugins = engine.get_plugins()
        gateways = engine.gateways

        # telegram bot
        if "telegram" in plugins:
            telegram_bot = plugins["telegram"].bot
            telegram_bot.send_message(
                f"{datetime.now()} {telegram_bot.__doc__}")

        # Live trade monitor
        if "monitor" in plugins:
            Path(".qtrader_cache/livemonitor").mkdir(
                parents=True,
                exist_ok=True)
            # remove existing folders if there is any
            existing_dirs = os.listdir(Path(".qtrader_cache/livemonitor"))
            existing_dirs = [d for d in existing_dirs if
                             not d.startswith(".")]
            for dir_ in existing_dirs:
                shutil.rmtree(Path(f".qtrader_cache/livemonitor/{dir_}"))

            from subprocess import Popen
            from qtrader.plugins.monitor import livemonitor
            # start time of all gateways are the same, just get one of them
            monitor_name = self.start.strftime("%Y%m%d")
            strategies = {}
            for strategy_name, strategy in self.strategies.items():
                security_codes = {}
                for gateway_name, securities in strategy.securities.items():
                    security_codes[gateway_name] = [
                        sec.code for sec in securities]
                strategies[strategy_name] = security_codes
            proc_livemonitor = Popen([
                'python',
                f'{livemonitor.__file__}',
                f'{monitor_name}',
                f'{strategies}'
            ],
                # shell=True
            )

        engine.start()

        cur_datetime = self.start
        livemonitor_name = cur_datetime.strftime("%Y%m%d")
        # start event loop
        while cur_datetime <= self.end:
            potential_next_datetime = (
                cur_datetime + timedelta(milliseconds=TIME_STEP)
            )
            # Check trading time of each gateway, if cur_datetime does not in
            # trading time, it will jump to next trading session
            jump_to_datetime = {}
            for gateway_name in gateways:
                gateway = gateways[gateway_name]
                trade_mode = self.trade_modes[gateway_name]
                if not gateway.is_trading_time(cur_datetime):
                    if trade_mode == TradeMode.BACKTEST:
                        next_trading_datetime = {}
                        for security in gateway.securities:
                            next_trading_dt = gateway.next_trading_datetime(
                                cur_datetime,
                                security
                            )
                            if next_trading_dt is not None:
                                next_trading_datetime[security] = next_trading_dt
                        if len(next_trading_datetime) == 0:
                            break
                        sorted_next_trading_datetime = sorted(
                            next_trading_datetime.items(),
                            key=lambda item: item[1])
                        engine.log.info(
                            f"{cur_datetime} is NOT in trading hours of "
                            f"{gateway_name}, jump to "
                            f"{sorted_next_trading_datetime[0][1]}")
                        jump_to_datetime[gateway_name] = sorted_next_trading_datetime[0][1]
                    elif trade_mode in (TradeMode.LIVETRADE, TradeMode.SIMULATE):
                        jump_to_datetime[gateway_name] = (
                            cur_datetime + timedelta(milliseconds=TIME_STEP)
                        )

            # None of the gateways are in trading hours
            if len(jump_to_datetime) == len(gateways):
                cur_datetime = min(jump_to_datetime.values())
                continue

            # At least one of the gateways is in trading hours
            active_gateways = [
                gateway_name
                for gateway_name in gateways
                if gateway_name not in jump_to_datetime]
            assert len(active_gateways) >= 1, (
                f"Active gateways is: {len(active_gateways)}. We expect at "
                "least 1."
            )

            # Get recent OHLCV data for each security and gateway
            if "cur_data" in locals():
                prev_data = {k: v for k, v in cur_data.items()}
            else:
                prev_data = {}
            cur_data = {}
            for gateway_name in active_gateways:
                gateway = gateways[gateway_name]
                cur_gateway_data = {}
                for security in gateway.securities:
                    if self.trade_modes[gateway_name] == TradeMode.BACKTEST:
                        data = gateway.get_recent_data(security, cur_datetime)
                    else:
                        data = gateway.get_recent_data(security)
                    # bar timestamp must be within trading hours
                    if data and gateway.is_trading_time(data.datetime):
                        cur_gateway_data[security] = data
                if cur_gateway_data:
                    cur_data[gateway_name] = cur_gateway_data

            # If data is not updated at all, we ignore the data
            data_updated = True if cur_data != prev_data else False

            # Execute the strategy if recent data is obtained, otherwise jump
            # to the next time step
            if cur_data and data_updated:

                # For backtest, due to data sparsity of some security, the
                # interval between two adjacent bars might be more than 1
                # TIME_STEP:
                #  |-----------|-----------|------------|
                # bar    (missing bar)    bar          bar
                #           cur_time
                #  <-----------| (drag it back to datetime of most recent bar)

                if len(cur_data) == 1 and "Backtest" in cur_data:
                    most_recent_bar_datetime = get_latest_datetime(
                        cur_data, ["Backtest"])
                    assert cur_datetime >= most_recent_bar_datetime, (
                        f"Current datetime {cur_datetime} can't be "
                        f"earlier than {most_recent_bar_datetime}"
                    )
                    # (In Backtest) Drag cur_datetime back to the latest
                    # datetime of the most recent bars
                    past_seconds = (cur_datetime
                                    - most_recent_bar_datetime).total_seconds()
                    past_steps = past_seconds * 1000. / TIME_STEP
                    if 0 < past_steps < 1:
                        cur_datetime = most_recent_bar_datetime
                        gateways["Backtest"].market_datetime = most_recent_bar_datetime

                # For each strategy
                for strategy_name, strategy in self.strategies.items():

                    # clear actions and prepare bar data before running
                    # strategy
                    for gateway_name in strategy.securities:
                        # clear actions
                        strategy.reset_action(gateway_name)

                        # cache recent bar data, to be consumed in get_open,
                        # get_high, etc
                        gateway = gateways[gateway_name]
                        for security in strategy.securities[gateway_name]:
                            if security not in cur_data[gateway_name]:
                                bar_data = Bar(
                                    datetime=cur_datetime,
                                    security=security,
                                    open=None,
                                    high=None,
                                    low=None,
                                    close=None,
                                    volume=None
                                )
                            else:
                                bar_data = cur_data[gateway_name][security]
                            strategy.update_bar(
                                gateway_name,
                                security,
                                bar_data
                            )

                    # run strategy
                    strategy.on_bar(cur_data)

                    # live monitor
                    monitor_file = (".qtrader_cache/livemonitor/"
                                    f"{strategy_name}/{livemonitor_name}")
                    if "monitor" in plugins:
                        if Path(monitor_file).exists():
                            with open(monitor_file, "rb") as f:
                                livemonitor_data = pickle.load(f)
                        else:
                            livemonitor_data = {}

                    # record variables for each gateway in the strategy
                    record_variables = {}
                    for gateway_name in strategy.securities:
                        # record variables by gateway
                        for field in self.recorders[strategy_name].get_recorded_fields(
                        ):
                            value = getattr(
                                strategy, f"get_{field}")(gateway_name)
                            if field in ("datetime", "bar_datetime"):
                                value = value.strftime("%Y-%m-%d %H:%M:%S")
                            if record_variables.get(field) is None:
                                record_variables[field] = [value]
                            else:
                                record_variables[field].append(value)

                    # write recorded variables
                    for field, value in record_variables.items():
                        self.recorders[strategy_name].write_record(
                            field, value)

                        # save information for live monitor
                        if "monitor" in plugins:
                            values = livemonitor_data.get(field)
                            if values is None:
                                livemonitor_data[field] = [value]
                            else:
                                values.append(value)
                                livemonitor_data[field] = values

                    # dump the live monitor data for append/reuse later
                    if "monitor" in plugins:
                        Path(f".qtrader_cache/livemonitor/{strategy_name}").mkdir(
                            parents=True,
                            exist_ok=True
                        )
                        with open(monitor_file, "wb") as f:
                            pickle.dump(livemonitor_data, f)

            # If telegram plugin is activated, can be used to control the
            # engine
            if "telegram" in plugins:
                telegrambot_control(engine)
            if engine.status == "inactive":
                return

            # Update timestamp for the event loop
            if TradeMode.BACKTEST in self.trade_modes.values():
                cur_datetime += timedelta(milliseconds=TIME_STEP)
            elif (
                    TradeMode.LIVETRADE in self.trade_modes.values()
                    or TradeMode.SIMULATE in self.trade_modes.values()
            ):
                sleep_time = (
                    potential_next_datetime - datetime.now()
                ).total_seconds()
                if sleep_time < 0:
                    if IGNORE_TIMESTEP_OVERFLOW:
                        engine.log.debug(
                            f"[WARN] Current time ({datetime.now()}) exceeds "
                            "expected bar interval.\nExpected next bartime is "
                            f"{potential_next_datetime})!\n")
                        sleep_time = 0.0
                    else:
                        raise OverflowError(
                            f"Current time ({datetime.now()}) exceeds expected "
                            "bar interval.\nExpected next bartime is "
                            f"{potential_next_datetime})!\nIf you want to "
                            "ignore this, set IGNORE_TIMESTEP_OVERFLOW="
                            "True in qtrader/core/config.")
                sleep(sleep_time)  # TIME_STEP/1000.
                cur_datetime = datetime.now()

        for gateway_name in gateways:
            gateway = gateways[gateway_name]
            gateway.close()
        if "telegram" in plugins:
            telegram_bot = plugins["telegram"].bot
            telegram_bot.close()
        if "monitor" in plugins:
            proc_livemonitor.terminate()
            proc_livemonitor.wait()
        if "analysis" in plugins:
            freq = None
            if (self.end - self.start).total_seconds() > 3600 * 24:
                freq = "daily"
            plot_pnl = plugins["analysis"].plot_pnl
            for strategy_name, recorder in self.recorders.items():
                result_path = recorder.save_csv(
                    file_name=f"result_{strategy_name}")
                plot_pnl(result_path=result_path,
                         title=strategy_name,
                         freq=freq)

        engine.stop()
        engine.log.info(
            "Event-loop ends, and engine stops normally "
            "(other working threads will stop within 1 minute)."
        )


def get_latest_datetime(
        cur_data: Dict[str, Dict[Security, Bar]],
        gateway_names: List[str]
):
    """Find latest datetime for the snapshot"""
    # we don't expect any backtest period earlier than 1970-01-01
    latest_datetime = datetime(1970, 1, 1)
    if gateway_names is None:
        gateway_names = [gateway_name for gateway_name in cur_data]
    for gateway_name in cur_data:
        if gateway_name not in gateway_names:
            continue
        cur_gateway_data = cur_data[gateway_name]
        for security in cur_gateway_data:
            bar = cur_gateway_data[security]
            if bar.datetime > latest_datetime:
                latest_datetime = bar.datetime
    return latest_datetime


def parse_order_string_to_dict(
        order_string: str,
        engine: Engine
) -> Dict[str, Any]:
    """Tranform a string to a dictionary of order instructions"""
    (security_code, quantity, direction, offset, order_type, gateway_name,
        price, stop_price) = order_string.split(",")
    if gateway_name not in engine.gateways:
        return None
    found_security = False
    for security in engine.gateways[gateway_name].securities:
        if security.code == security_code:
            found_security = True
            break
    if not found_security:
        return None
    try:
        quantity = int(quantity)
    except ValueError:
        return None
    if direction == "l":
        direction = Direction.LONG
    elif direction == "s":
        direction = Direction.SHORT
    else:
        return None
    if offset == "o":
        offset = Offset.OPEN
    elif offset == "c":
        offset = Offset.CLOSE
    else:
        return None
    if order_type == "m":
        order_type = OrderType.MARKET
    elif order_type == "l":
        order_type = OrderType.LIMIT
    elif order_type == "s":
        order_type = OrderType.STOP
    else:
        return None
    if price == "None":
        price = None
    else:
        try:
            price = float(price)
        except ValueError:
            return None
    if stop_price == "None":
        stop_price = None
    else:
        try:
            stop_price = float(stop_price)
        except ValueError:
            return None
    return dict(
        security=security,
        quantity=quantity,
        direction=direction,
        offset=offset,
        order_type=order_type,
        gateway_name=gateway_name,
        price=price,
        stop_price=stop_price
    )


def telegrambot_control(engine: Engine):
    """Telegram Bot to control the engine"""
    plugins = engine.get_plugins()
    gateways = engine.gateways
    telegram_bot = plugins["telegram"].bot
    if telegram_bot.qtrader_status == "Terminated":
        for gateway_name in gateways:
            gateway = gateways[gateway_name]
            gateway.close()
        if "telegram" in plugins:
            telegram_bot.close()
        engine.stop()
        engine.log.info("Engine was stopped manually.")
        return
    if telegram_bot.get_balance:
        for gateway_name in gateways:
            balance = engine.get_balance(gateway_name=gateway_name)
            telegram_bot.send_message(f"{gateway_name}\n{balance}")
            telegram_bot.get_balance = False
    if telegram_bot.get_positions:
        for gateway_name in gateways:
            positions = engine.get_all_positions(gateway_name=gateway_name)
            telegram_bot.send_message(f"*{gateway_name}*\n{positions}")
            telegram_bot.get_positions = False
    if telegram_bot.get_orders:
        num_orders_displayed = telegram_bot.num_orders_displayed
        active_orders = telegram_bot.active_orders
        if active_orders:
            func = "get_all_active_orders"
        else:
            func = "get_all_orders"
        for gateway_name in gateways:
            orders = getattr(engine, func)(gateway_name=gateway_name)
            if len(orders) == 0:
                telegram_bot.send_message(f"{gateway_name}\nNo orders now.")
            else:
                telegram_bot.send_message(f"{gateway_name}\n")
                for order in reversed(orders[-num_orders_displayed:]):
                    telegram_bot.send_message(f"{order}")
            telegram_bot.get_orders = False
            telegram_bot.active_orders = False
            telegram_bot.num_orders_displayed = 1
    if telegram_bot.get_deals:
        num_deals_displayed = telegram_bot.num_deals_displayed
        for gateway_name in gateways:
            deals = engine.get_all_deals(gateway_name=gateway_name)
            if len(deals) == 0:
                telegram_bot.send_message(f"{gateway_name}\nNo deals now.")
            else:
                telegram_bot.send_message(f"{gateway_name}\n")
                for deal in reversed(deals[-num_deals_displayed:]):
                    telegram_bot.send_message(f"{deal}")
            telegram_bot.get_deals = False
            telegram_bot.num_deals_displayed = 1
    if telegram_bot.cancel_order:
        orderid = telegram_bot.cancel_order_id
        gateway_name = telegram_bot.gateway_name
        engine.cancel_order(orderid=orderid, gateway_name=gateway_name)
        telegram_bot.send_message(f"{gateway_name}: {orderid} is cancelled.")
        telegram_bot.cancel_order_id = None
        telegram_bot.cancel_order = False
    if telegram_bot.cancel_orders:
        for gateway_name in gateways:
            orders = engine.get_all_active_orders(gateway_name=gateway_name)
            for order in orders:
                engine.cancel_order(
                    orderid=order.orderid,
                    gateway_name=gateway_name)
        telegram_bot.send_message(
            f"{gateway_name}: All active orders are cancelled.")
        telegram_bot.cancel_orders = False
    if telegram_bot.send_order:
        order_dict = parse_order_string_to_dict(
            order_string=telegram_bot.order_string,
            engine=engine
        )
        if order_dict is None:
            telegram_bot.send_message("Order input is incorrect.")
        else:
            engine.send_order(**order_dict)
            telegram_bot.send_message("Order has been sent.")
        telegram_bot.send_order = False
        telegram_bot.order_string = ""
    if telegram_bot.close_positions:
        gateway_name = telegram_bot.close_positions_gateway_name
        if gateway_name is None:
            close_position_in_gateways = list(gateways.keys())
        elif gateway_name in gateways:
            close_position_in_gateways = [gateway_name]
        else:
            telegram_bot.send_message(
                f"Gateway name {gateway_name} was not found.")
            close_position_in_gateways = []
        for gateway_name in close_position_in_gateways:
            positions = engine.get_all_positions(gateway_name=gateway_name)
            for position in positions:
                if position.direction == Direction.LONG:
                    direction = Direction.SHORT
                elif position.direction == Direction.SHORT:
                    direction = Direction.LONG
                engine.send_order(
                    security=position.security,
                    quantity=position.quantity,
                    direction=direction,
                    offset=Offset.CLOSE,
                    order_type=OrderType.MARKET,
                    gateway_name=gateway_name
                )
        telegram_bot.send_message("Positions have been closed.")
        telegram_bot.close_positions = False
        telegram_bot.close_positions_gateway_name = None
