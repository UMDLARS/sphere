$found = 1;
for $proc (@ARGV)
{
    print "Checking for $proc\n";
    open(FE,"ps axuw | grep $proc |") || die "Failed: $!\n";
    $f = 0;
    while ( <FE> )
    {
	if ($_ =~ /$proc/ && $_ !~ /grep/ && $_ !~ /check/)
	{
	    $f = 1;
	}
    }
    if (!$f)
    {
	print "$proc not running\n";
    }
    $found = $found & $f;
}
if ($found)
{
    print "All tests passed!\n";
}
