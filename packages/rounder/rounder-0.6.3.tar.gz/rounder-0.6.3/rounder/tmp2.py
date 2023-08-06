from functools import partial
from timeit import repeat
from rounder import signif_object
from pprint import pprint
from time import perf_counter

setup = """
from rounder import map_object, map_object_clean, signif
obj = {'number': 12.323, 'string': 'whatever', 'list': [122.45, .01]}
fun = lambda x: signif(x**.5, 3)
"""

n = 10_000_000
r = 21

repeat_ = partial(repeat, setup=setup, number=n, repeat=r)

start1 = perf_counter()
t1 = repeat_("map_object(fun, obj, use_copy=True)")
print("current:")
print(signif_object({"all ": sorted(t1),
                      "min  ": min(t1),
                      "range": max(t1) - min(t1)}))
print(f"Elapsed time: {perf_counter() - start1}")