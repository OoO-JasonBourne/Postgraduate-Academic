clc;

clear;

% 基于Sen的趋势值

[a,R]=geotiffread('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\Wet-VPD\19801.tif'); %先导入投影信息

info=geotiffinfo('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\Wet-VPD\19801.tif');%先导入投影信息

[m,n]=size(a);

datasum=zeros(m*n,20)+NaN;

k=1;

for year=2001:2020 %起始年份

  filename=['LST_',int2str(year),'.tif'];

  mkdata=importdata(filename);

  mkdata=reshape(mkdata,m*n,1);

  datasum(:,k)=mkdata; 

  k=k+1;

end

trend=zeros(m,n)+NaN;                                                                                                                

for i=1:size(datasum,1)

  mkdata=datasum(i,:);

  if min(mkdata)>0

      valuesum=[];

      for k1=2:20

          for k2=1:(k1-1)

              cz=mkdata(k1)-mkdata(k2);

              j1=k1-k2;

              value=cz./j1;

              valuesum=[valuesum;value];

          end

      end

      value=median(valuesum);

      trend(i)=value;

  end

end

filename = ['C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\检验结果\基于sen的频数变化趋势.tif']

geotiffwrite(filename,trend,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag); %注意修改路径

% MK趋势显著性检验

p=1;

for year=2001:2020 %起始年份

  filename=['C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\Wet-VPD\',int2str(year),'1.tif'];

  mkdata=importdata(filename);

  mkdata=reshape(mkdata,m*n,1);

  datasum(:,p)=mkdata; 

  p=p+1;

end

sresult=zeros(m,n)+NaN

for i=1:size(datasum,1)

    mkdata=datasum(i,:);

  if min(mkdata)>0 % 有效格点判定

  sgnsum=[];

  for k=2:20

      for j=1:(k-1)

          sgn=mkdata(k)-mkdata(j);

          if sgn>0

              sgn=1;

          else

              if sgn<0

                  sgn=-1;

              else

                  sgn=0;

              end

          end

          sgnsum=[sgnsum;sgn];

      end

  end

   add=sum(sgnsum);

   sresult(i)=add;

  end

end

  vars=20*(20-1)*(2*20+5)/18;

  zc=zeros(m,n)+NaN;

  sy=find(sresult==0);

  zc(sy)=0;

  sy=find(sresult>0);

  zc(sy)=(sresult(sy)-1)./sqrt(vars);

  sy=find(sresult<0);

  zc(sy)=(sresult(sy)+1)./sqrt(vars);

  geotiffwrite('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\检验结果\MK趋势检验Z值.tif',zc,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag); %注意修改路径

% sen+mk趋势检验结果

  mkdata=importdata('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\检验结果\MK检验结果.tif');

  sen_value=importdata('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\检验结果\基于sen的频数变化趋势.tif');

  sen_value(abs(mkdata)<1.96)=NaN; %MK结果值高于1.96则认为通过了显著性95%

geotiffwrite('C:\Users\smv16\Desktop\栅格数据\Wet-VPD-xianzhu\检验结果\通过显著性95%的MK+sen趋势分析结果.tif',sen_value,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);%注意修改路径