# Two arguments, experiment and project name
CPATH="/share/education/common"
echo "Path $CPATH"
echo "Checking files"
cd $CPATH; scp -r * attacker:/tmp
ssh -o stricthostkeychecking=no attacker "cd /tmp; /usr/bin/perl check-files.pl /bin/flooder; rm /tmp/index.html; wget server -o /tmp/index.html; /usr/bin/perl check-files.pl /tmp/index.html"
