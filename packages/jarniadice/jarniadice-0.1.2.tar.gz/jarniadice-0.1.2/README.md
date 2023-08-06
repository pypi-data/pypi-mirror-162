# Jarnia Dice
A library for parsing and evaluating Jarnia Dice Notation.

In the future, we aim to have all the features of standard Dice Notation,
but also more.

The current stage of development is pre-alpha, and I'm running
this library only on a private telegram bot and implementing
the features as I need.

# Documentation (Draft)
`roller.Roller().roll('3d6')`
Run three d6 and return the **sum**.

`roller.Roller().roll('2d10kh')`
Run two d10 and return the value of the **higher**.

`roller.Roller().roll('2d10kl')`
Run two d10 and return the value of the **lower**.

`roller.Roller().roll('2d10ka')`
Run two d10 and return **all** the values as a
[numpy.ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray).
