from more_itertools import powerset
from typing import List

def remove_subsets_of_second(set_of_sets: set, remove_subsets_of_this: set) -> set:
    new_set_of_sets = set()
    for s in set_of_sets:
        if not set(s) <= set(remove_subsets_of_this):
            new_set_of_sets.add(s)
    return new_set_of_sets

def main():
    powerset_of_5 = powerset({1,2,3,4,5})
    discard_subsets_of_these: List[set] = [{1,2,3,5}, {1,4,3,5}, {1,2,4,5}]
    for discard_subsets_of_s in discard_subsets_of_these:
        powerset_of_5 = remove_subsets_of_second(powerset_of_5, discard_subsets_of_s)
    print(powerset_of_5)













if __name__ == "__main__":
    main()