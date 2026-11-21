# Ensure that the /tmp files aren't removed before running this script.
# You can check this by going into the install script and making sure that "rm -rf" isn't commented out toward the end of the script.

echo "Path $CPATH"
NODE=alice
CPATH="/tmp/$NODE/common"
echo "=====> Checking Alice"
echo "Checking installed programs"
ssh -o stricthostkeychecking=no alice "cd $CPATH; /usr/bin/perl check-installed.pl elinks links wget netcat nmap curl telnetd libcgi-pm-perl"
echo "Checking files"
ssh -o stricthostkeychecking=no alice "cd $CPATH; sudo /usr/bin/perl check-files.pl /usr/local/bin/linechoose.pl /usr/lib/cgi-bin/access1.cgi /usr/lib/cgi-bin/access2.cgi"
echo "Checking processes"
ssh -o stricthostkeychecking=no alice "cd $CPATH; /usr/bin/perl check-processes.pl apache2 stockpost.pl"
NODE=bob
CPATH="/tmp/$NODE/common"
echo "=====> Checking Bob"
echo "Checking installed programs"
ssh -o stricthostkeychecking=no bob "cd $CPATH; /usr/bin/perl check-installed.pl elinks links wget netcat nmap curl libcgi-pm-perl"
echo "Checking files"
ssh -o stricthostkeychecking=no bob "cd $CPATH; sudo /usr/bin/perl check-files.pl /usr/local/bin/a1start.sh /usr/local/bin/a2start.sh  /usr/local/bin/telnet.pl  /usr/local/bin/telstart.sh /usr/lib/cgi-bin/stock.* /var/www/html/index.html"
echo "Checking processes"
ssh -o stricthostkeychecking=no bob "cd $CPATH; /usr/bin/perl check-processes.pl telstart.sh a1start.sh a2start.sh"
NODE=eve
CPATH="/tmp/$NODE/common"
echo "=====> Checking Eve"
echo "Checking installed programs"
ssh -o stricthostkeychecking=no eve "cd $CPATH; /usr/bin/perl check-installed.pl curl ettercap tshark hexedit"
echo "Checking files"
ssh -o stricthostkeychecking=no eve "cd $CPATH; sudo /usr/bin/perl check-files.pl /root/remote.ef /usr/bin/chaosreader"
cmd="curl -s alice/cgi-bin/access1.cgi"
ssh -o stricthostkeychecking=no eve "perl $CPATH/check-output.pl '${cmd}' 'END OF LINE'"
cmd="curl -s bob/cgi-bin/stock.cgi"
ssh -o stricthostkeychecking=no eve "perl $CPATH/check-output.pl '${cmd}' 'FrobozzCo'"


