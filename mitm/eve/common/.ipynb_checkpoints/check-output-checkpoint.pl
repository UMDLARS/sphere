$found = 0;
while (@ARGV)
{
    $prog = shift(@ARGV);
    $out = shift(@ARGV);
    print "Checking program $prog for output $out\n";
    open(FE,"$prog |") || die "Failed: $!\n";
    while ( <FE> )
    {
	if ($_ =~ /$out/)
	{
	    $found = 1;
	}
    }
    if (!$found)
    {
	print "Program $prog did not produce output $out\n";
    }
}
if ($found)
{
    print "All tests passed!\n";
}
