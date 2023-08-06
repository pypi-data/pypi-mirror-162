import re
import numpy as np
import logging
from enum import Enum
from typing import Any


class INumericExpr:
    def roll(self) -> int:
        '''Return the parsed final value of the expression'''
        raise(Exception('Not implemented'))


class DiceRollMode(Enum):
    SUM = ''
    MAX = 'h'
    MIN = 'l'
    ALL = 'a'


class DiceExpr(INumericExpr):
    _regex_dice: str = r'(\d*)d([0-9f]+)'
    _regex_mode: str = r'(k[hla])?'
    _regex: str = _regex_dice + _regex_mode
    MAX_NUMBER: int = 999

    _valid: bool = True
    dice_num: int = 0
    sides: str = ''
    isides: int = -1
    is_fudge: bool = False
    roll_mode: DiceRollMode = DiceRollMode.SUM

    def __init__(self, expr):
        self.expr = expr.lower()
        dice_raw = re.search(DiceExpr._regex, self.expr)
        if dice_raw is None:
            self._valid = False
            return

        self.dice_num = int(dice_raw.group(1)) if dice_raw.group(1) else 1
        if self.dice_num > DiceExpr.MAX_NUMBER:
            self.dice_num = DiceExpr.MAX_NUMBER

        self.sides = str(dice_raw.group(2)) if dice_raw.group(2) else ''
        if not self.sides:
            self._valid = False
            return

        mode = dice_raw.group(3)
        if mode is not None:
            if mode == 'kh':
                self.roll_mode = DiceRollMode.MAX
            elif mode == 'kl':
                self.roll_mode = DiceRollMode.MIN
            elif mode == 'ka':
                self.roll_mode = DiceRollMode.ALL

        if self.sides == 'f':
            self.is_fudge = True
            self.isides = 1
        elif self.sides.isnumeric():
            self.isides = int(self.sides)
        else:
            self._valid = False
            return

    def is_valid(self):
        return self._valid

    def roll(self):
        dall = np.array([])
        for _ in range(self.dice_num):
            dl = 1 if not self.is_fudge else -1
            dh = self.isides + 1
            dr = np.random.randint(dl, dh)
            dall = np.append(dall, dr)

        logging.debug(dall)

        return self.__apply_mode(dall)

    def __apply_mode(self, dall: np.ndarray) -> Any:
        options = {
            DiceRollMode.SUM: np.sum,
            DiceRollMode.MAX: np.max,
            DiceRollMode.MIN: np.min,
            DiceRollMode.ALL: lambda x: x,
        }

        return options[self.roll_mode](dall)

    def __str__(self):
        if not self.is_valid():
            return 'DiceExpr: <invalid>'

        return f'DiceExpr: {self.dice_num}d{self.sides}'\
            + (self.roll_mode.value)


class NumExpr(INumericExpr):
    def __init__(self, expr: int):
        self.expr = expr

    def roll(self) -> int:
        return self.expr

    def __str__(self):
        return f'NumExpr: {self.expr}'


class OperatorType(Enum):
    SUB = '-'
    SUM = '+'
    MUL = '*'
    DIV = '/'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def from_str(cls, label):
        options = {
            '-': cls.SUB,
            '+': cls.SUM,
            '*': cls.MUL,
            '/': cls.DIV,
        }

        return options[label]


class OperatorExpr:
    def __init__(self, kind: OperatorType):
        self.kind = kind

    def __str__(self):
        return f'OperatorExpr: {self.kind}'
