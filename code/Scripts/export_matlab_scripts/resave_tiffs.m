%% Clear data and devices

clearvars
close all
warning off


%% Input Parameters

srcfolder = '/media/hmorales/Skynet/TwinNet/CElegans_celldynamicsorg/testData/Pronuclear_migration/A001/temp/';
dstfolder = '/media/hmorales/Skynet/TwinNet/CElegans_celldynamicsorg/testData/Pronuclear_migration/A001/E001/';
imageExt = '*.jpg';
imageExtOut = '.tif';

images = dir(fullfile(srcfolder, imageExt));

N = length(images);

for i = 1: N


    if mod(i,10) == 0
        disp(['Image ' num2str(i) ' from ' num2str(N)])
    end

    img = imread(fullfile(srcfolder, images(i).name));
    temp = split(images(i).name, '.');

    imwrite(img,fullfile(dstfolder, [temp{1} imageExtOut]));

end