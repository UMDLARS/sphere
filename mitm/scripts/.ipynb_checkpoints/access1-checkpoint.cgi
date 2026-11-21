#!/usr/bin/perl -w

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use strict;

my $movie = "/var/sources/2.txt";
my $lineno = param('line');

print "Content-type: text/html\n\n";

if ($lineno) {
	open(SCRIPT,$movie) or die "Yaaargh!: $!";

	my $i = 0;
	foreach (<SCRIPT>) {
		$i++;

		if ($i < $lineno) {
			next;
		} elsif ($i == $lineno) {
			print "$_\n";
			exit 0;
		} elsif ($i > $lineno) {
			print "I pass the line? I'm freaking out. This has to be a BUG!";
			exit 0;
		}
	} 
}

print "XXX END OF LINE XXX\n";
exit 0;
