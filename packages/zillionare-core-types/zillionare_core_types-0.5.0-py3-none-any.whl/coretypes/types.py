"""Top-level package for zillionare core types."""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from enum import Enum
from typing import Union

import numpy as np
from numpy.typing import NDArray

Frame = Union[datetime.date, datetime.datetime]
"""包含日期date和时间datetime的联合类型"""


class FrameType(Enum):
    """对证券交易中K线周期的封装。提供了以下对应周期:

    |     周期    | 字符串 | 类型                 | 数值 |
    | --------- | --- | ------------------ | -- |
    |     年线    | 1Y  | FrameType.YEAR     | 10 |
    |     季线    | 1Q  | FrameType.QUARTER |  9  |
    |     月线    | 1M  | FrameType.MONTH    | 8  |
    |     周线    | 1W  | FrameType.WEEK     | 7  |
    |     日线    | 1D  | FrameType.DAY      | 6  |
    |     60分钟线 | 60m | FrameType.MIN60    | 5  |
    |     30分钟线 | 30m | FrameType.MIN30    | 4  |
    |     15分钟线 | 15m | FrameType.MIN15    | 3  |
    |     5分钟线  | 5m  | FrameType.MIN5     | 2  |
    |     分钟线   | 1m  | FrameType.MIN1     |  1 |

    """

    DAY = "1d"
    MIN60 = "60m"
    MIN30 = "30m"
    MIN15 = "15m"
    MIN5 = "5m"
    MIN1 = "1m"
    WEEK = "1w"
    MONTH = "1M"
    QUARTER = "1Q"
    YEAR = "1Y"

    def to_int(self) -> int:
        """转换为整数表示，用于串行化"""
        mapping = {
            FrameType.MIN1: 1,
            FrameType.MIN5: 2,
            FrameType.MIN15: 3,
            FrameType.MIN30: 4,
            FrameType.MIN60: 5,
            FrameType.DAY: 6,
            FrameType.WEEK: 7,
            FrameType.MONTH: 8,
            FrameType.QUARTER: 9,
            FrameType.YEAR: 10,
        }
        return mapping[self]

    @staticmethod
    def from_int(frame_type: int) -> "FrameType":
        """将整数表示的`frame_type`转换为`FrameType`类型"""
        mapping = {
            1: FrameType.MIN1,
            2: FrameType.MIN5,
            3: FrameType.MIN15,
            4: FrameType.MIN30,
            5: FrameType.MIN60,
            6: FrameType.DAY,
            7: FrameType.WEEK,
            8: FrameType.MONTH,
            9: FrameType.QUARTER,
            10: FrameType.YEAR,
        }

        return mapping[frame_type]

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.to_int() < other.to_int()
        return NotImplemented

    def __le__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self.to_int() <= other.to_int()

        return NotImplemented

    def __ge__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self.to_int() >= other.to_int()

        return NotImplemented

    def __gt__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self.to_int() > other.to_int()

        return NotImplemented


class SecurityType(Enum):
    """支持的证券品种类型定义

    |     类型                   | 值         | 说明    |
    | ------------------------ | --------- | ----- |
    |     SecurityType.STOCK   | stock     | 股票类型  |
    |     SecurityType.INDEX   | index     | 指数类型  |
    |     SecurityType.ETF     | etf       | ETF基金 |
    |     SecurityType.FUND    | fund      | 基金    |
    |     SecurityType.LOF     | lof，LOF基金 |       |
    |     SecurityType.FJA     | fja       | 分级A基金 |
    |     SecurityType.FJB     | fjb       | 分级B基金 |
    |     SecurityType.BOND    | bond      | 债券基金  |
    |     SecurityType.STOCK_B | stock_b   | B股    |
    |     SecurityType.UNKNOWN | unknown   | 未知品种  |
    """

    STOCK = "stock"
    INDEX = "index"
    ETF = "etf"
    FUND = "fund"
    LOF = "lof"
    FJA = "fja"
    FJB = "fjb"
    FUTURES = "futures"
    BOND = "bond"
    STOCK_B = "stock_b"
    UNKNOWN = "unknown"


class MarketType(Enum):
    """市场类型。当前支持的类型为上交所`XSHG`和`XSHE`"""

    XSHG = "XSHG"
    XSHE = "XSHE"


bars_dtype = np.dtype(
    [
        # use datetime64 may improve performance/memory usage, but it's hard to talk with other modules, like TimeFrame
        ("frame", "datetime64[s]"),
        ("open", "f4"),
        ("high", "f4"),
        ("low", "f4"),
        ("close", "f4"),
        ("volume", "f8"),
        ("amount", "f8"),
        ("factor", "f4"),
    ]
)
"""行情数据元类型"""

bars_dtype_with_code = np.dtype(
    [
        ("code", "O"),
        # use datetime64 may improve performance/memory usage, but it's hard to talk with other modules, like TimeFrame
        ("frame", "datetime64[s]"),
        ("open", "f4"),
        ("high", "f4"),
        ("low", "f4"),
        ("close", "f4"),
        ("volume", "f8"),
        ("amount", "f8"),
        ("factor", "f4"),
    ]
)
"""带证券代码的行情数据元类型"""

bars_cols = list(bars_dtype.names)
"""行情数据列名数组，即[frame, open, high, low, close, volume, amount, factor]"""

fields = bars_dtype.descr.copy()
fields.extend([("high_limit", "f4"), ("low_limit", "f4")])

bars_with_limit_dtype = np.dtype(fields)
"""带涨跌停价格的行情数据元类型，包含frame, open, high, low, close, volume, amount, factort high_limit, low_limit"""

bars_with_limit_cols = list(bars_with_limit_dtype.names)
"""带涨跌停价的行情数据列名数组，即[frame, open, high, low, close, volume, amount, factort high_limit, low_limit]"""

BarsArray = NDArray[bars_dtype]
"""行情数据(包含列frame, open, high, low, close, volume, amount, factor)数组"""

BarsWithLimitArray = NDArray[bars_with_limit_dtype]
"""带涨跌停价(high_limit, low_limit)的行情数据数组"""

BarsPanel = NDArray[bars_dtype_with_code]
"""带证券代码的行情数据数组"""

security_db_dtype = [("frame", "O"), ("code", "U16"), ("info", "O")]

security_info_dtype = [
    ("code", "O"),
    ("alias", "O"),
    ("name", "O"),
    ("ipo", "datetime64[s]"),
    ("end", "datetime64[s]"),
    ("type", "O"),
]

xrxd_info_dtype = [
    ("code", "O"),
    ("a_xr_date", "datetime64[s]"),
    ("bonusnote1", "O"),
    ("bonus_ratio", "<f4"),
    ("dividend_ratio", "<f4"),
    ("transfer_ratio", "<f4"),
    ("at_bonus_ratio", "<f4"),
    ("report_date", "datetime64[s]"),
    ("plan_progress", "O"),
    ("bonusnote2", "O"),
    ("bonus_cancel_pub_date", "datetime64[s]"),
]

__all__ = [
    "Frame",
    "FrameType",
    "SecurityType",
    "MarketType",
    "bars_dtype",
    "bars_dtype_with_code",
    "bars_cols",
    "bars_with_limit_dtype",
    "bars_with_limit_cols",
    "BarsArray",
    "BarsWithLimitArray",
    "BarsPanel",
    "security_db_dtype",
    "security_info_dtype",
    "xrxd_info_dtype",
]
