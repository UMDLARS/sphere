#!/usr/bin/perl -w

use strict;

my $filename = $ARGV[0];
my $linenum = $ARGV[1];
my $sleepytime = $ARGV[2];

open(SCRIPT,$filename) or die "Yaaargh!: $!";

my $i = 0;
foreach (<SCRIPT>) {
  $i++;
  if ($i < $linenum) {
	next;
  } elsif ($i == $linenum) {
	print "$_\n";
  } elsif ($i > $linenum) {
	last;
  }
  sleep($sleepytime) if $sleepytime;
} 

