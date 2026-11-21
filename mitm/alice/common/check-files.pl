$failed = 0;
for $file (@ARGV)
{
    open(FE,"perl file_exists.pl $file |") || die "Failed: $!\n";
    while ( <FE> )
    {
	if ($_ =~ /does not/)
	{
	    $failed = 1;
	}
    }
}
if (!$failed)
{
    print "All tests passed!\n";
}
