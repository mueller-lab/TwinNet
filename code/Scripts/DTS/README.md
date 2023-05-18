# NAME

dts - developmental time studio

# DESCRIPTION

This is a custom software package to study **cosine similarity** matrices of image sequences. It contains the &lt;dts> commandline tool to import and prepare the matrices/images. 
There is a comprehensive user-interface to browse the results, and explore the images underlying the matrices. 

# INSTALLATION INSTRUCTIONS

## MacOS (Tested: catalina using bash)

Installation instructions

### 1. Install brew : follow the installation instructions at https://docs.brew.sh/Installation

### 2. Use brew to install python3 and pip3
```
    $ brew install python3
    $ brew install pip3
```

### 3. Install qt   : follow the installation instruction at https://www.qt.io/download
We require the qml tool, to load the ui-app later.

### 4. Configure/edit the example-data folder location variables in $DTS_DIR/system/contexts/example-dataset/.bash_context

### 5. Activate the <dts> command (required after each new shell session)
```
    $ source system/objects/dts/install/.bash_context 

    # or persistantly install

    $ dts call system/objects/dts/install system/contexts/installation/macos
```

### 6. Either, rebuild all example-data sets (takes some while):
```
    $ dts invoke objects/example-dataset/rebuild contexts/example-dataset/*1
```

### 7. Or, rebuild one sample in the example-data set (zebrafish1, medakashort1, celegans1, stickleback1):
```
    $ dts call system/objects/example-dataset/rebuild system/contexts/example-dataset/zebrafish1
```

### 8. All commands of dts are documented in its manual-page. Install the manpages globally:
```
    $ dts call maninstall
    $ man dts
```

## Ubuntu (Tested: 22.04 using bash)

### 1. Install prerequisite packages
```
    $ sudo apt install -y perl-doc qml-qt6 python-is-python3
```

### 2. Configure/edit the example-data folder location variables in $DTS_DIR/system/contexts/example-dataset/.bash_context

### 3. Install the python3 packages
```
    $ pip3 install matplotlib
    $ pip3 install scipy
```

### 4. Activate the <dts> command (required after each new shell session)
```
    $ source system/objects/dts/install/.bash_context 
```

### 5. Either, rebuild all example-data sets (takes some while):
```
    $ dts invoke system/objects/example-dataset/rebuild contexts/example-dataset/*1

    # or persistantly 

    $ dts call system/objects/dts/install system/contexts/installation/ubuntu
```

### 6. Or, rebuild one sample in the example-data set (zebrafish1, medakashort1, celegans1, stickleback1):
```
    $ dts call system/objects/example-dataset/rebuild system/contexts/example-dataset/zebrafish1
```

### 7. All commands of dts are documented in its manual-page. Call:
```
    $ dts man
```

# DIRECTORIES
```
    code/     - Python code proper
    bin/      - contains all executable tools 
    ui/       - app to inspect a prepared/build dataset (live-view of embryo images requires presence of segmented images)
    system/   - configuration and instruction files 
```

# MANPAGES

Read instructions at doc/dts/internal to writeout system manpages. These are:

    dts(1), dts-help(1), dts-usage(1), dts-readme(1), dts-example_dataset-0001(1)

# USAGE
```
    $ dts usage
```

# AUTHOR

    Murat Uenalan <murat.uenalan@uni-konstanz.de>
