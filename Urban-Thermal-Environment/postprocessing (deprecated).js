Map.centerObject(image, 7)
// var image_id = ee.String(image.get('system:id'))
// print(image)
// var id_new = image_id.slice(32)
// var year = id_new.split('_')
// var start = ee.String(year.get(0)).cat(ee.String((year.get(1))))
// var end = ee.String(year.get(0)).cat(ee.String((year.get(2))))
// var date_start = ee.Date.parse('YYYYDDD', start)
// var date_end = ee.Date.parse('YYYYDDD', end)
// image = image.set({'system:time':date_end})
// print(image)

// print(date_start)
// print(date_end)
// print(start)
// print(year)
// print(image_id)
// print(id_new)

var images = ee.ImageCollection([image, image2, image3, image4, image5, image6, image7, image8, image9, image10,
 image11, image12, image13, image14, image15, image16, image17, image18, image19, image20, image21, image22, image23,
 image24, image25, image26, image27, image28, image29, image30, image31,  image33, image34, image35])

//影像后处理 （镶嵌、筛选、重命名 、添加日期）
var img_mosaic = function(img){
  var img0 = img.select(0).rename('LST')
  var img1 = img.select(1).rename('LST')
  var img2 = img.select(2).rename('LST')
  var img3 = img.select(3).rename('LST')
  var img4 = img.select(4).rename('LST')
  var img5 = img.select(5).rename('LST')
  var img6 = img.select(6).rename('LST')
  var img7 = img.select(7).rename('LST')
  var img8 = img.select(8).rename('LST')
  var img9 = img.select(9).rename('LST')

  var imgs = ee.ImageCollection([img0, img1, img2, img3, img4, img5,  img6, img7, img8, img9])
  //影像筛选函数
  var filter = function(img){
      // var lte = image.lte(65000)
      var gte = img.gte(30000)
      return img.updateMask(gte)
  }

  var imgss = imgs.map(filter)

  var img_m = imgss.mosaic()

  //影像日期重命名
  var img_id = ee.String(img.get('system:id'))
  var id_new = img_id.slice(32)

  //影响添加日期属性
  var year = id_new.split('_')
  var start = ee.String(year.get(0)).cat(ee.String((year.get(1))))
  var end = ee.String(year.get(0)).cat(ee.String((year.get(2))))
  var date_start = ee.Date.parse('YYYYDDD', start)
  var date_end = ee.Date.parse('YYYYDDD', end)
  var date = date_end.millis()



  return img_m.set({'system:id':id_new})
                .set({'start_time':date_start})
                .set({'system:time_start':date})
                .set({'end_time':date_end})

}

var images_mosaic = images.map(img_mosaic)
print(images_mosaic)
Map.addLayer(images_mosaic, {}, "2016.37-2017.9")

var image_1 = images_mosaic.first()
print(image_1)
Map.addLayer(image_1, {}, "image_1")

// Export.table.toDrive({
//   image: image,
//   description: 'LST_2016_216_225',
//   folder: 'train001',
//   scale: 30,
//   maxPixels: 1e13,
//   crs: 'EPSG4326'
// })

var cliped = function(image){
  var img = image.select('LST')
              .multiply(0.00341802)
              .add(149)
              .subtract(273.5)
              .rename('LST')
              .copyProperties(image, ["system:time_start", "start_time", "end_time"])
  return img
}

var l8_lst = images_mosaic.map(cliped)
print('l8_lst', l8_lst)
// Map.addLayer(l8_lst, {}, 'l8_lst')


//clip time
var days = 10

var join = ee.Join.saveAll({
  matchesKey: 'images'
})

var diffFilter = ee.Filter.maxDifference({
  difference: 1000*60*60*24*days,
  leftField: 'system:time_start',
  rightField: 'system:time_start',
})

//
var joinedCollection = join.apply({
  primary: l8_lst,
  secondary: l8_lst,
  condition: diffFilter
});

//mean
var smoothedCollection = ee.ImageCollection(joinedCollection.map(function(image){
  var collection = ee.ImageCollection.fromImages(image.get('images'));
  return ee.Image(image).addBands(collection.mean().rename('moving_average'))
}))
print(smoothedCollection)
//show
var chart = ui.Chart.image.series({
  imageCollection: smoothedCollection.select(['LST', 'moving_average']),
  region: geometry,
  reducer: ee.Reducer.mean(),
  scale: 100
}).setOptions({
  lineWidth: 1,
  title: 'LST Time Series',
  interpolateNulls: true,
  vAxis: {title: 'LST'},
  hAxis: {title: '', format: 'YYYY-MMM'},
  series: {
    1: {color: 'red', lineWidth: 2},
    0: {color: 'gray', lineWidth:2},
  },
})
// print(chart)







// // 选择数据集并进行波段比例换算
// var month = ee.List.sequence(2, 12);
// var collectYear = ee.ImageCollection(month
//   .map(function(m) {
//     var start = ee.Date.fromYMD(2016, m, 1);
//     var end = start.advance(1, 'month');
//     var LST = l8_lst.select('LST')
//                   .filterDate(start, end)
//                   .map(function(image){
//                     return image.set(image.toDictionary(image.propertyNames()));
//                   }).mean().rename('LST').clip(inner)
//     var NDVI = ee.ImageCollection("MODIS/006/MOD13Q1")
//                   .filterDate(start, end)
//                   .select("NDVI")
//                   .map(function(image){
//                     return image.multiply(0.0001).set(image.toDictionary(image.propertyNames()))
//                   }).mean();
//     return LST.addBands(NDVI).set('month',m)
// }));
// print (collectYear);



















