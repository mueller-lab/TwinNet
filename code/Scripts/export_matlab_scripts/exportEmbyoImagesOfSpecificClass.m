%% Clear data and devices

clearvars
close all
warning off


%% Input Parameters
srcpath = '/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Zebrafish/zebrafish_train_data/severity/Acquifer/BMP/'; %'/media/hmorales/Skynet/Toxin/'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Stickleback/stickleback_train_data/Normal/'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Zebrafish/zebrafish_test_data/test_data_2/'; %'/home/hmorales/WorkSpace/Development/TwinNetwork/KimmelNet/data/Zebrafish_ML_Archive/trainingData_segmented/'; %/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Zebrafish/zebrafish_train_data/zebrafish/Keyence/Normal/'; %'/media/hmorales/dcea2cc6-dec9-4aad-9261-535d1d200f33/EmbryoNetData/SourceData_MLpaper2022/Zebrafish/zebrafish_test_data/test_data_2/'; 
dstpath = '/media/hmorales/Skynet/TwinNet/Analysis_Figure3/segments_BMP_Acquifer/segments_NORMAL/'; %'/media/hmorales/Skynet/TwinNet/Stickleback/'; %/media/hmorales/Skynet/TwinNet/Figure3/segments/segments_RA_Megatron/';%'/media/hmorales/Skynet/TwinNet/NormalzfishKimmelNet/trainData/'; %
AnnotatorName = 'GT_json';%'Classified_result_1_json_class_agnostic'; %'GT_000back_json';%'AutoInitial000back_json'; %'GT_000back_json'; %'Johanna_json';
className = 'NORMAL'; %'UNKNOWN';
severity = 100; %"severe"
imageExt = { '*.jpg', '*.png'};% '*.tif',
EmbryoCount = 001;
maxImages = 10000;
minfractionImagesPerTrack = 1.0;
%ZeroPaddingEmbryos =4; -> Change in line 159

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
        jsonfolder = fullfile(wellpath, AnnotatorName);
        if isfolder(imgfolder)  && isfolder(jsonfolder)
            images = dir(fullfile(imgfolder, imageExt{1}));
            if isempty(images)
                images = dir(fullfile(imgfolder, imageExt{2}));
            end
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

                    if ~isempty(temp)
                        n1 = length(temp.id);
                        alltracks(nn:nn+n1-1) = temp.id;  
                        nn = nn+n1;
                    end
                end
                trackIds = unique(alltracks);  
                %get complete tracks
                countTrackPoints = zeros(length(trackIds),1);  
                positivetrackClasses = zeros(length(trackIds),1); 
                negativetrackClasses = zeros(length(trackIds),1); 

                for k = 3:Tmax
                    data = openjson(fullfile(jsonfolder, jsons(k).name));
                    if length(data.detection_list) > 1
                        temp = struct2table(data.detection_list);
                    else
                        temp = data.detection_list;
                    end
                    if ~isempty(temp)
                        trackIds_t = temp.id;  
                        class_t = temp.className;
                        severity_t = temp.severe;
                        for m = 1:length(trackIds_t)
                            idx = find(trackIds == trackIds_t(m));
                            if ~isempty(idx)
                                if length(trackIds_t) > 1
                                    currentclass = class_t{m,1};
                                    currentseverity = severity_t(m); 
                                else
                                    currentclass = class_t;
                                    currentseverity = severity_t; 
                                end
    
                                countTrackPoints(idx) = countTrackPoints(idx) + 1;
                                if (strcmp(currentclass, className) && currentseverity == severity)
                                    positivetrackClasses(idx) = positivetrackClasses(idx) + 1;
                                end
                                if strcmp(currentclass, 'CUT')
                                    negativetrackClasses(idx) = negativetrackClasses(idx) + 1;
                                end                           
                            end
                        end
                    end
                end
                
                countTrackPoints = countTrackPoints/(Tmax-2);
                idxSelected = (countTrackPoints >= minfractionImagesPerTrack) & (positivetrackClasses > 1) & (negativetrackClasses == 0);
                IdsCompleteTracks = trackIds(idxSelected);
                disp([num2str(length(IdsCompleteTracks)) ' ' className ' ' num2str(severity) ' complete tracks from ' num2str(length(trackIds)) ' ('  num2str(100*length(IdsCompleteTracks)/length(trackIds))  '%)' ])


                % create directory for output images of complete track
                tempEmbryoIds = zeros(length(IdsCompleteTracks),1);
                for k = 1: length(IdsCompleteTracks)
                    %outfolder = fullfile(dstpath, ExperimentName, wellName, ['E' num2str(IdsCompleteTracks(k),'%03.f')]);
                    outfolder = fullfile(dstpath, ExperimentName, wellName, ['E' num2str(EmbryoCount,'%03.f')]);
                    tempEmbryoIds(k) = EmbryoCount;
                    mkdir(outfolder)
                    EmbryoCount = EmbryoCount +1;
                end
                % export images for complete tracks
                
                initial_jsonName = jsons(3).name; % the first one from the tracking
                folderpath = fullfile(dstpath, ExperimentName, wellName);
                for k = 1:Tmax

                    temptempEmbryoIds = tempEmbryoIds;
                    if k > 2
                        data = openjson(fullfile(jsonfolder, jsons(k).name));
                    else
                        data = openjson(fullfile(jsonfolder, initial_jsonName));  % open the 3rd frame for the first two bounding boxes
                    end

                    if k > maxImages
                        continue
                    end

                    imageName = data.source_name; 
                    if ~strcmp(imageName , images(k).name)
                        imageName = images(k).name;
                    end
                    if length(data.detection_list) > 1
                        temp = struct2table(data.detection_list);
                    else
                        temp = data.detection_list;
                    end

                    if ~isempty(temp)

                        trackIds_t = temp.id;      
                        % open image
                        img = imread(fullfile(imgfolder, imageName));
                        [Y,X,C] = size(img);
                        for m = 1:length(trackIds_t)
                            idx = find(IdsCompleteTracks == trackIds_t(m));
                            if ~isempty(idx)
                                outName = ['img--' wellName '--LO'  num2str(k,'%03.f') '--E'  num2str(trackIds_t(m),'%03.f') '.tif' ];
                                %outfolder = fullfile(folderpath, ['E' num2str(trackIds_t(m),'%03.f')]);
                                outfolder = fullfile(folderpath, ['E' num2str(temptempEmbryoIds(idx),'%03.f')]);
                                x0 = min(temp.tlx(m)+1, temp.brx(m)+1);
                                y0 = min(temp.tly(m)+1, temp.bry(m)+1);
                                x1 = max(temp.tlx(m)+1, temp.brx(m)+1);
                                y1 = max(temp.tly(m)+1, temp.bry(m)+1);
                                if x1 > X
                                    x1 = X; 
                                end
                                if y1 > Y
                                    y1 = Y;
                                end
                                croppedimage = img(y0:y1, x0:x1, :);
                                imwrite(croppedimage,fullfile(outfolder, outName))
                            end
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

disp([num2str(EmbryoCount) ' embryos extracted'])