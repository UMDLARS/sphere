$failed = 0;
for $pack (@ARGV)
{
    print "Checking for $pack\n";
    open(FE,"dpkg -l | grep $pack | wc | ") || die "Failed: $!\n";
    while ( <FE> )
    {
	@items = split /\s+/, $_;
	if ($items[1] == 0)
	{
	    print "$pack does not exist\n";
	    $failed = 1;
	}
    }
}
if (!$failed)
{
    print "All tests passed!\n";
}
