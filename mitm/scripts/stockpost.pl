#!/usr/bin/perl -w

use Digest::MD5 qw(md5_hex);

$host = "bob-lan0";

@symbols = qw(FZCO
	      ZBOR
	      MSFT
	      FFFF
	      DNGL
	      ASDF
	      B1FF);

while (1) {

	$pview = int rand(10);
	$price = int rand(100);

	$sym = $symbols[rand ($#symbols + 1)];
	$price = int rand 100;
	$hash = md5_hex($sym . $price);

	print "stock: $sym; \$$price; $hash\n";
	if ($pview <= 6) {
		$cmd = "curl http://$host/cgi-bin/stock.cgi?symbol=$sym\\&new=$price\\&hash=$hash"; 
	} else {
		$cmd = "curl http://$host/cgi-bin/stock.cgi"; 
	}
	print "command: $cmd\n";
	$result = `$cmd`;
	sleep(int rand 10);
}
