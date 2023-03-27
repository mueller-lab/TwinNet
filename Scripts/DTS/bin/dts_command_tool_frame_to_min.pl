#!/usr/bin/perl

use Env qw(BASE_VALUE TIME_FACTOR_MIN);

unless( $BASE_VALUE )
{
    $BASE_VALUE=0
}

unless( $TIME_FACTOR_MIN )
{
    $TIME_FACTORY_MIN=1
}

for( @ARGV )
{
    printf( "frame %-5s = %2.f min\n", $_, ( ($_ * $TIME_FACTOR_MIN) + $BASE_VALUE ) );
}
