#!/usr/bin/perl -w

use strict;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5 qw(md5_hex);

my $blocknum = 10;
	my $symbol = 0;
	my $name = 1;
	my $about = 2;
	my $data = 3;


print header();
print start_html();
my @PS;
my @res = qw("foo", "bar");
while ($#res >= 1) {
	@PS = `ps aux`;
	@res = grep(/\/usr\/bin\/perl -w .+stock.cgi/, @PS);
	$blocknum--;
	if ($#res <= 1) { last; }
	print "($blocknum) Waiting for other process to close?...\n";
	sleep(1);
	if ($blocknum <= 0) {
		print h1("Try again later.");
		print end_html();
		exit(0);
	}
}

if (param('symbol') && param('new')) {
	print h4("Got symbol: '" . param('symbol'). "'");
	print h4("Adding new figure: '". param('new') . "'");

	my $hash;
	my $tmp;
	my $sym = param('symbol');
	chomp($sym);
	my $new = param('new');
	int(chomp($new));
	my $hash;
	if (param('hash')) {
		$hash = param('hash');
		chomp($hash);
	} else {
		$hash = ""; # none supplied
	}
	my $computed = md5_hex($sym . $new);
	if ($computed ne $hash) {
		print h1("PROTOCOL ERROR!");
		print h2("Cryptographic stamp incorrect.\n");
		print h3("Stock price update ($sym; $new) rejected.");
		print h2("<a href='/cgi-bin/stock.cgi'>Reload</a>");
		print end_html();
		exit 0;

	}

	
	open (DATA,'stock.data');
	my @data;
	while (<DATA>) {
		$tmp = $_; #each line of data
		if (($tmp =~ /^#.*/)||($tmp =~ /^\s*$/)) {
			push @data, $tmp;
			# skip comments or whitespace
		} else {
			my @row = split(/\t/, $tmp);
			if ($row[$symbol] eq $sym) { # we're going to update this row
				push (@row, $new);
				if (scalar @row > 18) { # 3 elements for name etc
				    splice(@row, 3, scalar @row - 18);
				}
			}
			foreach (@row) {
				$_ =~ s/\n*$//; # remove any trailing newlines from each item
			}
			$tmp = join("\t", @row);
			push @data, "$tmp\n"; # add one newline
		}	
	}
	close DATA;
	open (DATA, '>stock.data');
	foreach (@data) {
		print DATA $_;
	}
	close DATA;
	print h1("Data accepted.");
	print h2("<a href='/cgi-bin/stock.cgi'>Reload</a>");
	print end_html();
	exit 0;
	
}


print h1("A Real Stock Exchange");
print hr();
open (DATA,"stock.data");
while (<DATA>) {
	if ($_ =~ /^#.*$/) {
		next;
	}
	chomp($_);
	my @row = split(/\t/, $_);
	print h2("$row[$name] ($row[$symbol])");
	print h3("<i>$row[$about]</i>");
	print h3("Current price: \$$row[$#row]");
	my $longest = 0;
	shift @row;
	shift @row;
	shift @row;

	foreach (@row) {
		if ($_ > $longest) {
			$longest = $_;
		}
	}
	print "<table bgcolor='#aaaaff' border='0'><tr><td>\n";
	print "<table border='1' height='200'><tr>\n";
	my $i = 0;
	for ($i; $i <= $#row; $i++) {
		
		print "<td valign='bottom'><table border='1' bgcolor='#aa0000' align='left' valign='bottom' height='", $row[$i] * 2, "' width='50'><tr><td><p align='center'>\$$row[$i]</p></td></tr></table></td>\n";
		
	}
	print "</tr></table>\n";
	print "</td></tr></table>\n";

}
print hr();
close DATA;
print end_html();
exit 0;
