import pandas as pd
import numpy as np
import iris
import iris.coord_categorisation as cat
import geopy.distance as dist

# Extract information from ERA5 grib5 and convert to 
def extractGribInfo(filepath,savepath=""):
    cube = iris.load_cubes(filepath)[0]
    cat.add_year(cube,'time',name='year')
    annCube = cube.aggregated_by('year',iris.analysis.MAX)
    # Option to save the data in a .nc file which is easier for iris to read
    if savepath!="":
        iris.save(annCube,savepath)
    timeUnit = annCube.coords()[0].units
    firstYear = timeUnit.num2date(annCube.coords()[0].points[0]).year
    lastYear = timeUnit.num2date(annCube.coords()[0].points[-1]).year+1
    years=range(firstYear,lastYear)
    cubeDict = {}
    for i in range(0,annCube.shape[0]):
        yearDF = pd.DataFrame(annCube[i].data.data)
        yearDF = yearDF.replace(annCube[i].data.fill_value,np.nan)
        yearDF.index = annCube.coords()[1].points
        yearDF.columns = annCube.coords()[2].points
        cubeDict[years[i]] = pd.DataFrame(yearDF)
    return cubeDict

def removeMask(val_arr,z_indices):
    v_shp = val_arr.shape
    mask = np.zeros(v_shp,dtype=bool)
    y,x = np.ogrid[0:v_shp[1], 0:v_shp[2]]
    mask[z_indices,y,x] = 1
    val_arr[mask] = np.nan
    return val_arr

def calcPMPParams(dfDict,savepath = ""):
    numpyMap = np.array([])
    for i in dfDict:
        numpyMap = np.append(numpyMap, dfDict[i].to_numpy())
    numpyMap = numpyMap.reshape(len(cubeDict),len(cubeDict[i].columns),len(cubeDict[i].index))
    maxAMDP = numpyMap.max(axis=0)
    aveAMDP = numpyMap.mean(axis=0)
    stdAMDP = numpyMap.std(axis=0)
    maskIdx = numpyMap.argmax(axis=0)
    numpyMap = removeMask(numpyMap,maskIdx)
    numpyMapMasked = np.ma.array(numpyMap,mask=np.isnan(numpyMap))
    aveAdjAMDP = numpyMapMasked.mean(axis=0).filled(fill_value=np.nan)
    stdAdjAMDP = numpyMapMasked.std(axis=0).filled(fill_value=np.nan)
    siteK = (maxAMDP-aveAdjAMDP)/stdAdjAMDP
    sitePMP = aveAMDP+siteK*stdAMDP
    
    lonsMesh,latsMesh = np.meshgrid(cubeDict[i].columns,cubeDict[i].index)
    newDict = {"Latitude":latsMesh.ravel(),
               "Longitude":lonsMesh.ravel(),
               "sitePMP":sitePMP.ravel(),
               "siteK":siteK.ravel(),
               "maxAMDP":maxAMDP.ravel(),
               "aveAMDP":aveAMDP.ravel(),
               "stdAMDP":stdAMDP.ravel(),
               "aveAdjAMDP":aveAdjAMDP.ravel(),
               "stdAdjAMDP":stdAdjAMDP.ravel()}
    newDF = pd.DataFrame(data=newDict)
    if savepath!="":
        newDF.to_csv(savepath,index=False)
    return newDF 

# Functions for identify distance to site
def LocationTuple(df):
    df["Location"] = (df.Latitude,df.Longitude)
    return df

def calcDistance(df,location):
    df["Distance"] = dist.geodesic(location,df.Location).km
    return df

def nearbySites(df,location,radius,units='km'):
    # Determine unit conversion parameter.
    radius = convertUnits(radius,'Distance',units,'km')
    
    # Use radius to find latitude and longitude bounds for performance
    cLat, cLon = location
    dLat = radius/(110.574)
    dLonP = radius/(111.320*np.cos((cLat+dLat)*np.pi/180))
    dLonM = radius/(111.320*np.cos((cLon-dLat)*np.pi/180))
    dLon = np.max([dLonP,dLonM])
    
    # Apply bounds and calculate distance, then clean for circular radius
    df = df.loc[(df.Latitude<(cLat+dLat)) & (df.Latitude>(cLat-dLat)) & \
                (df.Longitude<(cLon+dLon)) & (df.Longitude>(cLon-dLon))]
    df = df.apply(LocationTuple,axis=1)
    df = df.apply(calcDistance,args=(location,),axis=1)
    df = df.loc[df.Distance<=radius]
    print("A total of %s have been selected." % len(df.index))
    return df

    