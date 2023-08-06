##################################################################
#                                                                #
#.#####...#####...##..##..##..##...####...##......######...####..#
#.##..##..##..##...####...###.##..##......##......##......##.....#
#.#####...#####.....##....##.###..##.###..##......####.....####..#
#.##......##..##....##....##..##..##..##..##......##..........##.#
#.##......##..##....##....##..##...####...######..######...####..#
#................................................................#
#                                                                #
# PlanetaRY spanGLES                                             #
# The bright-side of the light-curve of (ringed) exoplanets      #
#                                                                #
##################################################################
# Jorge I. Zuluaga, Mario Sucerquia, Jaime A. Alvarado (C) 2022  #
##################################################################
import unittest
from pryngles import *
class Test(unittest.TestCase):
    def test_fun(self):
        
        #Get path
        filepath=Misc.get_data("diffuse_reflection_function.data")
        print(filepath)
        
        #print_df dataframe
        import pandas as pd
        import numpy as np
        df=pd.DataFrame(np.zeros((5,3)),columns=["a","b","c"])
        Misc.print_df(df)
        

if __name__=="__main__":
        unittest.main(argv=['first-arg-is-ignored'],exit=False)
