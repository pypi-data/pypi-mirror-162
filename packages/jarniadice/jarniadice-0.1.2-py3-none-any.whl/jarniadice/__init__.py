import logging
import re
import numpy as np
from typing import List, cast, Union

from jarniadice.expr import (DiceExpr, NumExpr, OperatorExpr,
                  OperatorType, INumericExpr)

Expr = Union[INumericExpr, OperatorExpr]
ExprResult = Union[int, np.ndarray]


class Roller:
    _regex_expr: str = r'(\w+!?>?\d*)\s*([+*/()-]?)'

    reg: ExprResult = 0

    def __parse_expr(self, expression: str) -> List[Expr]:
        elements = re.findall(Roller._regex_expr, expression)
        el_all = [expr for pair in elements for expr in pair]

        logging.debug(f'Parsing {el_all}')
        res: List[Expr] = []
        for expr in el_all:
            if len(expr) == 0:
                continue

            if any(d in expr for d in ('d', 'D')):
                res.append(DiceExpr(expr))
            elif expr.isnumeric():
                res.append(NumExpr(int(expr)))
            elif expr in OperatorType.list():
                res.append(OperatorExpr(OperatorType.from_str(expr)))

        return res

    def roll(self, expr: str) -> ExprResult:
        exprs = self.__parse_expr(expr)
        op = OperatorType.SUM
        last_was_numeric = True
        self.reg = 0

        logging.debug(f'Reg: {self.reg}')

        for e in exprs:
            logging.debug(f'expr> {e}')

            if last_was_numeric:
                op = OperatorType.SUM

            logging.debug('-----')
            if isinstance(e, OperatorExpr):
                logging.debug('handling operator')
                op = cast(OperatorExpr, e).kind
                last_was_numeric = False
                logging.debug(f'Op: {op}')

            elif isinstance(e, INumericExpr):
                logging.debug('handling number')
                self.reg = self.__handle_op(op, cast(INumericExpr, e).roll())
                last_was_numeric = True
                logging.debug(f'Reg: {self.reg}')

        return self.reg

    def __handle_op(self, op: OperatorType, val: ExprResult) -> ExprResult:
        handlers = {
            OperatorType.SUB.value: lambda x, y: x - y,
            OperatorType.SUM.value: lambda x, y: x + y,
            OperatorType.MUL.value: lambda x, y: x * y,
            OperatorType.DIV.value: lambda x, y: x / y,
        }

        return handlers[op.value](self.reg, val)
