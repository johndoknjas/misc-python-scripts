from more_itertools import powerset
from typing import List

def main():
    powerset_of_5 = set(powerset({1,2,3,4,5}))
    subtract_powersets: List[set] = [{1,2,3,5}, {1,4,3,5}, {1,2,4,5}]
    for subtract_powerset in subtract_powersets:
        powerset_of_5 = powerset_of_5 - set(powerset(subtract_powerset))
    print(powerset_of_5)

if __name__ == "__main__":
    main()