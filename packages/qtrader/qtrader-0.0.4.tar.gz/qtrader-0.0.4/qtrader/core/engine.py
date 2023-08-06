# -*- coding: utf-8 -*-
# @Time    : 7/3/2021 9:50 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: engine.py
# @Software: PyCharm

"""
Copyright (C) 2020 Joseph Chen - All Rights Reserved
You may use, distribute and modify this code under the
terms of the JXW license, which unfortunately won't be
written for another century.

You should have received a copy of the JXW license with
this file. If not, please write to: josephchenhk@gmail.com
"""

import importlib
from datetime import datetime, timedelta
from time import sleep
from typing import List, Union, Any, Dict
from threading import Thread

from qtrader.core.balance import AccountBalance
from qtrader.core.constants import (
    Direction,
    Offset,
    OrderType,
    TradeMode,
    OrderStatus
)
from qtrader.core.deal import Deal
from qtrader.core.order import Order
from qtrader.core.portfolio import Portfolio
from qtrader.core.position import PositionData, Position
from qtrader.core.security import Security
from qtrader.core.data import Bar, CapitalDistribution, OrderBook, Quote
from qtrader.core.data import _get_data
from qtrader.core.utility import safe_call
from qtrader.core.utility import try_parsing_datetime
from qtrader.core.utility import cast_value
from qtrader.core.logger import logger
from qtrader.config import DATA_MODEL, DATA_PATH
from qtrader.config import ACTIVATED_PLUGINS
from qtrader.gateways import BaseGateway, BacktestGateway

PERSIST_TIME_INTERVAL = 5
ACTIVE_ORDER_STATUS = [
    OrderStatus.SUBMITTING,
    OrderStatus.SUBMITTED,
    OrderStatus.PART_FILLED]


class Engine:
    """Execution engine"""

    strategies = {}

    def __init__(
            self,
            gateways: Dict[str, BaseGateway],
            init_cash: Dict[str, float] = None,
            init_position: Dict[str, Position] = None
    ):
        self.gateways = gateways
        self.log = logger
        self._status = "active"
        if init_cash is None:
            init_cash = {gw: 0.0 for gw in gateways}
        if init_position is None:
            init_position = {gw: Position() for gw in gateways}
        self.init_portfolio(
            init_cash=init_cash,
            init_position=init_position
        )
        self.plugins = dict()
        for plugin in ACTIVATED_PLUGINS:
            self.plugins[plugin] = importlib.import_module(
                f"qtrader.plugins.{plugin}")

        # Persistence in sqlite3
        if "sqlite3" in self.plugins:
            # Persistence only works in Simulate/Live environment; for speed
            # consideration, it will be ignored in Backtest mode (even if you
            # set it activated in config)
            self.gateways_persist = []  # gateways that need to do persistence
            for gateway_name in self.gateways:
                gateway = self.gateways[gateway_name]
                if (
                    gateway.trade_mode == TradeMode.SIMULATE
                    or gateway.trade_moe == TradeMode.LIVETRADE
                ):
                    self.gateways_persist.append(gateway_name)
            if len(self.gateways_persist) > 0:
                DB = getattr(self.plugins["sqlite3"], "DB")
                self.db = DB()
                # Create new thread to do persistence to sqlite3
                self.persist_active: bool = False
                self._persist_t: Thread = Thread(
                    target=persist_data,
                    args=(self,),
                    name="persist_thread"
                )

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val: str):
        self._status = val

    def start(self):
        """Start the engine before event loop starts"""
        if self.has_db():
            self.persist_active = True
            self._persist_t.start()
        self.log.info("Engine starts")

    def stop(self):
        """Stop engine after event loop OR manual stop"""
        if self.has_db():
            self.persist_active = False
            # wait for the persist thread stop
            sleep(PERSIST_TIME_INTERVAL + 2)
            self.db.close()
        self.status = "inactive"
        self.log.info("Engine stops")

    def init_portfolio(
            self,
            init_cash: Dict[str, float],
            init_position: Dict[str, Position]
    ):
        """Initialize portfolio of the engine (an engine may include different
        gateways)."""
        # Just initialize account_balance and position here, and they will be
        # synced with broker later.
        self.portfolios = {}
        for gateway_name in self.gateways:
            gateway = self.gateways[gateway_name]
            cash = init_cash[gateway_name]
            position = init_position[gateway_name]
            portfolio = Portfolio(
                account_balance=AccountBalance(cash=cash),  # account balance
                position=position,                          # position
                market=gateway                              # trading channel
            )
            self.portfolios[gateway_name] = portfolio

    def get_plugins(self) -> Dict[str, Any]:
        """Plugins that are activated"""
        return self.plugins

    def has_db(self) -> bool:
        """Whether db exists"""
        return hasattr(self, "db")

    def get_balance_id(
            self,
            gateway_name: str,
            strategy_account: str,
            strategy_version: str
    ) -> str:
        """Get balance_id from sqlite3, balance_id is strategy specific"""
        broker_name = self.gateways[gateway_name].broker_name
        broker_account = self.gateways[gateway_name].broker_account
        broker_environment = self.gateways[gateway_name].trade_mode.name
        balance_df = self.db.select_records(
            table_name="balance",
            broker_name=broker_name,
            broker_environment=broker_environment,
            broker_account=broker_account,
            strategy_account=strategy_account,
            strategy_version=strategy_version,
        )
        if balance_df.empty:
            self.log.info(
                f"get_balance_id({gateway_name}, {strategy_account}, "
                f"{strategy_version}): \nBalance id is not available in DB yet,"
                " need to sync balance first.")
            return None
        if balance_df.shape[0] != 1:
            self.log.info(
                f"get_balance_id({gateway_name}, {strategy_account}, "
                f"{strategy_version}): \nThere are more than 1 records in DB. "
                f"Check\n{balance_df}.")
            raise ValueError("balance_id is NOT unique in DB.")
        balance_id = balance_df["id"].values[0]
        return balance_id

    def get_db_order(
            self,
            balance_id: int,
            broker_order_id: str
    ) -> Order:
        """Get order record (if not record in db, return None)"""
        order_df = self.db.select_records(
            table_name="trading_order",
            balance_id=balance_id,
            broker_order_id=broker_order_id,
        )
        if order_df.empty:
            return None
        if order_df.shape[0] != 1:
            self.log.info(
                f"get_db_order({balance_id}, {broker_order_id}): \n"
                f"There are more than 1 records in DB. Check\n{order_df}."
            )
            raise ValueError("order is NOT unique in DB.")

        order = Order(
            security=Security(
                security_name=order_df["security_name"].values[0],
                code=order_df["security_code"].values[0]
            ),
            price=order_df["price"].values[0],
            quantity=order_df["quantity"].values[0],
            direction=convert_direction_db2qt(order_df["direction"].values[0]),
            offset=convert_offset_db2qt(order_df["offset"].values[0]),
            order_type=convert_order_type_db2qt(order_df["order_type"].values[0]),
            create_time=try_parsing_datetime(order_df["create_time"].values[0]),
            updated_time=try_parsing_datetime(order_df["update_time"].values[0]),
            filled_avg_price=order_df["filled_avg_price"].values[0],
            filled_quantity=order_df["filled_quantity"].values[0],
            status=convert_order_status_db2qt(order_df["status"].values[0]),
            orderid=order_df["broker_order_id"].values[0],
        )
        return order

    def get_db_deal(
            self,
            balance_id: int,
            broker_deal_id: str
    ) -> Deal:
        """Get deal record (if not record in db, return None)"""
        deal_df = self.db.select_records(
            table_name="trading_deal",
            balance_id=balance_id,
            broker_deal_id=broker_deal_id,
        )
        if deal_df.empty:
            return None
        if deal_df.shape[0] != 1:
            self.log.info(
                f"get_db_deal({balance_id}, {broker_deal_id}): \n"
                f"There are more than 1 records in DB. Check\n{deal_df}."
            )
            raise ValueError("deal is NOT unique in DB.")

        deal = Deal(
            security=Security(
                security_name=deal_df["security_name"].values[0],
                code=deal_df["security_code"].values[0]),
            direction=convert_direction_db2qt(
                deal_df["direction"].values[0]),
            offset=convert_offset_db2qt(
                deal_df["offset"].values[0]),
            order_type=convert_order_type_db2qt(
                deal_df["order_type"].values[0]),
            updated_time=try_parsing_datetime(
                deal_df["update_time"].values[0]),
            filled_avg_price=deal_df["filled_avg_price"].values[0],
            filled_quantity=deal_df["filled_quantity"].values[0],
            dealid=deal_df["broker_deal_id"].values[0],
            orderid=deal_df["broker_order_id"].values[0],
        )
        return deal

    def get_db_balance(
            self,
            gateway_name: str,
            strategy_account: str,
            strategy_version: str,
    ) -> AccountBalance:
        """Get balance info (if not record in db, return None)"""
        broker_name = self.gateways[gateway_name].broker_name
        broker_account = self.gateways[gateway_name].broker_account
        broker_environment = self.gateways[gateway_name].trade_mode.name
        balance_df = self.db.select_records(
            table_name="balance",
            broker_name=broker_name,
            broker_environment=broker_environment,
            broker_account=broker_account,
            strategy_account=strategy_account,
            strategy_version=strategy_version,
        )
        if balance_df.empty:
            return None
        if balance_df.shape[0] != 1:
            self.log.info(
                f"get_db_balance({gateway_name}, {strategy_account}, "
                f"{strategy_version}): \nThere are more than 1 records in DB. "
                f"Check\n{balance_df}.")
            raise ValueError("balance is NOT unique in DB.")

        account_balance = AccountBalance(
            cash=balance_df["cash"].values[0],
            available_cash=balance_df["available_cash"].values[0],
            cash_by_currency=balance_df["cash_by_currency"].values[0],
            max_power_short=balance_df["max_power_short"].values[0],
            net_cash_power=balance_df["net_cash_power"].values[0],
            maintenance_margin=balance_df["maintenance_margin"].values[0],
            unrealized_pnl=balance_df["unrealized_pnl"].values[0],
            realized_pnl=balance_df["realized_pnl"].values[0],
        )
        return account_balance

    def get_db_position(self, balance_id: int) -> Position:
        """Get position info (if not record in db, return None)"""
        position_df = self.db.select_records(
            table_name="position",
            balance_id=balance_id,
        )
        if position_df.empty:
            return None
        position = Position()
        for _, row in position_df.iterrows():
            security = Security(
                code=row["security_code"],
                security_name=row["security_name"]
            )
            direction = convert_direction_db2qt(row["direction"])
            position_data = PositionData(
                security=security,
                direction=direction,
                holding_price=row["holding_price"],
                quantity=row["quantity"],
                update_time=try_parsing_datetime(row["update_time"])
            )
            offset = Offset.OPEN
            position.update(position_data=position_data, offset=offset)
        return position

    def sync_broker_balance(self, gateway_name: str):
        """Synchronize balance with broker"""
        broker_name = self.gateways[gateway_name].broker_name
        broker_account = self.gateways[gateway_name].broker_account
        broker_environment = self.gateways[gateway_name].trade_mode.name
        broker_balance = self.get_broker_balance(gateway_name)
        if broker_balance is None:
            return
        self.portfolios[gateway_name].account_balance = broker_balance
        if not self.has_db():
            return
        # Process data in db
        balance_df = self.db.select_records(
            table_name="balance",
            broker_name=broker_name,
            broker_environment=broker_environment,
            broker_account=broker_account,
        )
        if balance_df.empty:
            account_ids = self.db.select_records(
                table_name="balance",
                columns=[
                    "broker_account_id",
                    "strategy_account_id",
                    "strategy_account"]
            )
            if account_ids.empty:
                broker_account_id = 1
                strategy_account_id = 1
            else:
                broker_account_id = max(account_ids["broker_account_id"]) + 1
                strategy_account_id = max(account_ids["strategy_account_id"])

            # (1) Create balance for the different strategies
            all_cash = 0
            all_available_cash = 0
            for strategy_name, strategy in self.strategies.items():
                strategy_account_id += 1
                account = strategy.portfolios[gateway_name].account_balance
                all_cash += account.cash
                all_available_cash += account.available_cash
                self.db.insert_records(
                    table_name="balance",
                    broker_name=broker_name,
                    broker_environment=broker_environment,
                    broker_account_id=broker_account_id,      # same broker_account_id
                    broker_account=broker_account,
                    strategy_account_id=strategy_account_id,  # different strategy_account_id
                    strategy_account=strategy.strategy_account,
                    strategy_version=strategy.strategy_version,
                    strategy_version_desc="",
                    strategy_status="active",
                    cash=account.cash,
                    available_cash=account.available_cash,
                    max_power_short=cast_value(
                        value=account.max_power_short,
                        if_=None,
                        then=broker_balance.max_power_short),
                    net_cash_power=cast_value(
                        value=account.net_cash_power,
                        if_=None,
                        then=broker_balance.net_cash_power),
                    update_time=datetime.now(),
                    remark=""
                )

            # (2) Create a default strategy account to absorb all remaining cash
            default_account = account_ids[
                (account_ids.strategy_account == "default")
                & (account_ids.broker_account_id == broker_account_id)
            ]
            if default_account.empty:
                strategy_account_id = 1
            else:
                strategy_account_id = default_account["strategy_account_id"].values[0]
            remaining_cash = broker_balance.cash - all_cash
            remaining_available_cash = (
                broker_balance.available_cash
                - all_available_cash
            )
            self.db.insert_records(
                table_name="balance",
                broker_name=broker_name,
                broker_environment=broker_environment,
                broker_account_id=broker_account_id,
                broker_account=broker_account,
                strategy_account_id=strategy_account_id,
                strategy_account="default",
                strategy_version="1.0",
                strategy_version_desc="manual trading",
                strategy_status="active",
                cash=remaining_cash,
                available_cash=remaining_available_cash,
                max_power_short=-1,
                net_cash_power=-1,
                update_time=datetime.now(),
                remark=""
            )
        else:
            # (1) Update strategies
            all_cash = 0
            all_available_cash = 0
            for strategy_name, strategy in self.strategies.items():
                id_ = balance_df[balance_df["strategy_account"]
                                 == strategy.strategy_account]["id"].values[0]
                account = strategy.portfolios[gateway_name].account_balance
                all_cash += account.cash
                all_available_cash += account.available_cash
                strategy_cash_db = (
                    balance_df[balance_df.id == id_]["cash"].values[0]
                )
                strategy_available_cash_db = (
                    balance_df[balance_df.id == id_]["available_cash"].values[0]
                )
                if account.cash != strategy_cash_db:
                    self.db.update_records(
                        table_name="balance",
                        columns={"cash": account.cash},
                        id=id_)
                if account.available_cash != strategy_available_cash_db:
                    self.db.update_records(
                        table_name="balance",
                        columns={"available_cash": account.available_cash},
                        id=id_)
            # (2) Update default strategy
            remaining_cash = broker_balance.cash - all_cash
            remaining_available_cash = (
                broker_balance.available_cash
                - all_available_cash
            )
            id_ = balance_df[balance_df["strategy_account"]
                             == "default"]["id"].values[0]
            strategy_cash_db = (
                balance_df[balance_df.id == id_]["cash"].values[0]
            )
            strategy_available_cash_db = (
                balance_df[balance_df.id == id_]["available_cash"].values[0]
            )
            if remaining_cash != strategy_cash_db:
                self.db.update_records(
                    table_name="balance",
                    columns={"cash": remaining_cash},
                    id=id_
                )
            if remaining_available_cash != strategy_available_cash_db:
                self.db.update_records(
                    table_name="balance",
                    columns={"available_cash": remaining_available_cash},
                    id=id_
                )

    def sync_broker_position(self, gateway_name: str):
        """Synchronize position with broker"""
        broker_name = self.gateways[gateway_name].broker_name
        broker_account = self.gateways[gateway_name].broker_account
        broker_environment = self.gateways[gateway_name].trade_mode.name
        all_broker_positions = self.get_all_broker_positions(gateway_name)
        if all_broker_positions is None:
            return
        if len(all_broker_positions) == 0:
            return

        # Synchronize broker positions to engine
        for broker_position in all_broker_positions:
            # For positions opened and closed in the same day, the quantity will
            # be zero, so we just skip this position record
            if broker_position.quantity == 0:
                continue
            self.portfolios[gateway_name].position.update(
                position_data=broker_position,
                offset=Offset.OPEN
            )

        if not self.has_db():
            return

        # process data in db
        balance_df = self.db.select_records(
            table_name="balance",
            broker_name=broker_name,
            broker_environment=broker_environment,
            broker_account=broker_account,
        )
        assert not balance_df.empty, (
            "balance should not be empty, as it should have already been "
            "inserted in sync_broker_balance, please check "
            f"broker_name={broker_name}, "
            f"broker_environment={broker_environment}, "
            f"broker_account={broker_account}"
        )

        for strategy_name, strategy in self.strategies.items():
            strat_balance_id = balance_df[
                (balance_df["strategy_account"] == strategy.strategy_account)
                & (balance_df["strategy_version"] == strategy.strategy_version)
            ]["id"].values[0]
            position_df = self.db.select_records(
                table_name="position",
                balance_id=strat_balance_id
            )

            for position_data in strategy.portfolios[gateway_name].position.get_all_positions(
            ):
                # Deduce the portion of positions from strategy
                for broker_position in all_broker_positions:
                    if (
                        broker_position.security == position_data.security
                        and broker_position.direction == position_data.direction
                    ):
                        broker_position.quantity -= position_data.quantity
                        break

                # Insert or update position data to DB
                position_data_db = position_df[
                    (position_df.security_name == position_data.security.security_name)
                    and (position_df.security_code == position_data.security.security_code)
                    and (position_df.direction == position_data.direction.name)
                ]
                if position_data_db.empty:
                    self.db.insert_records(
                        table_name="position",
                        balance_id=strat_balance_id,
                        security_name=position_data.security.security_name,
                        security_code=position_data.security.code,
                        direction=position_data.direction.name,
                        holding_price=position_data.holding_price,
                        quantity=position_data.quantity,
                        update_time=position_data.update_time
                    )
                elif position_data_db["quantity"].values[0] != position_data.quantity:
                    self.db.update_records(
                        table_name="position",
                        columns={
                            "quantity": position_data.quantity,
                            "holding_price": position_data.holding_price,
                            "update_time": position_data.update_time
                        },
                        balance_id=strat_balance_id,
                        security_name=position_data.security.security_name,
                        security_code=position_data.security.code,
                        direction=position_data.direction.name
                    )

            # Remaining positions will be attributed to default strategy
            # account
            default_balance_id = (
                balance_df[
                    (balance_df["strategy_account"] == "default")
                    & (balance_df["strategy_version"] == "1.0")
                ]["id"].values[0]
            )
            for broker_position in all_broker_positions:
                position_df = self.db.select_records(
                    table_name="position",
                    balance_id=default_balance_id,
                    security_name=broker_position.security.security_name,
                    security_code=broker_position.security.code,
                    direction=broker_position.direction.name
                )
                if broker_position.quantity == 0:
                    continue
                if broker_position.quantity < 0:
                    broker_position.quantity = abs(broker_position.quantity)
                    broker_position.direction = (
                        Direction.LONG
                        if broker_position.direction == Direction.SHORT
                        else Direction.SHORT)

                if position_df.empty:
                    self.db.insert_records(
                        table_name="position",
                        balance_id=default_balance_id,
                        security_name=broker_position.security.security_name,
                        security_code=broker_position.security.code,
                        direction=broker_position.direction.name,
                        holding_price=broker_position.holding_price,
                        quantity=broker_position.quantity,
                        update_time=broker_position.update_time
                    )
                else:
                    self.db.update_records(
                        table_name="position",
                        columns={
                            "quantity": broker_position.quantity,
                            "holding_price": broker_position.holding_price,
                            "update_time": broker_position.update_time
                        },
                        balance_id=default_balance_id,
                        security_name=broker_position.security.security_name,
                        security_code=broker_position.security.code,
                        direction=broker_position.direction.name
                    )

    def send_order(
            self,
            security: Security,
            quantity: float,
            direction: Direction,
            offset: Offset,
            order_type: OrderType,
            gateway_name: str,
            price: float = None,
            stop_price: float = None
    ) -> str:
        """Send order to gateway"""
        create_time = self.gateways[gateway_name].market_datetime
        order = Order(
            security=security,
            price=price,
            stop_price=stop_price,
            quantity=quantity,
            direction=direction,
            offset=offset,
            order_type=order_type,
            create_time=create_time
        )
        orderid = self.gateways[gateway_name].place_order(order)
        return orderid

    @safe_call
    def cancel_order(self, orderid: str, gateway_name: str):
        """Cancel order (no wait)"""
        self.gateways[gateway_name].cancel_order(orderid)

    def get_order(self, orderid: str, gateway_name: str) -> Order:
        """Get order"""
        return self.gateways[gateway_name].get_order(orderid)

    def get_recent_data(
            self,
            security: Security,
            cur_datetime: datetime = datetime.now(),
            *,
            gateway_name: str,
            **kwargs,
    ) -> Union[Bar, List[Bar]]:
        """
        Get recent data (OHLCV or CapitalDistribution)

        sample of kwargs:
            dfield="kline"
            dfield="capdist"
        """
        return self.gateways[gateway_name].get_recent_data(
            security,
            cur_datetime, **kwargs
        )

    def get_history_data(
            self,
            security: Security,
            start: datetime,
            end: datetime,
            *,
            gateway_name: str,
            **kwargs,
    ) -> Union[Dict[str, List[Any]], Bar, CapitalDistribution]:
        """
        Get historical data (OHLCV or CapitalDistribution)

        sample of kwargs:
            dfield="kline"
            dfield="capdist"
        """
        if kwargs:
            assert "dfield" in kwargs, (
                f"`dfield` should be passed in as kwargs, but kwargs={kwargs}"
            )
            dfields = [kwargs["dfield"]]
        else:
            dfields = DATA_PATH
        data = dict()
        for dfield in dfields:
            if "dtype" in kwargs:
                data[dfield] = self.get_history_data_by_dfield(
                    security=security,
                    start=start,
                    end=end,
                    dfield=dfield,
                    dtype=kwargs["dtype"],
                    gateway_name=gateway_name,
                    **kwargs
                )
            else:
                data[dfield] = self.get_history_data_by_dfield(
                    security=security,
                    start=start,
                    end=end,
                    dfield=dfield,
                    gateway_name=gateway_name,
                    **kwargs
                )
        if len(dfields) == 1:
            return data[dfield]
        return data

    def get_history_data_by_dfield(
            self,
            security: Security,
            start: datetime,
            end: datetime,
            dfield: str,
            dtype: List[str] = None,
            gateway_name: str = None,
            **kwargs
    ) -> List[Any]:
        """
        Get historical data (explicitly specified dfield)

        sample of kwargs:
            dfield="kline"
            dfield="capdist"
        """
        if dtype is None:
            dtype = self.gateways[gateway_name].DTYPES.get(dfield)
        if dfield == "kline":
            interval = kwargs.get("interval")
            assert interval is not None, (
                "'interval' must be passed in if dfield='kline'."
            )
        df = _get_data(
            security=security,
            start=start,
            end=end,
            dfield=dfield,
            dtype=dtype,
            **kwargs
        )
        if dtype is None:
            time_cols = [c for c in df.columns if "time" in c or "Time" in c]
            assert len(time_cols) == 1, (
                "There should be one column related to `*time*`, but we got "
                f"{df.columns}"
            )
            time_col = time_cols[0]
        else:
            assert "time" in dtype[0] or "Time" in dtype[0], (
                "The first column in dtype should be related to `*time*`, but "
                f"we got {dtype[0]}"
            )
            time_col = dtype[0]
        data_cols = (
            [col for col in df.columns if col != time_col]
        )  # other than time_col
        data_cls = getattr(importlib.import_module(
            "qtrader.core.data"), DATA_MODEL[dfield])
        datas = []
        for _, row in df.iterrows():
            cur_time = datetime.strptime(row[time_col], "%Y-%m-%d %H:%M:%S")
            kwargs = {"datetime": cur_time, "security": security}
            for col in data_cols:
                kwargs[col] = row[col]
            data = data_cls(**kwargs)
            datas.append(data)
        return datas

    def find_deals_with_orderid(
            self,
            orderid: str,
            gateway_name: str
    ) -> List[Deal]:
        """Find the deal with orderid"""
        return self.gateways[gateway_name].find_deals_with_orderid(orderid)

    def get_balance(self, gateway_name: str) -> AccountBalance:
        """Get balance"""
        return self.portfolios[gateway_name].account_balance

    def get_broker_balance(self, gateway_name: str) -> AccountBalance:
        """Get broker balance"""
        return self.gateways[gateway_name].get_broker_balance()

    def get_position(
            self,
            security: Security,
            direction: Direction,
            gateway_name: str
    ) -> PositionData:
        """Get position"""
        return self.portfolios[gateway_name].position.get_position(
            security,
            direction
        )

    def get_broker_position(
            self,
            security: Security,
            direction: Direction,
            gateway_name: str
    ) -> PositionData:
        """Get broker position"""
        return self.gateways[gateway_name].get_broker_position(
            security,
            direction
        )

    def get_all_positions(self, gateway_name: str) -> List[PositionData]:
        """Get all positions in the specified gateway"""
        return self.portfolios[gateway_name].position.get_all_positions()

    def get_all_broker_positions(
            self, gateway_name: str) -> List[PositionData]:
        """Get all broker positions in the specified gateway"""
        return self.gateways[gateway_name].get_all_broker_positions()

    def get_all_orders(self, gateway_name: str) -> List[Order]:
        """Get all orders in the specified gateway"""
        return self.gateways[gateway_name].get_all_orders()

    def get_all_active_orders(self, gateway_name: str) -> List[Order]:
        """Get all active orders in the specified gateway"""
        orders = self.get_all_orders(gateway_name)
        active_orders = [o for o in orders if o.status in ACTIVE_ORDER_STATUS]
        return active_orders

    def get_all_deals(self, gateway_name: str) -> List[Deal]:
        """Get all deals in the specified gateway"""
        return self.gateways[gateway_name].get_all_deals()

    def get_quote(self, security: Security, gateway_name: str) -> Quote:
        """Get quote (in Backtest mode return None)"""
        return self.gateways[gateway_name].get_quote(security)

    def get_orderbook(
            self,
            security: Security,
            gateway_name: str
    ) -> OrderBook:
        """Get orderbook (in Backtest mode return None)"""
        return self.gateways[gateway_name].get_orderbook(security)

    def get_capital_distribution(
            self,
            security: Security,
            gateway_name: str
    ) -> CapitalDistribution:
        """Get capital distribution"""
        return self.gateways[gateway_name].get_capital_distribution(security)

    def req_historical_bars(
            self,
            security: Security,
            gateway_name: str,
            periods: int,
            freq: str,
            cur_datetime: datetime = None,
            trading_sessions: List[datetime] = None,
            mode: str = "direct"
    ) -> List[Bar]:
        """Request historical bar data"""
        gateway = self.gateways.get(gateway_name)
        if gateway:
            return gateway.req_historical_bars(
                security,
                periods,
                freq,
                cur_datetime,
                trading_sessions=trading_sessions,
                mode=mode
            )
        elif gateway_name == "Backtest":
            use_gateway = self.gateways.get(list(self.gateways.keys())[0])
            if freq == "1Day":
                num_days = periods + 14
            else:
                num_days = 14
            start = use_gateway.end - timedelta(days=num_days)
            if hasattr(use_gateway, "num_of_1min_bar"):
                num_of_1min_bar = getattr(use_gateway, "num_of_1min_bar")
            else:
                num_of_1min_bar = None
            gateway = BacktestGateway(
                securities=use_gateway.securities,
                start=start,
                end=use_gateway.end,
                gateway_name=gateway_name,
                fees=use_gateway.fees,
                num_of_1min_bar=num_of_1min_bar
            )
            return gateway.req_historical_bars(
                security,
                periods,
                freq,
                cur_datetime,
                trading_sessions=trading_sessions,
                mode=mode
            )
        raise ValueError(f"Gateway {gateway_name} was not found.")


def convert_direction_db2qt(direction: str) -> Direction:
    """Convert direction from string(in DB) to qtrader Direction"""
    if direction == "LONG":
        return Direction.LONG
    elif direction == "SHORT":
        return Direction.SHORT
    elif direction == "NET":
        return Direction.NET
    else:
        raise ValueError(f"Direction {direction} in database is invalid!")


def convert_offset_db2qt(offset: str) -> Offset:
    """Convert offset from string (in DB) to qtrader Offset"""
    if offset == "NONE":
        return Offset.NONE
    elif offset == "OPEN":
        return Offset.OPEN
    elif offset == "CLOSE":
        return Offset.CLOSE
    elif offset == "CLOSETODAY":
        return Offset.CLOSETODAY
    elif offset == "CLOSEYESTERDAY":
        return Offset.CLOSEYESTERDAY
    else:
        raise ValueError(f"Offset {offset} in database is invalid!")


def convert_order_type_db2qt(order_type: str) -> OrderType:
    """Convert order_type from string to qtrader OrderType"""
    if order_type == "LIMIT":
        return OrderType.LIMIT
    elif order_type == "MARKET":
        return OrderType.MARKET
    elif order_type == "STOP":
        return OrderType.STOP
    elif order_type == "FAK":
        return OrderType.FAK
    elif order_type == "FOK":
        return OrderType.FOK
    else:
        raise ValueError(f"Order Type {order_type} in database is invalid!")


def convert_order_status_db2qt(order_status: str) -> OrderStatus:
    """Convert order_status from string (in DB) to qtrader OrderStatus"""
    if order_status == "UNKNOWN":
        return OrderStatus.UNKNOWN
    elif order_status == "SUBMITTED":
        return OrderStatus.SUBMITTED
    elif order_status == "FILLED":
        return OrderStatus.FILLED
    elif order_status == "PART_FILLED":
        return OrderStatus.PART_FILLED
    elif order_status == "CANCELLED":
        return OrderStatus.CANCELLED
    elif order_status == "FAILED":
        return OrderStatus.FAILED
    else:
        raise ValueError(
            f"Order Status {order_status} in database is invalid!")


def persist_data(engine, time_interval=PERSIST_TIME_INTERVAL):
    """Persist data to DB"""
    # db connection is in main thread
    db_main = engine.db
    # Establish a new thread to process the persistence
    DB = getattr(engine.plugins["sqlite3"], "DB")
    setattr(engine, "db", DB())
    # Do persistence as long as it is active
    while engine.persist_active:
        persist_account_balance(engine)
        engine.log.info("[Account balance] is persisted")
        persist_position(engine)
        engine.log.info("[Position] is persisted")
        persist_order(engine)
        engine.log.info("[Order] is persisted")
        persist_deal(engine)
        engine.log.info("[Deal] is persisted")
        sleep(time_interval)
    engine.db.close()
    # Put the db connection in main thread
    setattr(engine, "db", db_main)
    engine.log.info("Gracefully stop persisting data.")


def persist_account_balance(engine):
    """Persist account balance"""
    # Loop over gateways
    for gateway_name in engine.gateways_persist:
        # Loop over strategies
        for strategy_name, strategy in engine.strategies.items():
            db_balance = engine.get_db_balance(
                gateway_name=gateway_name,
                strategy_account=strategy.strategy_account,
                strategy_version=strategy.strategy_version,
            )
            if db_balance is None:
                engine.log.info(
                    "[persist_account_balance] Account Balance is not available"
                    " in the DB yet, need to sync balance first.")
                return

            fields = ("cash",
                      "available_cash",
                      "max_power_short",
                      "net_cash_power")
            updates = dict()
            for field in fields:
                db_field = getattr(db_balance, field)
                mem_field = getattr(
                    strategy.portfolios[gateway_name].account_balance, field)
                if mem_field != db_field:
                    updates[field] = mem_field

            if updates:
                engine.db.update_records(
                    table_name="balance",
                    columns=updates,
                    strategy_account=strategy.strategy_account,
                    strategy_version=strategy.strategy_version,
                )


def persist_position(engine):
    """Persist position"""
    # Loop over gateways
    for gateway_name in engine.gateways_persist:
        # Loop over strategies
        for strategy_name, strategy in engine.strategies.items():
            strategy_position = strategy.portfolios[gateway_name].position
            strategy_positions = strategy_position.get_all_positions()
            balance_id = engine.get_balance_id(
                gateway_name=gateway_name,
                strategy_account=strategy.strategy_account,
                strategy_version=strategy.strategy_version
            )
            db_position = engine.get_db_position(balance_id=balance_id)

            if db_position is None:
                for position_data in strategy_positions:
                    engine.db.insert_records(
                        table_name="position",
                        balance_id=balance_id,
                        security_name=position_data.security.security_name,
                        security_code=position_data.security.code,
                        direction=position_data.direction.name,
                        holding_price=position_data.holding_price,
                        quantity=position_data.quantity,
                        update_time=position_data.update_time
                    )
            else:
                # Delete records in DB if it can not be found in Memory, as it
                # has been closed out.
                for db_position_data in db_position.get_all_positions():
                    strategy_position_data = strategy.portfolios[gateway_name].position.get_position(
                        security=db_position_data.security, direction=db_position_data.direction, )
                    if strategy_position_data is None:
                        engine.db.delete_records(
                            table_name="position",
                            balance_id=balance_id,
                            security_name=db_position_data.security.security_name,
                            security_code=db_position_data.security.code,
                            direction=db_position_data.direction.name,
                        )
                # Now records in DB is a subset of data in Memory; we update DB based on records
                # in Memory
                for position_data in strategy_positions:
                    db_position_data = db_position.get_position(
                        security=position_data.security,
                        direction=position_data.direction
                    )
                    if db_position_data is None:
                        engine.db.insert_records(
                            table_name="position",
                            balance_id=balance_id,
                            security_name=position_data.security.security_name,
                            security_code=position_data.security.code,
                            direction=position_data.direction.name,
                            holding_price=position_data.holding_price,
                            quantity=position_data.quantity,
                            update_time=position_data.update_time
                        )
                    elif position_data.quantity != db_position_data.quantity:
                        engine.db.update_records(
                            table_name="position",
                            columns=dict(
                                holding_price=position_data.holding_price,
                                quantity=position_data.quantity,
                                update_time=position_data.update_time
                            ),
                            balance_id=balance_id,
                            security_name=position_data.security.security_name,
                            security_code=position_data.security.code,
                            direction=position_data.direction.name,
                        )


def persist_order(engine):
    """Persist order"""
    # Loop over gateways
    for gateway_name in engine.gateways_persist:
        # Loop over strategies
        for strategy_name, strategy in engine.strategies.items():
            balance_id = engine.get_balance_id(
                gateway_name=gateway_name,
                strategy_account=strategy.strategy_account,
                strategy_version=strategy.strategy_version
            )
            orders = engine.get_all_orders(gateway_name=gateway_name)
            engine.log.info(orders)
            for order in orders:
                db_order = engine.get_db_order(
                    balance_id=balance_id, broker_order_id=order.orderid)
                if db_order is None:
                    engine.db.insert_records(
                        table_name="trading_order",
                        broker_order_id=order.orderid,
                        balance_id=balance_id,
                        security_name=order.security.security_name,
                        security_code=order.security.code,
                        price=order.price,
                        quantity=order.quantity,
                        direction=order.direction.name,
                        offset=order.offset.name,
                        order_type=order.order_type.name,
                        create_time=order.create_time,
                        update_time=order.updated_time,
                        filled_avg_price=order.filled_avg_price,
                        filled_quantity=order.filled_quantity,
                        status=order.status.name,
                        remark="",
                    )
                elif order.status != db_order.status:
                    engine.db.update_records(
                        table_name="trading_order",
                        columns=dict(
                            update_time=order.updated_time,
                            filled_avg_price=order.filled_avg_price,
                            filled_quantity=order.filled_quantity,
                            status=order.status.name,
                        ),
                        balance_id=balance_id,
                        broker_order_id=order.orderid
                    )


def persist_deal(engine):
    """Persist deal"""
    # Loop over gateways
    for gateway_name in engine.gateways_persist:
        # Loop over strategies
        for strategy_name, strategy in engine.strategies.items():
            balance_id = engine.get_balance_id(
                gateway_name=gateway_name,
                strategy_account=strategy.strategy_account,
                strategy_version=strategy.strategy_version
            )
            deals = engine.get_all_deals(gateway_name=gateway_name)
            engine.log.info(deals)
            for deal in deals:
                db_deal = engine.get_db_deal(
                    balance_id=balance_id, broker_deal_id=deal.dealid)
                if db_deal is None:
                    # order was synced before deal, therefore we must be able to
                    # locate the order here
                    order_df = engine.db.select_records(
                        table_name="trading_order",
                        balance_id=balance_id,
                        broker_order_id=deal.orderid,
                    )
                    assert not order_df.empty, (
                        "Records not found in order table. Check balance_id="
                        f"{balance_id}, broker_order_id={deal.orderid}."
                    )
                    assert order_df.shape[0] == 1, (
                        "More than 1 records were found in order table. Check "
                        f"balance_id={balance_id},broker_order_id={deal.orderid}"
                    )
                    order_id = order_df["id"].values[0]
                    engine.db.insert_records(
                        table_name="trading_deal",
                        broker_deal_id=deal.dealid,
                        broker_order_id=deal.orderid,
                        order_id=order_id,
                        balance_id=balance_id,
                        security_name=deal.security.security_name,
                        security_code=deal.security.code,
                        direction=deal.direction.name,
                        offset=deal.offset.name,
                        order_type=deal.order_type.name,
                        update_time=deal.updated_time,
                        filled_avg_price=deal.filled_avg_price,
                        filled_quantity=deal.filled_quantity,
                        remark="",
                    )
