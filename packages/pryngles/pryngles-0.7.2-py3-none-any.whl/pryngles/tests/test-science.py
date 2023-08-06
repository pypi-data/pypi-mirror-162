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
    def test_temp(self):
        
        #Test
        Science.template()
        """
        self.assertEqual(self.P.Nr,8,True)
        self.assertEqual(np.isclose([P.physics.wrot],
                                    [2*np.pi/PlanetDefaults.physics["prot"]],
                                    rtol=1e-7),
                         [True]*1)
        self.assertRaises(AssertionError,lambda:Observer(primary="Nada"))
        """
        
    def test_xyz(self):
        
        #Test
        rqf=Science.xyz2rtf([1,1,0])
        
        #Test it in each quadrant
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([+1,+1,1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([-1,1,1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([-1,-1,1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([+1,-1,1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([+1,+1,-1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([-1,1,-1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([-1,-1,-1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        rqf=Science.xyz2rtf([+1,-1,-1])
        print(rqf[0],rqf[1]*Consts.rad,rqf[2]*Consts.rad)   
        """
        self.assertEqual(self.P.Nr,8,True)
        self.assertEqual(np.isclose([P.physics.wrot],
                                    [2*np.pi/PlanetDefaults.physics["prot"]],
                                    rtol=1e-7),
                         [True]*1)
        self.assertRaises(AssertionError,lambda:Observer(primary="Nada"))
        """
        

if __name__=="__main__":
        unittest.main(argv=['first-arg-is-ignored'],exit=False)
