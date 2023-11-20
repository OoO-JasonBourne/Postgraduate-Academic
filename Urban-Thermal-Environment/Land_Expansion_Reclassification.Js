


// 加载影像
var img = ee.Image('users').clip(roi)

var re_class=img.remap([1,2,3,4,5,6,7,8,9],
                       [2,3,3,3,4,4,1,1,4]) ;

print('re_class', re_class)
Map.addLayer(re_class, {}, 're_class')


Export.image.toDrive({
  image: re_class,
  description: "CLCD_ShangHai_2001",
  folder: "CLCDCol_0625",
  scale: 30,
  region: roi,
  crs: 'EPSG:4326',
  maxPixels: 1e13
})

img = re_class



// //着色
//不透水表面
var IS = img.eq(1)
var IS_mask = IS.mask(IS)
Map.addLayer(IS_mask, {palette: '#FF0000'}, '不透水表面')


//森林草地
var Farmland = img.eq(3)
var Farmland_mask = Farmland.mask(Farmland)
Map.addLayer(Farmland_mask, {palette: '#daa520'}, '森林草地')

//水体
var Water = img.eq(4)
var Water_mask = Water.mask(Water)
Map.addLayer(Water_mask, {palette: '#0000FF'}, '水体')

//耕地
var Bare = img.eq(2)
var Bare_mask = Bare.mask(Bare)
Map.addLayer(Bare_mask, {palette: '#696969'}, '耕地')

// 计算影像中区域的像元数量
var pixelCount = img.reduceRegion({
  reducer: ee.Reducer.count(),
  geometry: roi,
  scale: 200, // 分辨率（米/像素）
}).get("remapped");

// 计算像元百分比函数
var countFun = function(image, all){
  var countCur = image.reduceRegion({
  reducer: ee.Reducer.count(),
  geometry: roi,
  scale: 200, // 分辨率（米/像素）
}).get("remapped");
  return ee.Number(countCur).divide(ee.Number(all))
}

// IS像元百分比
var ISCount = countFun(IS_mask, pixelCount)
// 打印结果
print('IS像元数量:', ISCount);

// 耕地像元百分比
var cropCount = countFun(Bare_mask, pixelCount)
// 打印结果
print('耕地像元百分比:', cropCount);

// 森林草地像元百分比
var FarmlandCount = countFun(Farmland_mask, pixelCount)
// 打印结果
print('森林草地像元数量:', FarmlandCount);


// 水体像元百分比
var waterCount = countFun(Water_mask, pixelCount)
// 打印结果
print('水体像元百分比:', waterCount);




