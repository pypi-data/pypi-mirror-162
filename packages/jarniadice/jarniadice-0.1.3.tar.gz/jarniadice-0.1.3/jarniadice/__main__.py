import sys
import jarniadice as dice

if __name__ == "__main__":
    expr = ' '.join(sys.argv[1:])
    res = dice.Roller().roll(expr)
    print(res)
