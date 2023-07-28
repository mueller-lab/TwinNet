%% Clear data and devices

% Script to display forlder for testing
clearvars
close all
warning off


%% Input Parameters

srcpath = '/media/hmorales/Skynet/TwinNet/Medaka/testData/'; 
%srcpath = '/media/hmorales/Skynet/TwinNet/Stickleback/testData/';


d = dir(srcpath);
% remove all files (isdir property is 0)
dfolders = d([d(:).isdir]) ;
% remove '.' and '..' 
dfolders = dfolders(~ismember({dfolders(:).name},{'.','..'}));
NFolders = length(dfolders);

% for each experiment folder
for i = 1: NFolders

    ExperimentName = dfolders(i).name;
    % for each subfolder i.e. well folder
    d = dir(fullfile(srcpath, ExperimentName));
    subfolders = d([d(:).isdir]) ;
    subfolders = subfolders(~ismember({subfolders(:).name},{'.','..'}));
    
    for j = 1: length(subfolders)
        wellName = subfolders(j).name;
        % for each subsubfolder i.e. embryo folder
        d = dir(fullfile(srcpath, ExperimentName, wellName));
        subsubfolders = d([d(:).isdir]) ;
        subsubfolders = subsubfolders(~ismember({subsubfolders(:).name},{'.','..'}));

        for k = 1: length(subsubfolders)
            embryoName = subsubfolders(k).name;
            folderName = fullfile(srcpath, ExperimentName, wellName,embryoName);
            disp(['"' fullfile(srcpath, ExperimentName, wellName,embryoName) '/";'])
        end

    end

end