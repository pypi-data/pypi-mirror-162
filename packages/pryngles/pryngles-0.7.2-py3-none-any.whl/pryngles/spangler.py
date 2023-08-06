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
#!/usr/bin/env python
# coding: utf-8

# # Pryngles module: Spangler

# This module contains all the physics of light scattered on spangles

from pryngles import *

# ## External modules

import pandas as pd
from collections import OrderedDict as odict
from copy import deepcopy
import random

#Aliases
print_df=Misc.print_df
sci=Science
verbose=Verbose.print

# ## The Spangler class
# 
# This class contains a family of routines useful for spangling different kind of objects.

Spangler_doc="""A Spangler associated to an object or set of objects.
    
   There are two ways to initialize a Spangler:
    
        Creating a Spangler for a single object:

            nspangles: int, default = 0:
                Number of spangles in spangling.

            body_hash: string, default = None:
                Hash identifying the body to which spangles are associated 
                (see Body documentation for explanation about hash).
                
            spangle_type: int, default = 0:
                Type of spangle (see *_SPANGLE in Consts module).

            n_equ: numpy Array (3), default = [0,0,1]:
                unitary vector normal to {equ} (equatorial) plane.
        
        Joining a set of Spanglers (several objects):

            spanglers: list of Spanglers. default = []:
                Set of spanglers to join.
                
            n_obs: numpy Array (3), default = [0,0,1]:
                unitary vector normal to {obs} observer direction.
            
Core attributes:

    nspangles: int:
        Total number of spangles.

    data: Pandas DataFrame: 
        Dataframe containing all the information about the spangling.
        For Columns see global variable SPANGLER_COLUMNS.

            
Secondary attributes:

    M_ecl2obs, M_obs2ecl: array (3x3):
        Transformation matrices going from {obs} <-> {ecl}.

    M_ecl2equ, M_equ2ecl: array (nspanglersx3x3):
        Transformation matrices going from {equ} <-> {ecl}.
        
Public methods:
    
    update_positions: update positions by changing observer orientation.
"""

#Columns of spangling
SPANGLER_COLUMNS=odict(
    {
        "body_hash":"",
        
        #Type of spangle
        "type":SOLID_SPANGLE,
        
        #Lengh-scale of the coordinates
        "scale":1,
        
        #Coordinates of the spangle (cartesian and spherical)
        "x_ecl":0,"y_ecl":0,"z_ecl":0,#Calculated in the class
        "r_ecl":0,"t_ecl":0,"f_ecl":0,#Calculated in the class

        #Coordinates of the spangle with an arbitrary origin
        "X_ecl":0,"Y_ecl":0,"Z_ecl":0,#Calculated in the class
        
        #Equatorial system
        "n_equ":[0,0,1],#Direction of the equator
        "alpha_equ":0,#Zero meridian of equatorial system
        "x_equ":0,"y_equ":0,"z_equ":1,
        "r_equ":0,"t_equ":0,"f_equ":90*Consts.deg,
        
        #Observer system
        "n_obs":[0,0,1],
        "alpha_obs":0,#Zero meridian of observer system
        "x_obs":0,"y_obs":0,"z_obs":0,#Calculated in the class
        "r_obs":0,"t_obs":0,"f_obs":0,#Calculated in the class
        
        #Coordinates with respect to the light source
        "n_luz":[0,0,1],
        "alpha_luz":0,#Zero meridian of observer system
        "x_luz":0,"y_luz":0,"z_luz":0,#Calculated in the class
        "r_luz":0,"t_luz":0,"f_luz":0,#Calculated in the class

        #Unitary vector normal to spangle
        "ns_equ":[0,0,1],
        "ns_ecl":[0,0,0],#Calculated in the class
        "ns_obs":[0,0,0],#Calculated in the class
        "ns_luz":[0,0,0],#Calculated in the class
        
        #Geometrical parameters
        "asp":1.0, #Area
        "dsp":1.0, #Effective diameter of spangle
        
        #Optical parameters
        "albedo_gray_normal":1,
        "tau_gray_optical":0.0,
        
        #Spangle state
        "unset":1, #State has not been set
        "visible":0, #The spangle is visible from observer
        "shadow":0, #The spangle is in the shadow of other spangle
        "illuminated":0, #The spangle is illuminated
        "transit":0, #The spangle is transiting
        "indirect":0, #The spangle is indirectly illuminated
        "occult":0, #The spangle is occulted by a light source
    }
)

class Spangler(PrynglesCommon):
    
    def __init__(self,
                 #Initialization using specific options
                 nspangles=1,body_hash=None,spangle_type=SOLID_SPANGLE,
                 n_equ=SPANGLER_COLUMNS["n_equ"],n_obs=SPANGLER_COLUMNS["n_obs"],
                 #Initialization with a list of 
                 spanglers=[]):

        #Create a spanglers with a list of other spanglers
        if len(spanglers)>0:
            self._join_spanglers(spanglers,n_obs=n_obs)
            
        #Create a spangler with the desired options
        else:
            #Attributes
            self.nspangles=nspangles
            
            #Update default values
            self._defaults=deepcopy(SPANGLER_COLUMNS)

            if not body_hash:
                body_hash=str(random.getrandbits(16))
            self._defaults.update(dict(body_hash=body_hash))
            if spangle_type:
                self._defaults.update(dict(type=spangle_type))

            #Create Spangler dataframe
            if self.nspangles>0:
                
                #Create a simple DataFrame with the default values
                self.data=pd.DataFrame([list(self._defaults.values())]*self.nspangles,columns=self._defaults.keys())

                #Update positions
                self.set_positions(n_equ=n_equ,n_obs=n_obs)
        
            else:        
                #Creat a blank DataFrame
                self.data=pd.DataFrame(columns=self._defaults.keys())
                
    # Prototype
    def _join_spanglers(self,spanglers,nobs):pass
    
Spangler.__doc__=Spangler_doc

def set_observer(self,n_obs=[],alpha_obs=0,force=False):

    if len(n_obs)>0:
        #Unitary observer vector
        n_obs,one=spy.unorm(n_obs)
        self.data["n_obs"]=self.data.apply(lambda df:n_obs,axis=1)

        #Observer direction in spherical coordinates
        self.d_obs=sci.xyz2rtf(n_obs)

        #Transformation matrices
        ez_obs=n_obs
        ex_obs=spy.ucrss([0,0,1],n_obs) #Spice is 5 faster for vcrss
        if spy.vnorm(ex_obs)==0:
            ex_obs=np.array([1,0,0]) if np.sum(ez_obs)>0 else np.array([-1,0,0])
        ey_obs=spy.ucrss(ez_obs,ex_obs)
        self.M_obs2ecl=np.array(list(np.vstack((ex_obs,ey_obs,ez_obs)).transpose())).reshape((3,3))
        self.M_ecl2obs=spy.invert(self.M_obs2ecl)
        verbose("Axis obs:",ex_obs,ey_obs,ez_obs)
        self.axis_obs=[ex_obs,ey_obs,ez_obs]

    #Update positions
    self.data[["x_obs","y_obs","z_obs"]]=        self.data.apply(lambda df:pd.Series(spy.mxv(self.M_ecl2obs,
                                                    [df.x_ecl,df.y_ecl,df.z_ecl])),
                        axis=1)
    
    self.data[["r_obs","t_obs","f_obs"]]=        self.data.apply(lambda df:pd.Series(sci.xyz2rtf([df.x_obs,df.y_obs,df.z_obs])),
                        axis=1)

    #Update spangles orientations
    self.data["ns_obs"]=self.data.apply(lambda df:spy.mxv(self.M_ecl2obs,df["ns_ecl"]),axis=1)

Spangler.set_observer=set_observer

def set_positions(self,
                 n_equ=[],alpha_equ=0,
                 n_obs=[],alpha_obs=0):
    """
    Set the positions and orientation of spanglers in the ecliptic system.

    Parameters:

        n_equ: list/array (3), default = []:
            Normal vector towards north pole equatorial system.

    Optional:

        alpha_equ: float, default = 0:
            Roll angle of x-axis of equatorial system (not implemented yet)

    Return:
        None

    Update:

        Coordinates of the spangles, (x_ecl,y_ecl,z_ecl) and their spherical 
        counterparts (r_ecl,t_ecl,f_ecl).

        Normal to spangles, ns_ecl, ns_obs.

        Rotation matrices M_equ2ecl
    """
    
    if len(n_equ)>0:
        #Unitary equatorial vector
        n_equ,one=spy.unorm(n_equ)
        self.data["n_equ"]=self.data.apply(lambda df:n_equ,axis=1)

        #Transformation matrices
        ez_equ=n_equ
        ex_equ=spy.ucrss([0,0,1],n_equ)
        if spy.vnorm(ex_equ)==0:
            ex_equ=np.array([1,0,0]) if np.sum(ez_equ)>0 else np.array([-1,0,0])
        ey_equ=spy.ucrss(ez_equ,ex_equ)
        
        self.M_equ2ecl=np.array(list(np.vstack((ex_equ,ey_equ,ez_equ)).transpose())).reshape((3,3))
        self.M_ecl2equ=spy.invert(self.M_equ2ecl)
        self.axis_equ=[ex_equ,ey_equ,ez_equ]
        verbose("Axis equ:",ex_equ,ey_equ,ez_equ)

    #Update spangles positions
    self.data[["x_ecl","y_ecl","z_ecl"]]=        self.data.apply(lambda df:pd.Series(spy.mxv(self.M_equ2ecl,
                                                    [df.x_equ,df.y_equ,df.z_equ])),
                        axis=1)

    self.data[["r_ecl","t_ecl","f_ecl"]]=        self.data.apply(lambda df:pd.Series(sci.xyz2rtf([df.x_ecl,df.y_ecl,df.z_ecl])),
                        axis=1)

    #Update spangles orientations
    self.data["ns_ecl"]=self.data.apply(lambda df:spy.mxv(self.M_equ2ecl,np.array(df["ns_equ"])),axis=1)
    
    #Set observer
    self.set_observer(n_obs=n_obs)
    
Spangler.set_positions=set_positions


def populate_spangler(self,scale=1,seed=0,geometry="circle",**geometry_args):
    """Populate data of a Spangler using points generated with a given geometry.
    
    Parameters:
    
        geometry: string, default = "circle":
            Geometry of the Sampler.  Available: "circle", "ring", "sphere"
            
            
        seed: integer. default = 0:
            Value of the integer seed of random number generation (if 0 no random seed is set).
            If a non-zero seed is used the position of the spangle will be always the same.
    """
    #Create sampler
    self.sample=Sampler(N=self.nspangles,seed=seed)
    self.geometry=geometry
    
    #Generate sampling points
    exec(f"self.sample.gen_{geometry}(**geometry_args)")
    
    #Purge sample if it is in 3d
    if self.sample.dim>2:
        verbose("Purging sample")
        self.sample.purge_sample()
                
    #Check if number of samples is not equal to that of spangles
    if self.sample.N!=self.nspangles:
        dif=self.sample.N-self.nspangles
        if dif>0:
            for i in range(dif):
                df=pd.DataFrame([self.data.iloc[-1]])
                self.data=pd.concat([self.data,df],ignore_index=True)
        else:
            self.data.drop(range(self.nspangles+dif,self.nspangles),inplace=True)
        self.nspangles=self.sample.N
    
    #Area
    self.data["asp"]=self.sample.aes*scale**2
    self.data["dsp"]=2*(self.data["asp"]/np.pi)**0.5
    
    #Update scale
    self.data["scale"]=scale

    #Store positions in DataFrame
    self.data[["x_equ","y_equ","z_equ"]]=self.sample.ss*scale

    #Update normal vectors
    if self.sample.dim>2:
        self.data["ns_equ"]=self.data.apply(
            lambda df:spy.unorm([df["x_equ"],df["y_equ"],df["z_equ"]])[0],axis=1)
    else:
        self.data["ns_equ"]=self.data.apply(
            lambda df:[0,0,1],axis=1)
        
    #Update positions
    self.set_positions()
    
Spangler.populate_spangler=populate_spangler


def plot3d(self,spangled=dict(),factor=1.2,**args):
    """
    Plot spangle.

    Parameters:
        args: scatter plotting options, dictionary.
    """
    sargs=dict(c='k',s=0.1)
    sargs.update(args)
    bgcolor='k'

    #Figure
    fig=plt.figure(figsize=(5,5))
    fig.patch.set_facecolor(bgcolor)
    ax=fig.add_subplot(111,projection='3d',facecolor=bgcolor)

    ax.axis("off")
    ax.scatter(self.data.x_ecl,self.data.y_ecl,self.data.z_ecl,**sargs)

    #Spangles
    for i in range(self.nspangles):
        center=[self.data.x_ecl[i],self.data.y_ecl[i],self.data.z_ecl[i]]
        radius=self.data.dsp[i]/2
        zDir=self.data.ns_ecl[i]
        verbose(i,center,radius,zDir)
        Plot.circle3d(ax,
                      center=center,
                      radius=radius,
                      zDir=zDir,
                      color='c',alpha=0.5)    

    ax.set_box_aspect([1,1,1])

    #Range
    maxval=1.0*np.abs(self.data[["x_ecl","y_ecl","z_ecl"]].to_numpy()).max()
    ax.set_xlim(-maxval,maxval)
    ax.set_ylim(-maxval,maxval)
    ax.set_zlim(-maxval,maxval)
    
    #Decoration
    xmin,xmax=factor*np.array(list(ax.get_xlim()))
    ymin,ymax=factor*np.array(list(ax.get_ylim()))
    zmin,zmax=factor*np.array(list(ax.get_zlim()))

    #Axis
    ax.plot([xmin,xmax],[0,0],[0,0],'w-',alpha=0.3)
    ax.plot([0,0],[ymin,ymax],[0,0],'w-',alpha=0.3)
    ax.plot([0,0],[0,0],[zmin,zmax],'w-',alpha=0.3)
    ax.text(xmax,0,0,r"$x_{ecl}$",color='w',alpha=0.5,fontsize=8)
    ax.text(0,ymax,0,r"$y_{ecl}$",color='w',alpha=0.5,fontsize=8)
    ax.text(0,0,zmax,r"$z_{ecl}$",color='w',alpha=0.5,fontsize=8)

    #Title
    ax.set_title(f"Spangler {self.geometry}, N = {self.nspangles}",
                 color='w',fontsize=10)
    Plot.pryngles_mark(ax)

    #Orientation
    ax.view_init(azim=30)
    fig.tight_layout()

    self.fig3d=fig
    self.ax3d=ax

Spangler.plot3d=plot3d


def plot_obs(self,spangled=dict(),**args):
    """
    Plot spangle.

    Parameters:
        args: scatter plotting options, dictionary.
    """
    sargs=dict(c='c',s=3.5)
    sargs.update(args)
    bgcolor='k'

    #Figure
    fig=plt.figure(figsize=(5,5))
    fig.patch.set_facecolor(bgcolor)
    ax=fig.add_subplot(111,facecolor=bgcolor)
    ax.axis("off")

    #Plot
    cond=self.data.z_obs>=0
    ax.scatter(self.data.x_obs[cond],self.data.y_obs[cond],**sargs)
    cond=self.data.z_obs<0
    sargs.update(dict(alpha=0.4))
    ax.scatter(self.data.x_obs[cond],self.data.y_obs[cond],**sargs)

    #Ranges
    maxval=1.2*np.abs(self.data[["x_obs","y_obs","z_obs"]].to_numpy()).max()
    ax.set_xlim(-maxval,maxval)
    ax.set_ylim(-maxval,maxval)
    
    factor=1
    xmin,xmax=factor*np.array(list(ax.get_xlim()))
    ymin,ymax=factor*np.array(list(ax.get_ylim()))

    #Axis
    ax.plot([xmin,xmax],[0,0],'w-',alpha=0.3)
    ax.plot([0,0],[ymin,ymax],'w-',alpha=0.3)
    ax.text(xmax,0,r"$x_{obs}$",color='w',alpha=0.5,fontsize=8)
    ax.text(0,ymax,r"$y_{obs}$",color='w',alpha=0.5,fontsize=8)

    #Title
    lamb_obs=self.d_obs[1]*Consts.rad
    phi_obs=self.d_obs[2]*Consts.rad
    label_obs=f"Obs ($\lambda$,$\\beta$) : ({lamb_obs:.1f}$^\circ$,{phi_obs:.1f}$^\circ$)"
    ax.set_title(f"Spangler {self.geometry}, N = {self.nspangles}, {label_obs}",
                 color='w',fontsize=10,position=(0.5,+0.5),ha='center')
    Plot.pryngles_mark(ax)

    #Decoration
    #ax.set_aspect("equal")

    fig.tight_layout()
    self.fig2d=ax
    self.ax2d=ax

Spangler.plot_obs=plot_obs


def _join_spanglers(self,spanglers,n_obs):
    """
    Join spanglers into a single spangler
    """
    self.spanglers=spanglers
    datas=[spangler.data for spangler in spanglers]
    self.data=pd.concat(datas,ignore_index=True)
    self.nspangles=len(self.data)
    self.geometry="Join"
    self.set_observer(n_obs)
    
Spangler._join_spanglers=_join_spanglers


# Set scale
def set_scale(self,scale):
    lengths=[
        "x_equ","y_equ","z_equ",
        "x_ecl","y_ecl","z_ecl",
        "x_obs","y_obs","z_obs",
        "r_equ","r_ecl","r_obs",
        "dsp",
    ]
    self.data[lengths]*=scale
    areas=[
        "asp",
    ]
    self.data[areas]*=scale**2
    

Spangler.set_scale=set_scale


