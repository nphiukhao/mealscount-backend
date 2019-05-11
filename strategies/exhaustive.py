from .base import BaseCEPStrategy,CEPGroup
from itertools import combinations, chain

class ExaustiveCEPStrategy(BaseCEPStrategy):
    ''' Grouping strategy is to compute every possible partition

    * This follows with https://en.wikipedia.org/wiki/Partition_of_a_set
    * We limit this to districts with 10 Schools or less

      '''
    name="Exhaustive"
    def create_groups(self,district):
        # some debugging/optimization required

        # check district size, if over 10 don't calculates partitions
        # bell number of 10 = 115,975 (15 ~ 1.4 bil;  20 ~ 51.7 tril)
        # if over assign groups like OneToOne (this way it can run on all districts without taking a year)
        if len(district.schools) > 10:
            self.groups = [
                CEPGroup(school.district,school.name,[school])
                for school in district.schools
            ]
        else:
            def partition(collection):
                '''gives the all possible partitions as nested lists'''
                # function straight from stock overflow- seems to work well (search Set partitions in python)
                if len(collection) == 1:
                    yield [collection]
                    return

                first = collection[0]
                for smaller in partition(collection[1:]):
                    # insert `first` in each of the subpartition's subsets
                    for n, subset in enumerate(smaller):
                        yield smaller[:n] + [[first] + subset] + smaller[n + 1:]
                    # put `first` in its own subset
                    yield [[first]] + smaller


            def powerset(iterable):
                ''' gives all possible combinations for group sizes 1 to all groups'''
                s = list(iterable)
                return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))

            # generate all CEPgroup objects for all possible groups
            possible_groups = {}
            for i, g in enumerate(powerset(district.schools)):
                possible_groups[g] = CEPGroup(district, i, list(g))

            best_grouping = []
            best_covered = 0
            # generate all partions
            for x in partition(district.schools):
                # save grouping with highest num of covered students
                grouping = []
                students_covered = 0
                for group in x:
                    grouping.append(possible_groups[tuple(group)])
                    students_covered += possible_groups[tuple(group)].covered_students
                    if students_covered > best_covered:
                        best_grouping = grouping
                        best_covered = students_covered
            self.groups = best_grouping

