# Supply one argument, path to file/dir to check

$file=$ARGV[0];
if (-e $file)
{
    print "$file exists\n";
}
else
{
    print "$file does not exist\n";
}
