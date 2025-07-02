all: celp flooder 

clean:
	rm -f celp flooder 

celp: celp.c 
	g++ celp.c -o celp

flooder: flooder.c 
	g++  flooder.c -lnet -lm -lpcap -fpermissive -o flooder

