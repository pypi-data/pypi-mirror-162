import os
import gc
import galsim
import fitsio
import numpy as np
import logging
import numpy.lib.recfunctions as rfn

# LSST Task
try:
    import lsst.afw.math as afwMath
    import lsst.afw.image as afwImg
    import lsst.afw.geom as afwGeom
    import lsst.meas.algorithms as meaAlg
    with_lsst=True
except ImportError as error:
    with_lsst=False
    print('Do not have lsst pipeline!')


hpInfofname     =   os.path.join(os.environ['homeWrk'],'skyMap/healpix-nside%d-nest.fits')

cosmoHSThpix    =   np.array(\
       [1743739, 1743740, 1743741, 1743742, 1743743, 1743825, 1743828,
        1743829, 1743830, 1743831, 1743836, 1743837, 1744397, 1744398,
        1744399, 1744402, 1744408, 1744409, 1744410, 1744411, 1744414,
        1744416, 1744417, 1744418, 1744419, 1744420, 1744421, 1744422,
        1744423, 1744424, 1744425, 1744426, 1744427, 1744428, 1744429,
        1744430, 1744431, 1744432, 1744433, 1744434, 1744435, 1744436,
        1744437, 1744438, 1744439, 1744440, 1744441, 1744442, 1744443,
        1744444, 1744445, 1744446, 1744447, 1744482, 1744488, 1744489,
        1744490, 1744491, 1744494, 1744512, 1744513, 1744514, 1744515,
        1744516, 1744517, 1744518, 1744519, 1744520, 1744521, 1744522,
        1744523, 1744524, 1744525, 1744526, 1744527, 1744528, 1744529,
        1744530, 1744531, 1744532, 1744533, 1744534, 1744535, 1744536,
        1744537, 1744538, 1744539, 1744540, 1744541, 1744542, 1744543,
        1744545, 1744548, 1744549, 1744550, 1744551, 1744557, 1744560,
        1744561, 1744562, 1744563, 1744564, 1744565, 1744566, 1744567,
        1744568, 1744569, 1744570, 1744571, 1744572, 1744573, 1744574,
        1744576, 1744577, 1744578, 1744579, 1744580, 1744581, 1744582,
        1744583, 1744584, 1744585, 1744586, 1744587, 1744588, 1744589,
        1744590, 1744594, 1744608, 1744609, 1744610, 1750033])

class cosmoHSTGal():
    def __init__(self,version):
        self.hpInfo     =   fitsio.read(hpInfofname %512)
        self.directory  =   os.path.join(os.environ['homeWrk'],'COSMOS/galsim_train/COSMOS_25.2_training_sample/')
        self.catName    =   'real_galaxy_catalog_25.2.fits'
        self.finName    =   os.path.join(self.directory,'cat_used.fits')
        if version=='252':
            self.hpDir  =   os.path.join(self.directory,'healpix-nside512')
        elif version=='252E':
            _dir        =   os.path.join(os.environ['homeWrk'],\
                        'COSMOS/galsim_train/COSMOS_25.2_extended/')
            self.hpDir  =   os.path.join(_dir,'healpix-nside512')
        else:
            return
        return

    def selectHpix(self,pixId):
        """
        # select galaxies in one healPIX
        """
        indFname    =   os.path.join(self.hpDir,'%d-25.2_ind.fits' %pixId)
        if os.path.isfile(indFname):
            __mask  =   fitsio.read(indFname)
        else:
            dd      =   self.hpInfo[self.hpInfo['pix']==pixId]
            __mask  =   (self.catused['ra']>dd['raMin'])\
                    &(self.catused['ra']<dd['raMax'])\
                    &(self.catused['dec']>dd['decMin'])\
                    &(self.catused['dec']<dd['decMax'])
        __out   =   self.catused[__mask]
        return __out

    def readHpixSample(self,pixId):
        """
        # select galaxies in one healPIX
        """
        fname   =   os.path.join(self.hpDir,'cat-%d-25.2.fits' %pixId)
        if os.path.isfile(fname):
            out =   fitsio.read(fname)
        else:
            out =   None
        return out

    def readHSTsample(self):
        """
        # read the HST galaxy training sample
        """
        if os.path.isfile(self.finName):
            catfinal    =   fitsio.read(self.finName)
        else:
            cosmos_cat  =   galsim.COSMOSCatalog(self.catName,dir=self.directory)
            # used index
            index_use   =   cosmos_cat.orig_index
            # used catalog
            paracat     =   cosmos_cat.param_cat[index_use]
            # parametric catalog
            oricat      =   fitsio.read(cosmos_cat.real_cat.getFileName())[index_use]
            ra          =   oricat['RA']
            dec         =   oricat['DEC']
            indexNew    =   np.arange(len(ra),dtype=int)
            __tmp=np.stack([ra,dec,indexNew]).T
            radec=np.array([tuple(__t) for __t in __tmp],dtype=[('ra','>f8'),('dec','>f8'),('index','i8')])
            catfinal    =   rfn.merge_arrays([paracat,radec], flatten = True, usemask = False)
            fitsio.write(self.finName,catfinal)
        self.catused    =   catfinal
        return

def makeHSCExposure(galData,psfData,pixScale,variance):
    """
    Generate an HSC image
    """
    if not with_lsst:
        raise ImportError('Do not have lsstpipe!')
    ny,nx       =   galData.shape
    exposure    =   afwImg.ExposureF(nx,ny)
    exposure.getMaskedImage().getImage().getArray()[:,:]=galData
    exposure.getMaskedImage().getVariance().getArray()[:,:]=variance
    #Set the PSF
    ngridPsf    =   psfData.shape[0]
    psfLsst     =   afwImg.ImageF(ngridPsf,ngridPsf)
    psfLsst.getArray()[:,:]= psfData
    psfLsst     =   psfLsst.convertD()
    kernel      =   afwMath.FixedKernel(psfLsst)
    kernelPSF   =   meaAlg.KernelPsf(kernel)
    exposure.setPsf(kernelPSF)
    #prepare the wcs
    #Rotation
    cdelt   =   (pixScale*afwGeom.arcseconds)
    CD      =   afwGeom.makeCdMatrix(cdelt, afwGeom.Angle(0.))#no rotation
    #wcs
    crval   =   afwGeom.SpherePoint(afwGeom.Angle(0.,afwGeom.degrees),afwGeom.Angle(0.,afwGeom.degrees))
    #crval   =   afwCoord.IcrsCoord(0.*afwGeom.degrees, 0.*afwGeom.degrees) # hscpipe6
    crpix   =   afwGeom.Point2D(0.0, 0.0)
    dataWcs =   afwGeom.makeSkyWcs(crpix,crval,CD)
    exposure.setWcs(dataWcs)
    #prepare the frc
    dataCalib = afwImg.makePhotoCalibFromCalibZeroPoint(63095734448.0194)
    exposure.setPhotoCalib(dataCalib)
    return exposure


## For ring tests
def make_ringrot_radians(nord=8):
    """
    Generate rotation angle array for ring test
    Parameters:
        nord:   up to 1/2**nord*pi rotation
    """
    rotArray=   np.zeros(2**nord)
    nnum    =   0
    for j in range(nord+1):
        nj  =   2**j
        for i in range(1,nj,2):
            nnum+=1
            rotArray[nnum]=i/nj
    return rotArray*np.pi

def make_basic_sim(outDir,gname,Id0):
    """
    Make basic galaxy image simulation (isolated)
    Parameters:
        outDir:     output directory
        gname:      shear distortion setup
        Id0:        index of the simulation
    """
    nx          =   100
    ny          =   100
    ngrid       =   64
    scale       =   0.168
    # Get the shear information
    gList       =   np.array([-0.02,0.,0.02])
    gList       =   gList[[eval(i) for i in gname.split('-')[-1]]]
    if gname.split('-')[0]=='g1':
        g1=gList[0]
        g2=0.
    elif gname.split('-')[0]=='g2':
        g1=0.
        g2=gList[0]
    else:
        raise ValueError('cannot decide g1 or g2')
    logging.info('Processing for %s, and shear List is for %s.' %(gname,gList))
    # PSF
    psfFWHM =   eval(outDir.split('_psf')[-1])/100.
    logging.info('The FWHM for PSF is: %s arcsec'%psfFWHM)
    psfInt  =   galsim.Moffat(beta=3.5,fwhm=psfFWHM,trunc=psfFWHM*4.)
    psfInt  =   psfInt.shear(e1=0.02,e2=-0.02)
    #psfImg =   psfInt.drawImage(nx=45,ny=45,scale=scale)

    gal_image=  galsim.ImageF(nx*ngrid,ny*ngrid,scale=scale)
    gal_image.setOrigin(0,0)
    outFname=   os.path.join(outDir,'image-%d-%s.fits' %(Id0,gname))
    if os.path.exists(outFname):
        logging.info('Already have the outcome')
        return

    ud      =   galsim.UniformDeviate(Id0)
    bigfft  =   galsim.GSParams(maximum_fft_size=10240)
    if 'small' not in outDir:
        # use parametric galaxies
        if 'Shift' in outDir:
            do_shift=   True
            logging.info('Galaxies with be randomly shifted')
        else:
            do_shift=   False
            logging.info('Galaxies will not be shifted')
        rotArray    =   make_ringrot_radians(8)
        logging.info('We have %d rotation realizations' %len(rotArray))
        irot        =   Id0//8     # we only use 80000 galaxies
        ang         =   rotArray[irot]*galsim.radians
        Id          =   int(Id0%8)
        logging.info('Making Basic Simulation. ID: %d, GID: %d.' %(Id0,Id))
        logging.info('The rotating angle is %.2f degree.' %rotArray[irot])
        # Galsim galaxies
        directory   =   os.path.join(os.environ['homeWrk'],\
                        'COSMOS/galsim_train/COSMOS_25.2_training_sample/')
        catName     =   'real_galaxy_catalog_25.2.fits'
        cosmos_cat  =   galsim.COSMOSCatalog(catName,dir=directory)

        # Basic parameters
        flux_scaling=   2.587
        # catalog
        cosmo252=   cosmoHSTGal('252')
        cosmo252.readHSTsample()
        hscCat  =   cosmo252.catused[Id*10000:(Id+1)*10000]
        for i,ss  in enumerate(hscCat):
            ix  =   i%nx
            iy  =   i//nx
            b   =   galsim.BoundsI(ix*ngrid,(ix+1)*ngrid-1,iy*ngrid,(iy+1)*ngrid-1)
            # each galaxy
            gal =   cosmos_cat.makeGalaxy(gal_type='parametric'\
                    ,index=ss['index'],gsparams=bigfft)
            gal =   gal.rotate(ang)
            gal =   gal*flux_scaling
            gal =   gal.shear(g1=g1,g2=g2)
            if do_shift:
                dx =ud()-1
                dy =ud()-1
                gal=gal.shift(dx,dy)
            gal =   galsim.Convolve([psfInt,gal],gsparams=bigfft)
            # draw galaxy
            sub_img =   gal_image[b]
            gal.drawImage(sub_img,add_to_image=True)
            del gal,b,sub_img
            gc.collect()
        del hscCat,cosmos_cat,cosmo252,psfInt
        gc.collect()
    else:
        # use galaxies with random knots
        irr =   eval(outDir.split('_psf')[0].split('small')[-1])
        if irr==0:
            radius  =0.07
        elif irr==1:
            radius  =0.15
        elif irr==2:
            radius  =0.20
        else:
            raise ValueError('Something wrong with the outDir!')
        logging.info('Making Small Simulation with Random Knots.' )
        logging.info('Radius: %s, ID: %s.' %(radius,Id0) )
        npoints =   20
        gal0    =   galsim.RandomKnots(half_light_radius=radius,\
                    npoints=npoints,flux=10.,rng=ud)
        for ix in range(100):
            for iy in range(100):
                igal   =    ix*100+iy
                b      =    galsim.BoundsI(ix*ngrid,(ix+1)*ngrid-1,\
                            iy*ngrid,(iy+1)*ngrid-1)
                if igal%4==0 and igal!=0:
                    gal0=   galsim.RandomKnots(half_light_radius=radius,\
                            npoints=npoints,flux=10.,rng=ud,gsparams=bigfft)
                sub_img =   gal_image[b]
                ang     =   igal%4*np.pi/4. * galsim.radians
                gal     =   gal0.rotate(ang)
                # Shear the galaxy
                gal     =   gal.shear(g1=g1,g2=g2)
                gal     =   galsim.Convolve([psfInt,gal],gsparams=bigfft)
                # Draw the galaxy image
                gal.drawImage(sub_img,add_to_image=True)
                del gal,b,sub_img
                gc.collect()
    gal_image.write(outFname,clobber=True)
    del gal_image
    gc.collect()
    return
