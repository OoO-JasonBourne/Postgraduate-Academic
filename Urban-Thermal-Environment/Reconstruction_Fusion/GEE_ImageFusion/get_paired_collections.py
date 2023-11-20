# -*- coding: utf-8 -*-


import ee
import math




import os

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

ee.Initialize()


# # 要裁剪的区域
region_2 = ee.FeatureCollection('users/mwang3108/ShangHai_new')




def maskLandsat(image):
    cloudShadowBitMask = 1 << 4
    cloudsBitMask = 1 << 3
    snow = 1 << 5

    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
        .And(qa.bitwiseAnd(cloudsBitMask).eq(0)) \
        .And(qa.bitwiseAnd(snow).eq(0))
    saturationMask = image.select('QA_RADSAT').eq(0)
    opticalBand = image.select('ST_B6')
    lst = opticalBand.rename('LST')


    return image.updateMask(mask) \
                .addBands(opticalBand, None, True) \
                .addBands(lst, None, True) \
                .select('LST') \
                .copyProperties(image, ["system:time_start"])


# 计算MODIS像素个数的函数
def maskPixel(image):
    realCount = image.reduceRegion(
                        reducer= ee.Reducer.count(),
                        geometry= region_2,
                        scale= 1000,
                        maxPixels= 1e9) \
                    .get('LST')
    return image.set({'count': realCount})



def LST_mod(image):
    opticalBand = image.select('LST_Day_1km')
    lst = opticalBand.rename('LST')

    return image.addBands(opticalBand, None, True) \
                .addBands(lst) \
                .select('LST') \
                .copyProperties(image, ["system:time_start", 'system:id'])

def clip_l(image):
    image = image.clip(region_2.geometry())
    return image.copyProperties(image, ["system:time_start"])
def clip_mosaic_up(image):
    # 定义多边形的坐标点
    coords = [[120.78502536508415,31.139586861627034],
              [122.12571896237502, 30.908382834815963],
              [122.05430782956252, 31.780978892553495],
              [121.10124386471877, 31.93028400895904],
              [120.78502536508415,31.139586861627034]]

    image = image.clip(ee.Geometry.Polygon(coords))
    return image.copyProperties(image, ["system:time_start"])

def clip_mosaic_down(image):
    # 定义多边形的坐标点
    coords = [[120.81979868318524, 31.11429686700464],
              [120.84589121248212, 30.688913085673992],
              [121.89371225740399, 30.66765341078872],
              [122.04340097810712, 31.035490498845707],
              [120.87747690584149, 31.21887884697859],
              [120.81979868318524, 31.11429686700464]]
    image = image.clip(ee.Geometry.Polygon(coords))
    return image.copyProperties(image, ["system:time_start"])
def clip_m(image):
    image = image.clip(region_2.geometry())
    return image.copyProperties(image, ["system:time_start", 'system:id'])
def qtd(image):
    filled1a = image.focal_mean(2, 'square', 'pixels', 8)
    return filled1a.blend(image) \
                   .copyProperties(image, ["system:time_start"])
    # 使用map函数应用焦点均值，使用以下代码对集合中的每个图像进行混合



##############################################################################
# FILTER AND PAIR IMAGES
##############################################################################
def addDependents(image):
    years = image.date().difference('1970-01-01', 'year')
    timeRadians = ee.Image(years.multiply(2 * math.pi)).rename('t')
    constant = ee.Image(1)
    return image.addBands(constant).addBands(timeRadians.float())

#定义
harmonics = 4
harmonicFrequencies = ee.List.sequence(1, harmonics)

#另外创建了一个列表-------------------------------------------------------------------------------------
harmonicFrequencies_1 = ['1', '2', '3', '4']






def constructBandNames(base, list):

    return ee.List(list).map(lambda i: ee.String(base).cat(i))
# def constructBandNames(base, list):
#     def transit_1(i):
#         return ee.String(base).cat(ee.Number(i).int())
#     return ee.List(list).map(transit_1)

cosNames = constructBandNames('cos_', harmonicFrequencies_1)
sinNames = constructBandNames('sin_', harmonicFrequencies_1)
independents = ee.List(['constant', 't']).cat(cosNames).cat(sinNames)


def addHarmonics(freqs):
    def transit(image):
        frequencies = ee.Image.constant(freqs)
        time = ee.Image(image).select('t')
        cosines = time.multiply(frequencies).cos().rename(cosNames)
        sines = time.multiply(frequencies).sin().rename(sinNames)
        return image.addBands(cosines).addBands(sines)
    return transit

# 计算MODIS像素个数的函数
def maskPixel(image):
    realCount = image.reduceRegion(
                        reducer= ee.Reducer.count(),
                        geometry= region_2,
                        scale= 1000,
                        maxPixels= 1e9) \
                    .get('LST')
    return image.set({'count': realCount})

def getPaired(startDate, endDate,
              landsatCollection, landsatBands, bandNamesLandsat,
              modisCollection, modisBands, bandNamesModis,
              commonBandNames, region_up, region_down):
    # 重新编辑---------------------------------------------------------
    if landsatCollection == 'LANDSAT/LE07/C02/T1_L2':
        landsat = ee.ImageCollection(landsatCollection) \
                    .filterDate(startDate, endDate) \
                    .filterBounds(region_up) \
                    .filterMetadata('CLOUD_COVER', 'less_than', 30) \
                    .select(landsatBands, bandNamesLandsat) \
                    .map(maskLandsat) \
                    .map(qtd) \
                    .map(addDependents) \
                    .map(addHarmonics(harmonicFrequencies))
        dependent = 'LST'
        harmonicTrend = landsat.select(independents.add(dependent)) \
                               .reduce(ee.Reducer.linearRegression(independents.length(), 1))
        harmonicTrendCoefficients = harmonicTrend.select('coefficients') \
                                                 .arrayProject([0]) \
                                                 .arrayFlatten([independents])

        def fitted(image):
            return image.addBands(
                image.select(independents) \
                    .multiply(harmonicTrendCoefficients) \
                    .reduce('sum') \
                    .rename('LST')) \
                    .uint16()

        fittedHarmonic = landsat.map(fitted)

        #重新定义重命名函数
        def rena(image):
            return image.select('LST') \
                        .reproject('EPSG:32651', None, 100) \
                        .clipToBoundsAndScale(region_2)

        ###down
        landsat_down = ee.ImageCollection(landsatCollection) \
            .filterDate(startDate, endDate) \
            .filterBounds(region_down) \
            .filterMetadata('CLOUD_COVER', 'less_than', 30) \
            .select(landsatBands, bandNamesLandsat) \
            .map(maskLandsat) \
            .map(qtd) \
            .map(addDependents) \
            .map(addHarmonics(harmonicFrequencies))

        harmonicTrend_down = landsat_down.select(independents.add(dependent)) \
            .reduce(ee.Reducer.linearRegression(independents.length(), 1))
        harmonicTrendCoefficients_down = harmonicTrend_down.select('coefficients') \
            .arrayProject([0]) \
            .arrayFlatten([independents])

        def fitted_down(image):
            return image.addBands(
                image.select(independents) \
                    .multiply(harmonicTrendCoefficients_down) \
                    .reduce('sum') \
                    .rename('LST')) \
                .uint16()

        fittedHarmonic_down = landsat_down.map(fitted_down)

        land_1_up = fittedHarmonic.first()
        land_1_up = clip_mosaic_up(land_1_up)
        land_2_up = fittedHarmonic.sort('system:time_start', False).first()
        land_2_up = clip_mosaic_up(land_2_up)

        land_1_down = fittedHarmonic_down.first()
        land_1_down = clip_mosaic_down(land_1_down)
        land_2_down = fittedHarmonic_down.sort('system:time_start', False).first()
        land_2_down = clip_mosaic_down(land_2_down)
        landsat_1 = ee.Image(ee.ImageCollection([land_1_up, land_1_down])
                             .mosaic()
                             .copyProperties(land_1_up, ["system:time_start"]))
        landsat_2 = ee.Image(ee.ImageCollection([land_2_up, land_2_down])
                             .mosaic()
                             .copyProperties(land_2_up, ["system:time_start"]))
        # 重新定义重命名函数
        def rena(image):
            return image.select('LST') \
                .reproject('EPSG:32651', None, 100) \
                .clipToBoundsAndScale(region_2)

        landsat = ee.ImageCollection([landsat_1, landsat_2]) \
                        .map(clip_l) \
                        .map(rena) \
                        .map(lambda image: image \
                             .setMulti({
                                'system:time_start':
                                    ee.Date(image.date().format('y-M-d')) \
                                    .millis(),
                                'DOY': image.date().format('D')
                                })) \
                        .select(commonBandNames)
    else:
        landsat = ee.ImageCollection(landsatCollection) \
            .filterDate(startDate, endDate) \
            .filterBounds(region_up) \
            .filterMetadata('CLOUD_COVER', 'less_than', 30) \
            .select(landsatBands, bandNamesLandsat) \
            .map(maskLandsat) \
            .map(qtd) \
            .map(addDependents) \
            .map(addHarmonics(harmonicFrequencies))
        dependent = 'LST'
        harmonicTrend = landsat.select(independents.add(dependent)) \
            .reduce(ee.Reducer.linearRegression(independents.length(), 1))
        harmonicTrendCoefficients = harmonicTrend.select('coefficients') \
            .arrayProject([0]) \
            .arrayFlatten([independents])

        def fitted(image):
            return image.addBands(
                image.select(independents) \
                    .multiply(harmonicTrendCoefficients) \
                    .reduce('sum') \
                    .rename('LST')) \
                .uint16()

        fittedHarmonic = landsat.map(fitted)

        # 重新定义重命名函数
        def rena(image):
            return image.select('LST') \
                .reproject('EPSG:32651', None, 100) \
                .clipToBoundsAndScale(region_2)

        ###down
        landsat_down = ee.ImageCollection(landsatCollection) \
            .filterDate(startDate, endDate) \
            .filterBounds(region_down) \
            .filterMetadata('CLOUD_COVER', 'less_than', 30) \
            .select(landsatBands, bandNamesLandsat) \
            .map(maskLandsat) \
            .map(qtd) \
            .map(addDependents) \
            .map(addHarmonics(harmonicFrequencies))

        harmonicTrend_down = landsat_down.select(independents.add(dependent)) \
            .reduce(ee.Reducer.linearRegression(independents.length(), 1))
        harmonicTrendCoefficients_down = harmonicTrend_down.select('coefficients') \
            .arrayProject([0]) \
            .arrayFlatten([independents])

        def fitted_down(image):
            return image.addBands(
                image.select(independents) \
                    .multiply(harmonicTrendCoefficients_down) \
                    .reduce('sum') \
                    .rename('LST')) \
                .uint16()

        fittedHarmonic_down = landsat.map(fitted_down)

        land_1_up = fittedHarmonic.first()
        land_2_up = fittedHarmonic.sort('system:time_start', False).first()
        land_1_down = fittedHarmonic_down.first()
        land_2_down = fittedHarmonic_down.sort('system:time_start', False).first()
        landsat_1 = ee.Image(ee.ImageCollection([land_1_up, land_1_down])
                             .mosaic()
                             .copyProperties(land_1_up, ["system:time_start"]))
        landsat_2 = ee.Image(ee.ImageCollection([land_2_up, land_2_down])
                             .mosaic()
                             .copyProperties(land_2_up, ["system:time_start"]))

        # 重新定义重命名函数
        def rena(image):
            return image.select('LST') \
                .reproject('EPSG:32651', None, 100) \
                .clipToBoundsAndScale(region_2)

        landsat = ee.ImageCollection([landsat_1, landsat_2]) \
            .map(clip_l) \
            .map(rena) \
            .map(lambda image: image \
                 .setMulti({
            'system:time_start':
                ee.Date(image.date().format('y-M-d')) \
                    .millis(),
            'DOY': image.date().format('D')
        })) \
            .select(commonBandNames)


    # get modis images
    modis = ee.ImageCollection(modisCollection) \
              .filterDate(startDate, endDate) \
              .select(modisBands, bandNamesModis) \
              .map(LST_mod) \
              .map(clip_m) \
              .map(maskPixel) \
              .filter(ee.Filter.gt('count', 6500)) \
              .map(lambda image: image.set('DOY', image.date().format('D'))) \
              .select(commonBandNames)

    # filter the two collections by the date property
    dayfilter = ee.Filter.equals(leftField='system:time_start',
                                 rightField='system:time_start')

    # define simple join
    pairedJoin = ee.Join.simple()
    # define inverted join to find modis images without landsat pair
    invertedJoin = ee.Join.inverted()

    # create collections of paired landsat and modis images
    landsatPaired = pairedJoin.apply(landsat, modis, dayfilter)
    modisPaired = pairedJoin.apply(modis, landsat, dayfilter)
    modisUnpaired = invertedJoin.apply(modis, landsat, dayfilter)

    return [landsatPaired, modisPaired, modisUnpaired]


##############################################################################
# CREATE SUBCOLLECTIONS FOR EACH SET OF LANDSAT/MODIS PAIRS
##############################################################################


def getDates(image, empty_list):
    """
    Get date from image and append to list.

    Parameters
    ----------
    image : image.Image
        Any earth engine image.
    empty_list : ee_list.List
        Earth engine list object to append date to.

    Returns
    -------
    updatelist : ee_list.List
        List with date appended to the end.

    """
    # get date and update format
    date = ee.Image(image).date().format('yyyy-MM-dd')

    # add date to 'empty list'
    updatelist = ee.List(empty_list).add(date)

    return updatelist


def makeSubcollections(paired):
    """
    Reorganize the list of collections into a list of lists of lists. Each\
    list within the list will contain 3 lists. The first of these three will\
    have the earliest and latest Landsat images. The second list will have the\
    earliest and latest MODIS images. The third list will have all the MODIS\
    images between the earliest and latest pairs.\
    (e.g. L8 on 05/22/2017 & 06/23/2017, MOD 05/23/2017 & 06/23/2017,\
     MOD 05/23/2017 through 06/22/2017).

    Parameters
    ----------
    paired : python List
        List of image collections. 1. Landsat pairs, 2. MODIS pairs, and\
        3. MODIS between each of the pairs.

    Returns
    -------
    ee_list.List
        List of lists of lists.

    """
    def getSub(ind):
        """
        Local function to create individual subcollection.

        Parameters
        ----------
        ind : int
            Element of the list to grab.

        Returns
        -------
        ee_list.List
            List of pairs lists for prediction 2 pairs and images between.

        """
        # get landsat images
        lan_01 = paired[0] \
            .filterDate(ee.List(dateList).get(ind),
                        ee.Date(ee.List(dateList).get(ee.Number(ind).add(1)))\
                            .advance(1, 'day')) \
            .toList(2)
        # get modis paired images
        mod_01 = paired[1] \
            .filterDate(ee.List(dateList).get(ind),
                        ee.Date(ee.List(dateList).get(ee.Number(ind).add(1)))\
                            .advance(1, 'day')) \
            .toList(2)
        # get modis images between these two dates
        mod_p = paired[2] \
            .filterDate(ee.List(dateList).get(ind),
                        ee.Date(ee.List(dateList).get(ee.Number(ind).add(1)))\
                            .advance(1, 'day'))

        mod_p = mod_p.toList(mod_p.size())

        # combine collections to one object
        subcollection = ee.List([lan_01, mod_01, mod_p])

        return subcollection

    # empty list to store dates
    empty_list = ee.List([])

    # fill empty list with dates
    dateList = paired[0].iterate(getDates, empty_list)

    # filter out sub collections from paired and unpaired collections
    subcols = ee.List.sequence(0, ee.List(dateList).length().subtract(2))\
        .map(getSub)

    return subcols


