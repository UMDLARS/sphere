CPATH="/share/education"
echo "Path $CPATH"
echo "Checking files"
cd $CPATH; scp -r common pass:/tmp
ssh -o stricthostkeychecking=no pass "cd /tmp/common; /usr/bin/perl check-installed.pl john"
ssh -o stricthostkeychecking=no pass "cd /tmp/common; /usr/bin/perl check-files.pl /var/passwords"
