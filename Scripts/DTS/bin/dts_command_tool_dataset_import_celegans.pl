#!/usr/bin/perl

use strict;

use warnings;

use Path::Class;

use Data::Dump qw(pp);

=pod

   DESCRIPTION
 
     Script to import uncommon filenames, to adhere to rules in the DevTimeStudio software.

    function
    getSourceImageFromModel(model_)
    {
     	var loidstr = ("000" + model_.lo_id).substr(-3,3)

	return [ config1.pngRoot, "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png".arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );
    }

=cut

use Env qw($DTS_DIR_PROJECTS);

my $organism = 'CElegans';

print( "Copy/Import [${organism}] imageset into a common filename scheme.. begin\n" );

# ${DTS_DIR_PROJECTS}/${organism}/test_data_embryoImages/E001/img--A001--LO0001--E001.tif
my $rootSourceImages = dir( "${DTS_DIR_PROJECTS}/${organism}/test_data_embryoImages/" );
my $rootTargetImagesTIF = dir( "${DTS_DIR_PROJECTS}/${organism}/unified/TIFs" );
my $rootTargetImagesPNG = dir( "${DTS_DIR_PROJECTS}/${organism}/unified/PNGs" );
# find -name '*.tif' |perl -MPath::Class -ne 'chomp; $basename=file($_)->basename; $basename=~s/\.tif/.png/; printf qq{convert -- %s ${DTS_DIR_PROJECTS}/CElegans/unified/PNGs/-XY01--PO01/embryos/-XY01--PO01--E001/%s\n}, $_, $basename'|parallel



# ${DTS_DIR_PROJECTS}/${organism}/plots/2105--001--E001/2105--001--E001_sims_autoregression_gridZ.mat
my $rootSourceMat = dir( "${DTS_DIR_PROJECTS}/${organism}/plots" );
my $rootTargetMat = dir( "${DTS_DIR_PROJECTS}/${organism}/unified/MATs" );


my $flag_dryrun = 0;



print( "Copy/Import [${organism}] .. processing .. rootSourceImages: ", $rootSourceImages, " .\n" );
print( "Copy/Import [${organism}] .. processing .. rootTargetImages: ", $rootTargetImagesTIF, " .\n" );

my $rootSourceImagesGlobString = $rootSourceImages->file( "E001/*.tif" );

print( "Copy/Import [${organism}] .. processing .. rootSourceImagesGlobString: ", $rootSourceImagesGlobString, " .. begin\n" );

my @rootSourceImagesGlobArray = glob( $rootSourceImagesGlobString );

print( "Copy/Import [${organism}] .. processing .. rootSourceImagesGlobArray: ", length(@rootSourceImagesGlobArray), "\n" );

for my $source ( @rootSourceImagesGlobArray )
{
    print( "Copy/Import [${organism}] .. processing .. rootSourceImage glob entry, source: ", $source, "\n" );

    # ${DTS_DIR_PROJECTS}/${organism}/test_data_embryoImages/E001/img--A001--LO0001--E001.tif

#img0001.tif                   img0037.tif                   img0073.tif                   img0109.tif                   img--XY01--LO0035.tif         img--XY01--LO0071.tif         img--XY01--LO0107.tif         img--XY01--LO0143.tif         img--XY01--LO0179.tif
#img0002.tif                   img0038.tif                   img0074.tif                   img0110.tif                   img--XY01--LO0036.tif         img--XY01--LO0072.tif         img--XY01--LO0108.tif         img--XY01--LO0144.tif         img--XY01--LO0180.tif
#img0003.tif                   img0039.tif                   img0075.tif                   img--XY01--LO0001.tif         img--XY01--LO0037.tif         img--XY01--LO0073.tif         img--XY01--LO0109.tif         img--XY01--LO0145.tif         img--XY01--LO0181.tif
    
    my ($embryo_id, $well_id, $loidstr, $suffix)  = ($source =~ /\/(E\d+)\/img--(XY\d+)--(LO\d+)\.(.+)$/);

    next unless $well_id;
    
    # return [ config1.pngRoot, "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png".arg(model_.well_id).arg(loidstr).arg(model_.embryo_id) ].join( "/" );
    my $target_tif = $rootTargetImagesTIF->subdir( sprintf "-%s--PO01", $well_id )->subdir( "embryos" )->subdir( sprintf "-%s--PO01--%s", $well_id, $embryo_id )->file( sprintf "-%s--PO01--%s--CO6--%s.%s", $well_id, $loidstr, $embryo_id, $suffix );

    print( "Copy/Import [${organism}] .. processing .. rootSourceImage glob entry, target: ", $target_tif, "\n" );

    $target_tif->dir()->mkpath();
    
    my $command_copy = sprintf 'rsync -u "%s" "%s"', $source, $target_tif;
    
    if( ! -e $target_tif )
    {
	print( "Copy/Import [${organism}] .. processing .. copy cmd: ", $command_copy, "\n\n" );

	if( ! $flag_dryrun )
	{
	    qx{$command_copy};
	}
    }
    else
    {
	print( "Copy/Import [${organism}] .. processing .. target found .. skip", "\n\n" );
    }




    my $target_png = $rootTargetImagesPNG->subdir( sprintf "-%s--PO01", $well_id )->subdir( "embryos" )->subdir( sprintf "-%s--PO01--%s", $well_id, $embryo_id )->file( sprintf "-%s--PO01--%s--CO6--%s.%s", $well_id, $loidstr, $embryo_id, 'png' );

    $target_png->dir()->mkpath();
	    
    my $command_convert = sprintf qq{convert -- "%s" "%s"\n}, $target_tif, $target_png;

    print( "Copy/Import [${organism}] .. processing .. convert to PNG: ", $command_convert, "\n\n" );

    if( ! -e $target_png )
    {
	if( ! $flag_dryrun )
	{
	    print qx{$command_convert};
	}
    }
    else
    {
	print( "Copy/Import [${organism}] .. processing .. target found .. skip", "\n\n" );
    }

    
}

print( "Copy/Import [${organism}] .. processing .. rootSourceImagesGlobString: ", $rootSourceImagesGlobString, " .. end\n\n\n" );








print( "Copy/Import [${organism}] .. processing .. rootSourceMat: ", $rootSourceMat, ".\n" );

print( "Copy/Import [${organism}] .. processing .. rootTargeteMat: ", $rootTargetMat, ".\n" );

my $rootSourceMatGlobString = $rootSourceMat->file( "*/*_gridZ.mat" );

print( "Copy/Import [${organism}] .. processing .. rootSourceMatGlobString: ", $rootSourceMatGlobString, " .. begin\n" );

my @rootSourceMatGlobArray = glob( $rootSourceMatGlobString );

print( "Copy/Import [${organism}] .. processing .. rootSourceMatGlobArray: ", length(@rootSourceMatGlobArray), "\n" );

for my $source ( @rootSourceMatGlobArray )
{
    print( "Copy/Import [${organism}] .. processing .. rootSourceMat glob entry, source: ", $source, "\n" );

    # ${DTS_DIR_PROJECTS}/${organism}/plots/2105--001--E001/2105--001--E001_sims_autoregression_gridZ.mat
    #                             /plots/exp1--001--E001/exp1--001--E001_sims_autoregression_gridZ.mat
    
    my ($some_id, $rank_id, $embryo_id)  = ($source =~ /\/([^\/]+)--(\d+)--(E\d+)_sims_autoregression_gridZ.mat$/);

    # TN_similarities_0089--A003--PO01--E000.mat')

    my $target = $rootTargetMat->file( sprintf "TN_similarities_%s--A%s--PO01--%s.mat", $some_id, $rank_id, $embryo_id );

    print( "Copy/Import [${organism}] .. processing .. rootSourceMat glob entry, target: ", $target, "\n" );

    $target->dir()->mkpath();
    
    my $command_copy = sprintf 'rsync -u "%s" "%s"', $source, $target;
    
    if( ! -e $target )
    {
	print( "Copy/Import [${organism}] .. processing .. copy cmd: ", $command_copy, "\n\n" );

	qx{$command_copy};
    }
    else
    {
	print( "Copy/Import [${organism}] .. processing .. target found .. skip", "\n\n" );
    }
}

print( "Copy/Import [${organism}] .. processing .. rootSourceMatGlobString: ", $rootSourceMatGlobString, " .. end\n" );






print( "Copy/Import [${organism}] imageset into a common filename scheme.. done\n" );