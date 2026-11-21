#!/usr/bin/perl -w

use strict;
use Net::Telnet;

my $timeout = 60;
my $steps = 20;
my $sleep = 5;
my %users = (
	jimbo => 'goofy76',
	jambo => 'minnie77',
	jumbo => 'donald78',);
my @tempkeys = keys(%users);
my $user = $tempkeys[rand @tempkeys];
print "My user: '$user'\n";
print "My pass: '$users{$user}'\n";

my $telnet = new Net::Telnet ( 
	Timeout=>$timeout, 
	Errmode=>'die'
);

#Prompt=> '/.+\$ $/i'

print "Trying to log in via telnet...\n";
$telnet->open('alice-lan0');
$telnet->waitfor('/login: $/i');
$telnet->print($user);
$telnet->waitfor('/password: $/i');
$telnet->print($users{$user});
#$telnet->login($user, $users{$user});
$telnet->cmd('screen');
$telnet->cmd('');
$telnet->cmd('cd /usr');

my $step;
print "Looping over commands...\n";

for ($step = 0; $step <= $steps; $step++) {

	# my @ls = $telnet->cmd('ls -d *');
	# print "@ls\n";
	my @choices;
	# foreach (@ls) {
	#	my @temp = split(/\s+/i, $_);
	#	foreach (@temp) {
	#		$_ = "cd $_";
	#	}
	#	@choices = (@choices, @temp);
	# }
	push(@choices, 
	     "cd .", 
	     "cd /usr",
	     "cd",
	     "find . -xdev",
	     "who",
	     "ls -alh",
	     "ps aux",
	     "ls ..",
	     "du -xsh .",
	     "uname -a",
	     "uptime",
	);
	my $choice = $choices[rand @choices];
	#foreach (@choices) {
	#	print "'$_' ";
	#}
	#print "\n";
	print "action: $choice\n";
	$telnet->cmd($choice);
	sleep(rand $sleep);
}
