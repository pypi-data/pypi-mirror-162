import pandas as pd
import numpy as np
import ee
from scipy import optimize
from typing import Tuple
from climate_resilience import utils
import warnings
warnings.formatwarning = utils.warning_format


# Functions for optimizing and calculating Hersh and SarkerMaityK PMP
def calculatePMP(
    aveAMDP: np.array,
    stdAMDP: np.array,
    K: np.array
):
    """Calculate PMP
    
    Args:
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        stdAMDP (np.array): Numpy array of the standard deviation of daily precipitation annual maxima.
        K (np.array): Numpy array of frequency factors.
    
    Returns:
        np.array: Numpy array of PMP values.
    
    """
    return aveAMDP+K*stdAMDP


def HershfieldK(
    aveAMDP: np.array,
    Ka: float,
    a: float,
):
    """Calculate Hershfield Frequency Factors
    
    Args:
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        Ka (float): Fitting frequency factor for set of data.
        a (float): Fitting parameter for set of data.

    Returns:
        np.array: Numpy array of Hershfield frequency factors.
    """
    return Ka*np.exp(-a*aveAMDP)


def SarkerMaityK(
    aveAMDP: np.array,
    maxK: float,    
    KAveAMDP: float,
    Ka: float,
    a: float,
):
    """Calculate Sarker Maity Frequency Factors

    Args:
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        maxK (float): Largest calculated site frequency factor.
        KAveAMDP (float): Average AMDP corresponding to maxK.
        Ka (float): Fitting frequency factor for set of data.
        a (float): Fitting parameter for set of data.

    Returns:
        np.array: Numpy array of Sarker Maity frequency factors.

    """
    # Calculate via Hershfield, but cap K at the maximum existing frequency factor.
    K = HershfieldK(aveAMDP,Ka,a)
    K[aveAMDP<=KAveAMDP] = maxK
    
    return K


def HershError(
    fit: Tuple,
    AMDP: np.array,
    siteK: np.array,
):
    """Calculate Mean Squared Error With Hershfield Method

    Args:
        fit (tuple): Tuple of the fitting parameters Ka and a.
        AMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        siteK (np.array): Numpy array of the frequency factor calculated at each site.
    
    Results:
        float: MSE of fitting parameter guess.

    """
    # Retrieve fitting parameters
    Ka, a = fit

    # Recalculate K
    guess = HershfieldK(np.array(AMDP),Ka,a)

    # Calculate error
    error = np.sum((siteK-guess)**2)

    return error


def SMError(
    fit: Tuple,
    aveAMDP: np.array,
    siteK: np.array,
    maxK: float,
    KAveAMDP: float,
):
    """Calculate Mean Squared Error With Sarker Maity Method

    Args:
        fit (tuple): Tuple of the fitting parameters Ka and a.
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        siteK (np.array): Numpy array of the frequency factor calculated at each site.
        maxK (float): Largest calculated site frequency factor.
        KAveAMDP (float): Average AMDP corresponding to maxK.

    Results:
        float: MSE of fitting parameter guess.

    """
    # Retrieve fitting parameters
    Ka, a = fit

    # Recalculate K
    guess = SarkerMaityK(aveAMDP,maxK,KAveAMDP,Ka,a)
    
    # Calculate Error
    error = np.sum((siteK-guess)**2)

    return error


def HershCon(
    fit: Tuple,
    aveAMDP: np.array,
    siteK: np.array,
):
    """Construct Minimization Constraint for Hershfield

    Args:
        fit (tuple): Tuple of the fitting parameters Ka and a.
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        siteK (np.array): Numpy array of the frequency factor calculated at each site.

    Results:
        np.array: Numpy array of frequency factor differences that must be greater than 0.

    """
    # Retrieve fitting parameters
    Ka,a = fit

    # Recalculate frequency facotrs
    newK = HershfieldK(np.array(aveAMDP),Ka,a)
    
    # Return difference
    return newK-siteK


def SMCon(
    fit: Tuple,
    aveAMDP: np.array,
    siteK: np.array,
    maxK: float,
    KAveAMDP: float,
): 
    """Construct Minimization Constraint for Sarker Maity

    Args:
        fit (tuple): Tuple of the fitting parameters Ka and a.
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        siteK (np.array): Numpy array of the frequency factor calculated at each site.
        maxK (float): Largest calculated site frequency factor.
        KAveAMDP (float): Average AMDP corresponding to maxK.

    Results:
        np.array: Numpy array of frequency factor differences that must be greater than 0.

    """
    # Retrieve fitting parameters
    Ka,a = fit

    # Recalculate frequency factors
    newK = SarkerMaityK(np.array(aveAMDP),KAveAMDP,maxK,Ka,a)

    # Return difference
    return newK-siteK


def identifyInfluentialPoints(
    aveAMDP: np.array,
    siteK: np.array,
    maxK: float,
    KAveAMDP: float,
    numPoints: int=5,
):  
    """Identifies Influential Optimization Points

    Args:
        aveAMDP (np.array): Numpy array of the average of daily precipitation annual maxima.
        siteK (np.array): Numpy array of the frequency factor calculated at each site.
        maxK (float): Largest calculated site frequency factor.
        KAveAMDP (float): Average AMDP corresponding to maxK. 
        numPoints (int): Number of influential points to find.
    
    Returns:
        np.array: The average of daily precipitation annual maxima of the influential points.
        np.array: The frequency factor of the influential points.
    """
    # Calculate Slopes from maxK point to other point
    ms = (siteK-maxK)/(aveAMDP-KAveAMDP)

    # Sort the slopes and pick the smallest (largest negative) slopes
    msSort = np.sort(np.array(ms),axis=None)
    msPick = msSort[msSort<0][-numPoints:]

    # Find values of most influential points.
    newAMDPs = np.array([KAveAMDP])
    newKs = np.array([maxK])
    for m in msPick:
        idx = np.where(ms==m)
        newAMDPs = np.append(newAMDPs,aveAMDP[idx])
        newKs = np.append(newKs,siteK[idx])
    
    return newAMDPs, newKs


# Earth engine related functions
def checkAuth():
    """Checks for Earth Engine Authentication"""
    # Try to initialize earth engine, otherwise require authentication
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()


def generateFC(
    locDF: pd.DataFrame
):
    """Generate Feature Collection
    
    Args:
        locDF (pd.DataFrame): A DataFrame containing every point location to be included in the feature collection.
        
    Returns:
        ee.FeatureCollection: A FeatureCollection for extracting data from sites in Earth Engine.

    Raises:
        KeyError: DataFrame must contain Longitude and Latitude columnes.
    """
    # Check Earth Engine Authorization
    checkAuth()

    # Check DataFrame contains the appropriate columns
    neededColumns = ["siteK","aveAMD","stdAMD"]
    if not set(neededColumns).issubset(locDF.columns.to_list()):
        raise KeyError("The DataFrame needs to contain the following columns: Latitude and Longitude.")
    
    # Iterate through DataFrame creating list of features
    features = []
    for index,row in locDF.iterrows():
        feature = ee.Feature(ee.Geometry.Point(row.Latitude,row.Longitude))
        features.append(feature)
        
    return ee.FeatureCollection(features)


def findAllAMD(
    imCol: ee.ImageCollection,
    var: str,
    yearStart: int=-np.inf,
    yearEnd: int=np.inf,
) -> ee.ImageCollection:
    """Find Annual Daily Maximums.
    Main: 
        Args:
            imCol (ee.ImageCollection): Image Collection of dataset of interest.
            var (str): Variable of interest in the Image Collection.
            yearStart (int): First year for values to be collected.
            yearEnd (int): Last year for values to be collected (inclusive).
            
        Returns 
            ee.ImageCollection: The output Image Collection consisting of daily
            maximums images for each year.
    
    Helper: 
        Args:
            year (ee.ComputedObject/int): Year of interest.
        
        Returns:
            ee.Image: Image of annual maximums for all locations.

    """
    # Define helper function
    def findAMD(year):
        # Define earth engine tiemframe
        dateStart = ee.Date.fromYMD(year,1,1)
        dateEnd = ee.Date.fromYMD(year,12,31)

        # Filter the Image Collection for the year of interest
        imSlice = imCol.select(var).filterDate(dateStart,dateEnd)

        # Find Maximum values over the year of interest
        AMD = imSlice.max().copyProperties(imSlice.first())
        
        return AMD

    # Map helper function to a list of the years of interest and collect in a new Image Collection.
    AMDs = ee.ImageCollection(ee.List.sequence(yearStart,yearEnd).map(findAMD))
    
    return AMDs


def collectionMask(
    imCol: ee.ImageCollection,
    imageMax: ee.Image,
    var: str
) -> ee.ImageCollection:
    """Remove Maximum AMDs.
    Main: 
        Args:
            imCol (ee.ImageCollection): Image Collection of the annual maximums of the dataset.
            imageMax (ee.Image): Image of the maximum values over the entire timeframe.
            var (str): Variable of interest.

        Returns:
            ee.ImageCollection: A duplicate Image Collection with the maximums removed.
    
    Helper:
        Args:
            image (ee.Image): Annual maximum image.

        Returns:
            ee.Image: Annual maximum image with maximum value removed. 
    """
    # Define helper function
    def removeMax(image):
        # Apply no max mask to the image
        maskImage = image.select(var).updateMask(image.select(var).neq(imageMax))
       
        return ee.Image(maskImage)
    
    # Map masking function for each year of annual maxima
    noMax = imCol.map(removeMax)

    return noMax


def findAllPMP(
    imCol: ee.ImageCollection,
    var: str,
    yearStart: int=np.inf,
    yearEnd: int=np.inf,
):
    """Calculate and Retreive PMP Results
    
    Args:
        imCol (ee.ImageCollection): Image Collection of dataset of interest.
        var (str): Variable of interest in the Image Collection.
        yearStart (int): First year for values to be collected.
        yearEnd (int): Last year for values to be collected (inclusive).
    
    Returns:
        ee.ImageCollection: Image Collection of PMP calculation results.

    """
    # Process the Image Collection to retrieve AMD Image Collection
    imColAMD = findAllAMD(imCol,var,yearStart,yearEnd)

    # Calculate statistics over AMD Image Collection
    maxAMD = imColAMD.max()
    aveAMD = imColAMD.mean()
    stdAMD = imColAMD.reduce(ee.Reducer.sampleStdDev())

    # Mask AMD Image Collection
    imColnoMax = collectionMask(imColAMD,maxAMD,var)

    # Calculate statistics over Masked AMD Image Collection
    adjAveAMD = imColnoMax.mean()
    adjStdAMD = imColnoMax.reduce(ee.Reducer.sampleStdDev())

    # Calculate Frequency Factor and PMP for the site according to Hersh method
    initKs = (maxAMD.subtract(adjAveAMD)).divide(adjStdAMD)
    initPMPs = (initKs.multiply(stdAMD)).add(aveAMD)

    # Modify band names for collection creation
    stdAMD = stdAMD.select([var+"_stdDev"],[var])
    adjStdAMD = adjStdAMD.select([var+"_stdDev"],[var])
    
    # Aggregate Information in PMP Image Collection
    PMPCol = ee.ImageCollection.fromImages([initPMPs,initKs,maxAMD,aveAMD,stdAMD,adjAveAMD,adjStdAMD])
    
    return PMPCol  


def findSitePMP(
    fc: ee.FeatureCollection,
    imCol: ee.ImageCollection,
    var: str,
    yearStart: int=-np.inf,
    yearEnd: int=np.inf
):
    """ Collect PMP Results for Locations of Interest

    Args:
        fc (ee.FeatureCollection): Feature Collection of locations or area of interest.
        imCol (ee.ImageCollection): Image Collection of dataset of interest.
        var (str): Variable of interest in the Image Collection.
        yearStart (int): First year for values to be collected.
        yearEnd (int): Last year for values to be collected (inclusive).
    
    Results:
        pd.DataFrame: DataFrame of site PMP Calculation Results
    
    Raises:
        KeyError: If the input variable is not included in the bands of the Image Collection.
        ValueError: If the input time range is outside of the available time range for the Image Collection.

    """
    # Check Earth Engine Authorization
    checkAuth()
    
    # Retrieve band information
    imColBands = imCol.first().bandNames().getInfo()
    
    # Check that variable is one of the Image Collection bands
    if var not in imColBands:
        raise KeyError("Input variable does not exist in the bands of the Image Collection.")

    # Retrieve time range information
    imColEpochStart = imCol.first().date().getInfo()["value"]
    imColEpochEnd = imCol.sort("system:time_start",False).first().date().getInfo()["value"]

    # Modify input years to be in time since epoch
    imColYearStart = np.floor(imColEpochStart/(365*24*60*60)+1970)
    imColYearEnd = np.floor(imColEpochEnd/(365*24*60*60)+1970)

    # Check that data exists for range of interest
    if (yearStart < imColYearStart) or (yearEnd > imColYearEnd):
        raise ValueError(f"({yearStart}-{yearEnd} falls outside of acceptable range of \
                            {imColYearStart}-{imColYearEnd} for this Image Collection.")
    else:
        if yearStart==-np.inf:
            yearStart = imColYearStart
        if yearEnd==np.inf:
            yearEnd = imColYearEnd
    
    # Calculate PMP over the dataset
    imColPMP = findAllPMP(imCol,var,yearStart,yearEnd)

    # Collect PMP Information from Earth Engine
    PMPDict = imColPMP.toArray().sampleRegions(fc,scale=1).getInfo()
    
    # Predefine iterative variables
    index = 0
    arrayPMP = np.array([]) #Can't predefine shape effectively yet

    # Loop through and extract PMP data
    for i in PMPDict["features"]:

        # Extract site PMP info
        data = np.array(i["properties"]["array"]).flatten()
        
        # Try to add data to array, add NaN values otherwise
        # Typically for points in Feature Collection that fall outside of dataset range
        try:
            arrayPMP[index,:] = data
        except:
            arrayPMP[index,:] = np.nan
        
        index+=1

    # Create DataFrame from numpy array 
    dfPMP = pd.DataFrame(data=arrayPMP,columns=["sitePMP","siteK","maxAMDP","aveAMDP","stdAMDP","adjAveAMDP","adjStdAMDP"])
    
    return dfPMP


def eeGeographicPMP(
    eeDF: pd.DataFrame
):
    """ Re-evalute PMP Based on Regional Data

    Args:
        eeDF (pd.DataFrame): A DataFrame with a collection of initial PMP calculations of inidividual sites
        to be reevaluted.

    Returns:
        pd.DataFrame: A DataFrame returning the re-evaluted PMP calculations for each location.
    
    Raises:
        KeyError: If the DataFrame does not contain the appropriate column names: siteK, aveAMD, stdAMD.
    """
    
    # Check DataFrame contains the appropriate columns
    neededColumns = ["siteK","aveAMD","stdAMD"]
    if not set(neededColumns).issubset(eeDF.columns.to_list()):
        raise KeyError("The DataFrame needs to contain the following columns: siteK, aveAMD, and stdAMD.")
    
    # Extract relevant site information
    siteKs = eeDF.siteK.to_numpy()
    siteaveAMDP = eeDF.aveAMDP.to_numpy()
    siteSTD = eeDF.stdAMDP.to_numpy()
    maxK = np.max(siteKs)
    maxAMDP = siteaveAMDP[siteKs==maxK][0]

    # Find influential data points
    newAMDPs,newKs = identifyInfluentialPoints(siteaveAMDP,siteKs,maxAMDP,maxK)
    
    # Optimize for best fit to data
    initGuess=(maxK+2,0.01)
    args = (newAMDPs,newKs,maxAMDP,maxK)
    cons = ({'type':'ineq','fun':HershCon,'args':args},
            {'type':'ineq','fun':SMCon,'args':args})
    result = optimize.minimize(SMError,initGuess,
                                args=args,constraints=cons,
                                options={'maxiter':10000},tol=1e-10)
    Ka,a = result.x
    print(f"The fitting parameters were calculated to be Ka={Ka:.4f} and a={a:.4f}.")

    # Calculating regional K and PMP values
    geoHershKs = HershfieldK(siteaveAMDP,Ka,a)
    geoSMKs = SarkerMaityK(siteaveAMDP,maxAMDP,maxK,Ka,a)
    geoSMKs[geoSMKs>maxK] = maxK
    geoHershPMPs = calculatePMP(siteaveAMDP,siteSTD,geoHershKs)
    geoSMPMPs = calculatePMP(siteaveAMDP,siteSTD,geoSMKs)

    # Adding calculated values to dataframe
    eeDF["geoHershPMPs"] = geoHershPMPs
    eeDF["geoHershKs"] = geoHershKs
    eeDF["geoSMPMPs"] = geoSMPMPs
    eeDF["geoSMKs"] = geoSMKs

    return eeDF
