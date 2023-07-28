%% Clear data and devices

clearvars
close all
warning off


%% Input Parameters
datasource = '/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Stickleback/stickleback_test_data/Normal'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Zebrafish/zebrafish_train_data/zebrafish/Keyence/Normal';%'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Stickleback/stickleback_train_data/Normal/'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Medaka/medaka_train_data/Normal';%'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Stickleback/stickleback_test_data/Normal'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Stickleback/stickleback_train_data/Normal/';

srcpath = fullfile(datasource, '/Stickleback/stickleback_test_data/Normal');
dstpath = '/media/hmorales/Skynet/TwinNet/SticklebackShort/testData/';%'/media/hmorales/Skynet/TwinNet/testNormalzfish';%'/media/hmorales/Skynet/TwinNet/Stickleback/trainData/';%'/media/hmorales/Skynet/TwinNet/Medaka/trainData/'; %'/media/hmorales/Skynet/TwinNet/Stickleback/testData/';%'/media/hmorales/Skynet/TwinNet/Stickleback/trainData/';
imageExt = '*.jpg';
maxImages = 600;

%% Export tiffs

% Get the folder contents
d = dir(srcpath);
% remove all files (isdir property is 0)
dfolders = d([d(:).isdir]) ;
% remove '.' and '..' 
dfolders = dfolders(~ismember({dfolders(:).name},{'.','..'}));
NFolders = length(dfolders);

% for each experiment folder
for i = 1: NFolders

    % for each subfolder i.e. well folder
    d = dir(fullfile(srcpath, dfolders(i).name));
    subfolders = d([d(:).isdir]) ;
    subfolders = subfolders(~ismember({subfolders(:).name},{'.','..'}));
    ExperimentName = dfolders(i).name;
    for j = 1: length(subfolders)

        wellName = subfolders(j).name;
        wellpath = fullfile(srcpath, ExperimentName, wellName);
        imgfolder = fullfile(wellpath, 'images');
        jsonfolder = fullfile(wellpath, 'Classified_result_1_json_class_agnostic');
        if isfolder(imgfolder)  && isfolder(jsonfolder)
            images = dir(fullfile(imgfolder, imageExt));
            jsons = dir(fullfile(jsonfolder, '*.json'));

            if length(images) == length(jsons)

                disp(['Exporting : ' wellpath])
                % extract only complete embryo tracks
                Tmax = length(jsons);
                %get all tracks
                alltracks = [];
                nn = 1;
                for k = 3:Tmax
                    data = openjson(fullfile(jsonfolder, jsons(k).name));
                    if length(data.detection_list) > 1
                        temp = struct2table(data.detection_list);
                    else
                        temp = data.detection_list;
                    end
                    n1 = length(temp.id);
                    alltracks(nn:nn+n1-1) = temp.id;  
                    nn = nn+n1;
                end
                trackIds = unique(alltracks);  
                %get complete tracks
                countTrackPoints = zeros(length(trackIds),1);     
                for k = 3:Tmax
                    data = openjson(fullfile(jsonfolder, jsons(k).name));
                    if length(data.detection_list) > 1
                        temp = struct2table(data.detection_list);
                    else
                        temp = data.detection_list;
                    end
                    trackIds_t = temp.id;  
                    for m = 1:length(trackIds_t)
                        idx = find(trackIds == trackIds_t(m));
                        if ~isempty(idx)
                            countTrackPoints(idx) = countTrackPoints(idx) + 1;
                        end
                    end
                end
                
                countTrackPoints = countTrackPoints/(Tmax-2);
                IdsCompleteTracks = trackIds(countTrackPoints ==1);
                disp([num2str(length(IdsCompleteTracks)) ' complete tracks from ' num2str(length(trackIds)) ' ('  num2str(100*length(IdsCompleteTracks)/length(trackIds))  '%)' ])

                % create directory for output images of complet track                              
                for k = 1: length(IdsCompleteTracks)
                    outfolder = fullfile(dstpath, ExperimentName, wellName, ['E' num2str(IdsCompleteTracks(k),'%03.f')]);
                    mkdir(outfolder)
                end
                % export images for complete tracks
                
                initial_jsonName = jsons(3).name; % the first one from the tracking
                folderpath = fullfile(dstpath, ExperimentName, wellName);
                parfor k = 1:Tmax

                    if k > 2
                        data = openjson(fullfile(jsonfolder, jsons(k).name));
                    else
                        data = openjson(fullfile(jsonfolder, initial_jsonName));  % open the 3rd frame for the first two bounding boxes
                    end

                    if k > maxImages
                        continue
                    end

                    imageName = data.source_name; 
                    if length(data.detection_list) > 1
                        temp = struct2table(data.detection_list);
                    else
                        temp = data.detection_list;
                    end
                    trackIds_t = temp.id;  

                    % open image
                    img = imread(fullfile(imgfolder, imageName));
                    for m = 1:length(trackIds_t)
                        idx = find(IdsCompleteTracks == trackIds_t(m));
                        if ~isempty(idx)
                            outName = ['img--' wellName '--LO'  num2str(k,'%04.f') '--E'  num2str(trackIds_t(m),'%03.f') '.tif' ];
                            outfolder = fullfile(folderpath, ['E' num2str(trackIds_t(m),'%03.f')]);
                            x0 = temp.tlx(m)+1;
                            y0 = temp.tly(m)+1;
                            x1 = temp.brx(m)+1;
                            y1 = temp.bry(m)+1;
                            croppedimage = img(y0:y1, x0:x1, :);
                            imwrite(croppedimage,fullfile(outfolder, outName))
                        end
                    end

                end



            else
                disp('Image and json number do not match')
                disp(imgfolder)
            end
        end
    end











end