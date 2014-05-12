import numpy

import sqlite3
from sqlite3 import dbapi2 as sqlite

import os
import unittest
import warnings
import sys
import lsst.utils.tests as utilsTests

from lsst.sims.catalogs.measures.instance import InstanceCatalog
from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData
from lsst.sims.coordUtils.Astrometry import AstrometryGalaxies, AstrometryStars, compound
from lsst.sims.photUtils.Photometry import PhotometryGalaxies, PhotometryStars
from lsst.sims.photUtils.Bandpass import Bandpass
from lsst.sims.photUtils.Sed import Sed
from lsst.sims.photUtils.EBV import EBVmixin

from lsst.sims.photUtils.Variability import Variability

class testDefaults(object):

    def get_proper_motion_ra(self):
        ra=self.column_by_name('raJ2000')
        out=numpy.zeros(len(ra))
        for i in range(len(ra)):
            out[i]=0.0
        
        return out
  
    
    def get_proper_motion_dec(self):
        ra=self.column_by_name('raJ2000')
        out=numpy.zeros(len(ra))
        for i in range(len(ra)):
            out[i]=0.0
        
        return out
    
    def get_parallax(self):
        ra=self.column_by_name('raJ2000')
        out=numpy.zeros(len(ra))
        for i in range(len(ra)):
            out[i]=1.2
        
        return out
    
    def get_radial_velocity(self):
        ra=self.column_by_name('raJ2000')
        out=numpy.zeros(len(ra))
        for i in range(len(ra)):
            out[i]=0.0
        
        return out

class cartoonPhotometryStars(PhotometryStars):
    """
    This is a class to support loading cartoon bandpasses into photometry so that we can be sure
    that the photometry mixin is loading the right files and calculating the right magnitudes.
    """

    @compound('cartoon_u','cartoon_g','cartoon_r','cartoon_i','cartoon_z')
    def get_magnitudes(self):
        idNames = self.column_by_name('id')
        bandPassList=['u','g','r','i','z']
        bandPassDir=os.getenv('SIMS_PHOTUTILS_DIR')+'/tests/cartoonSedTestData/'
        output = self.meta_magnitudes_getter(idNames, bandPassList, 
                  bandPassDir = bandPassDir, bandPassRoot = 'test_bandpass_')
        
       
        magNormList = self.column_by_name('magNorm')
        sedNames = self.column_by_name('sedFilename')
        
        #the two variables below will allow us to get at the SED and magnitude
        #data from within the unit test class, so that we can be sure
        #that the mixin loaded the correct bandPasses
        sublist = self.loadSeds(sedNames,magNorm = magNormList)
        for ss in sublist:
            self.sedMasterList.append(ss)
        
        if len(output) > 0:
            for i in range(len(output[0])):
                subList = []
                for j in range(len(output)):
                    subList.append(output[j][i])
            
                self.magnitudeMasterList.append(subList)
       
        return output


class cartoonPhotometryGalaxies(PhotometryGalaxies):
    """
    This is a class to support loading cartoon bandpasses into photometry so that we can be sure
    that the photometry mixin is loading the right files and calculating the right magnitudes.
    """

    @compound('ctotal_u','ctotal_g','ctotal_r','ctotal_i','ctotal_z',
              'cbulge_u','cbulge_g','cbulge_r','cbulge_i','cbulge_z',
              'cdisk_u','cdisk_g','cdisk_r','cdisk_i','cdisk_z',
              'cagn_u','cagn_g','cagn_r','cagn_i','cagn_z')
    def get_magnitudes(self):
        idNames = self.column_by_name('galid')
        bandPassList=['u','g','r','i','z']
        bandPassDir=os.getenv('SIMS_PHOTUTILS_DIR')+'/tests/cartoonSedTestData/'
        output = self.meta_magnitudes_getter(idNames, bandPassList, 
                  bandPassDir = bandPassDir, bandPassRoot = 'test_bandpass_')
        
        if len(output) > 0:
            for i in range(len(output[0])):
                j = 5
                subList = []
                while j < 10:
                    subList.append(output[j][i])
                    j += 1
                self.magnitudeMasterDict['Bulge'].append(subList)
                
                subList = []
                while j < 15:
                    subList.append(output[j][i])
                    j += 1
                self.magnitudeMasterDict['Disk'].append(subList)
                
                subList = []
                while j < 20:
                    subList.append(output[j][i])
                    j += 1
                self.magnitudeMasterDict['Agn'].append(subList)
                
                
        
        
        componentNames = ['Bulge','Disk','Agn']
        
        for cc in componentNames:
            magName = "magNorm" + cc
            magNormList = self.column_by_name(magName)
            sName = "sedFilename" + cc
            sedNames = self.column_by_name(sName)
            
            if cc == 'Bulge' or cc == 'Disk':
                AvName = "internalAv"+cc
                Av = self.column_by_name(AvName)
            else:
                Av = None
        
            
            redshift = self.column_by_name("redshift")
            
            sublist = self.loadSeds(sedNames, magNorm = magNormList)
            self.applyAvAndRedshift(sublist, internalAv = Av, redshift = redshift)
            
            for ss in sublist:
                self.sedMasterDict[cc].append(ss)
       
        return output




class testCatalog(InstanceCatalog,AstrometryStars,Variability,testDefaults):
    catalog_type = 'MISC'
    default_columns=[('expmjd',5000.0,float)]
    
    def db_required_columns(self):
        return ['raJ2000'],['varParamStr']


class cartoonStars(InstanceCatalog,AstrometryStars,EBVmixin,Variability,cartoonPhotometryStars,testDefaults):
    catalog_type = 'cartoonStars'
    column_outputs=['id','ra_corr','dec_corr','magNorm',\
    'cartoon_u','cartoon_g','cartoon_r','cartoon_i','cartoon_z']
    
    sedMasterList = []
    magnitudeMasterList = []
    

class cartoonGalaxies(InstanceCatalog,AstrometryGalaxies,EBVmixin,Variability,cartoonPhotometryGalaxies,testDefaults):
    catalog_type = 'cartoonGalaxies'
    column_outputs=['galid','ra_corr','dec_corr',\
    'ctotal_u','ctotal_g','ctotal_r','ctotal_i','ctotal_z']
    
    sedMasterDict = {}
    sedMasterDict["Bulge"] = []
    sedMasterDict["Disk"] = []
    sedMasterDict["Agn"] = []
    
    magnitudeMasterDict = {}
    magnitudeMasterDict["Bulge"] = []
    magnitudeMasterDict["Disk"] = []
    magnitudeMasterDict["Agn"] = []
 
        
class testStars(InstanceCatalog,AstrometryStars,EBVmixin,Variability,PhotometryStars,testDefaults):
    catalog_type = 'test_stars'
    column_outputs=['id','ra_corr','dec_corr','magNorm',\
    'stellar_magNorm_var', \
    'lsst_u','sigma_lsst_u','lsst_u_var','sigma_lsst_u_var',
    'lsst_g','sigma_lsst_g','lsst_g_var','sigma_lsst_g_var',\
    'lsst_r','sigma_lsst_r','lsst_r_var','sigma_lsst_r_var',\
    'lsst_i','sigma_lsst_i','lsst_i_var','sigma_lsst_i_var',\
    'lsst_z','sigma_lsst_z','lsst_z_var','sigma_lsst_z_var',\
    'lsst_y','sigma_lsst_y','lsst_y_var','sigma_lsst_y_var',\
    'EBV','varParamStr']

class testGalaxies(InstanceCatalog,AstrometryGalaxies,EBVmixin,Variability,PhotometryGalaxies,testDefaults):
    catalog_type = 'test_galaxies'
    column_outputs=['galid','ra_corr','dec_corr',\
        'magNorm_Recalc_var', 'magNormAgn', 'magNormBulge', 'magNormDisk', \
        'uRecalc', 'sigma_uRecalc', 'uRecalc_var','sigma_uRecalc_var',\
        'gRecalc', 'sigma_gRecalc', 'gRecalc_var','sigma_gRecalc_var',\
        'rRecalc', 'sigma_rRecalc', 'rRecalc_var', 'sigma_rRecalc_var',\
         'iRecalc', 'sigma_iRecalc', 'iRecalc_var','sigma_iRecalc_var',\
         'zRecalc', 'sigma_zRecalc', 'zRecalc_var', 'sigma_zRecalc_var',\
         'yRecalc', 'sigma_yRecalc', 'yRecalc_var', 'sigma_yRecalc_var',\
        'sedFilenameBulge','uBulge', 'sigma_uBulge', 'gBulge', 'sigma_gBulge', \
        'rBulge', 'sigma_rBulge', 'iBulge', 'sigma_iBulge', 'zBulge', 'sigma_zBulge',\
         'yBulge', 'sigma_yBulge', \
        'sedFilenameDisk','uDisk', 'sigma_uDisk', 'gDisk', 'sigma_gDisk', 'rDisk', 'sigma_rDisk', \
        'iDisk', 'sigma_iDisk', 'zDisk', 'sigma_zDisk', 'yDisk', 'sigma_yDisk', \
        'sedFilenameAgn',\
        'uAgn', 'sigma_uAgn', 'uAgn_var', 'sigma_uAgn_var',\
        'gAgn', 'sigma_gAgn', 'gAgn_var', 'sigma_gAgn_var',\
        'rAgn', 'sigma_rAgn', 'rAgn_var', 'sigma_rAgn_var',\
        'iAgn', 'sigma_iAgn', 'iAgn_var', 'sigma_iAgn_var',\
        'zAgn', 'sigma_zAgn', 'zAgn_var', 'sigma_zAgn_var',\
        'yAgn', 'sigma_yAgn', 'yAgn_var', 'sigma_yAgn_var', 'varParamStr']


class variabilityUnitTest(unittest.TestCase):

    galaxy = DBObject.from_objid('galaxyBase')
    rrly = DBObject.from_objid('rrly')
    obsMD = DBObject.from_objid('opsim3_61')
    obs_metadata = obsMD.getObservationMetaData(88544919, 0.1, makeCircBounds = True)
    
    def testGalaxyVariability(self):   
                
        galcat = testCatalog(self.galaxy,obs_metadata = self.obs_metadata)
        rows = self.galaxy.query_columns(['varParamStr'], constraint = 'VarParamStr is not NULL',chunk_size=20)
        rows = rows.next()
        for i in range(20):
            #print "i ",i
            mags=galcat.applyVariability(rows[i]['varParamStr'])
            #print mags

    def testRRlyVariability(self):
        rrlycat = testCatalog(self.rrly,obs_metadata = self.obs_metadata)
        rows = self.rrly.query_columns(['varParamStr'], constraint = 'VarParamStr is not NULL',chunk_size=20)
        rows = rows.next()
        for i in range(20):
            mags=rrlycat.applyVariability(rows[i]['varParamStr'])

class photometryUnitTest(unittest.TestCase):
       
    def testStars(self):
        dbObj=DBObject.from_objid('rrly')
        obs_metadata_pointed=ObservationMetaData(mjd=2013.23, circ_bounds=dict(ra=200., dec=-30, radius=1.))
        obs_metadata_pointed.metadata = {}
        obs_metadata_pointed.metadata['Opsim_filter'] = 'i'
        test_cat=testStars(dbObj,obs_metadata=obs_metadata_pointed)
        test_cat.write_catalog("testStarsOutput.txt")
    
    def testAlternateBandpassesStars(self):
        dbObj=DBObject.from_objid('rrly')
        obs_metadata_pointed=ObservationMetaData(mjd=2013.23, circ_bounds=dict(ra=200., dec=-30, radius=1.))
        obs_metadata_pointed.metadata = {}
        obs_metadata_pointed.metadata['Opsim_filter'] = 'i'
        test_cat=cartoonStars(dbObj,obs_metadata=obs_metadata_pointed)
        test_cat.write_catalog("testStarsCartoon.txt")
        
        cartoonDir = os.getenv('SIMS_PHOTUTILS_DIR')+'/tests/cartoonSedTestData/'
        testBandPasses = {}
        keys = ['u','g','r','i','z']
        
        bplist = []

        for kk in keys:
            testBandPasses[kk] = Bandpass()
            testBandPasses[kk].readThroughput(os.path.join(cartoonDir,"test_bandpass_%s.dat" % kk))
            bplist.append(testBandPasses[kk])
        
        sedObj = Sed()
        phiArray, waveLenStep = sedObj.setupPhiArray(bplist)
        
        for ss in test_cat.sedMasterList:
            ss.resampleSED(wavelen_match = bplist[0].wavelen)
            ss.flambdaTofnu()

        
        i = 0
        for ss in test_cat.sedMasterList:
            mags = -2.5*numpy.log10(numpy.sum(phiArray*ss.fnu, axis=1)*waveLenStep) - ss.zp
            for j in range(len(mags)):
                self.assertAlmostEqual(mags[j],test_cat.magnitudeMasterList[i][j],10)
            i += 1
    
    
    def testGalaxies(self):
        dbObj=DBObject.from_objid('galaxyBase')
        obs_metadata_pointed=ObservationMetaData(mjd=50000.0, circ_bounds=dict(ra=0., dec=0., radius=0.01))
        obs_metadata_pointed.metadata = {}
        obs_metadata_pointed.metadata['Opsim_filter'] = 'i'

        test_cat=testGalaxies(dbObj,obs_metadata=obs_metadata_pointed)
        test_cat.write_catalog("testGalaxiesOutput.txt")

    def testAlternateBandpassesGalaxies(self):
        dbObj=DBObject.from_objid('galaxyBase')
        obs_metadata_pointed=ObservationMetaData(mjd=50000.0, circ_bounds=dict(ra=0., dec=0., radius=0.01))
        obs_metadata_pointed.metadata = {}
        obs_metadata_pointed.metadata['Opsim_filter'] = 'i'
        test_cat=cartoonGalaxies(dbObj,obs_metadata=obs_metadata_pointed)
        test_cat.write_catalog("testGalaxiesCartoon.txt")
        
        cartoonDir = os.getenv('SIMS_PHOTUTILS_DIR')+'/tests/cartoonSedTestData/'
        testBandPasses = {}
        keys = ['u','g','r','i','z']
        
        bplist = []

        for kk in keys:
            testBandPasses[kk] = Bandpass()
            testBandPasses[kk].readThroughput(os.path.join(cartoonDir,"test_bandpass_%s.dat" % kk))
            bplist.append(testBandPasses[kk])
        
        sedObj = Sed()
        phiArray, waveLenStep = sedObj.setupPhiArray(bplist)
        
        components = ['Bulge', 'Disk', 'Agn']
        
        for cc in components:
            for ss in test_cat.sedMasterDict[cc]:
                if ss.wavelen != None:
                    ss.resampleSED(wavelen_match = bplist[0].wavelen)
                    ss.flambdaTofnu()
        
            i = 0
            for ss in test_cat.sedMasterDict[cc]:
                if ss.wavelen != None:
                    mags = -2.5*numpy.log10(numpy.sum(phiArray*ss.fnu, axis=1)*waveLenStep) - ss.zp
                    for j in range(len(mags)):
                        self.assertAlmostEqual(mags[j],test_cat.magnitudeMasterDict[cc][i][j],10)
                i += 1
 

     
def suite():
    utilsTests.init()
    suites = []
    #suites += unittest.makeSuite(variabilityUnitTest)
    suites += unittest.makeSuite(photometryUnitTest)
    return unittest.TestSuite(suites)

def run(shouldExit = False):
    utilsTests.run(suite(),shouldExit)

if __name__ == "__main__":
    run(True)
