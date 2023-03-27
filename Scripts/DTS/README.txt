NAME
    dts - developmental time studio

DESCRIPTION
    This is a custom software package to study b<cosine similarity> matrices
    of image sequences. It contains the <dts> commandline tool to import and
    prepare the matrices/images. There is a comprehensive user-interface to
    browse the results, and explore the images underlying the matrices.

INSTALLATION INSTRUCTIONS
  MacOS
    Installation instructions

       1. Install brew : follow the installation instructions at https://docs.brew.sh/Installation

         $ brew install python3
         $ brew install pip3

       2. Install qt   : follow the installation instruction at https://www.qt.io/download

       3. Unpack the data/ folder, containing the example-dataset

          $ unzip data.zip

       4. Activate the <dts> command (required after each new shell session)

          $ source objects/dts/install/.bash_context 

       5. Display the <dts> manpage

          $ dts man

       6. Rebuild all example-data sets (takes some while)

          $ dts invoke objects/example-dataset/rebuild contexts/example-dataset/*1

  Ubuntu 22.04
       1. Install prerequisite packages

          $ sudo apt install -y perl-doc qml-qt6 python-is-python3

       2. Unpack the data/ folder, containing the example-dataset

          $ unzip data.zip

       3. Install the python3 packages

          $ pip3 install matplotlib
          $ pip3 install scipy

       4. Activate the <dts> command (required after each new shell session)

          $ source objects/dts/install/.bash_context 

       5. Display the <dts> manpage

          $ dts man

       6. Rebuild all example-data sets (takes some while)

          $ dts invoke objects/example-dataset/rebuild contexts/example-dataset/*1

DIRECTORIES
      code/     - PYTHON3 code proper
      bin/      - contains tools to import datasets, service the package, and build plots for inspection/quality-control of the matrices 
      ui/       - app to inspect a prepared/build dataset (live-view of embryo images requires additional installation of the dataset)
      data.zip  - zip file containing the data/ folder, containing the example-dataset
      contexts/ - configuration files 
      objects/  - instruction files

MANPAGE
     dts man

USAGE
     dts usage

AUTHOR
    Murat Uenalan <murat.uenalan@uni-konstanz.de>

