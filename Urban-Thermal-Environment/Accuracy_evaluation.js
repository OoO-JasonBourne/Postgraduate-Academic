var image20010703_yuan = ee.ImageCollection(['LANDSAT/LE07/C02/T1_L2/LE07_118038_20010703', 'LANDSAT/LE07/C02/T1_L2/LE07_118039_20010703'])
              .mosaic()
              .clip(table)
              .select("ST_B6")
              .rename("LST")
              .multiply(0.00341802)
              .subtract(273.5)
              .add(149)
Map.addLayer(image20010703_yuan, {}, 'image20010703_yuan')

var imageStrip_20080519 = ee.ImageCollection(['LANDSAT/LE07/C02/T1_L2/LE07_118038_20080519', 'LANDSAT/LE07/C02/T1_L2/LE07_118039_20080519'])
                                .mosaic()
                                .clip(table)
                                .select("ST_B6")
                                .rename("LST")
                                .multiply(0.00341802)
                                .subtract(273.5)
                                .add(149)
// Map.addLayer(imageStrip_20080519, {}, 'imageStrip_20080519')

var missingStrip = imageStrip_20080519.mask().neq(0);
// Map.addLayer(missingStrip, {}, 'missingStrip');
var maskedImage = image20010703_yuan.updateMask(missingStrip);

var regionOfInterest = imageStrip_20080519.geometry().bounds();




var image1 = image20010703_yuan;
var image2 = maskedImage_fill;
var diff = image1.subtract(image2);

var rmse = diff.pow(2).reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: table,
  scale: 30,
  maxPixels: 1e9
}).getNumber('LST').sqrt();

print('RMSE:', rmse);


var scale = 30; 
var factor = 2;
var ergas_1 = diff.reduceRegion({
  reducer: ee.Reducer.mean().combine(ee.Reducer.stdDev(), null, true),
  geometry: table,
  scale: scale,
  maxPixels: 1e9
}).get('LST_mean');

var ergas_2 = ee.Number(factor).multiply(diff.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: table,
  scale: scale,
  maxPixels: 1e9
}).get('LST'));
var ergas = ee.Number(ergas_1).divide(ergas_2)

print('ergas',ergas)

var psnr = ee.Number(10).multiply(ee.Number(2.302585092994046)).multiply(diff.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: table,
  scale: scale,
  maxPixels: 1e9
}).get('LST')).log10().multiply(20).multiply(-1);
print('psnr',psnr)

var sam = image1.select("LST").spectralAngle(image2.select("LST"));
print('sam', sam)


var cc = image1.select('LST').reduceRegion({
  reducer: ee.Reducer.pearsonsCorrelation(),
  geometry: table,
  scale: scale,
  maxPixels: 1e9
}).get('LST');
print('cc', cc)



























