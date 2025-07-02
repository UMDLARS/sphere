/*
 * Copyright (C) 2007 SPARTA, Inc.
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 */

#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/poll.h>
#include <sys/time.h>

unsigned char buf[4096];
int pkt_interval = 100000;
int payload_len = 28;
int use_voip = 0;

#define CELP_PKTLEN 28

void usage(const char *appname)
{
    printf("usage: %s -p PEERIP [ -sV ] [ -S usecs ] [ -l LEN ]\n\n", appname);
    puts  ("sender options:");
    puts  ("  -s           act as sender");
    puts  ("  -S usecs     sleep for this many microseconds between packets");
    puts  ("  -n NUMPKTS   send a specific number of packets then stop");
    puts  ("  -l LEN       use a payload of LEN bytes");
    puts  ("  -V           use voip ports");
    exit(1);
}

void sender(int fd, u_int32_t max_packets)
{
    u_int32_t seqno = 1;
    int rv;
    u_int32_t j = 0;
    struct timeval now;

    memset(buf + 4, 0, payload_len - 4);
    do {
	gettimeofday(&now, 0 );

	/* record sequence number */
	buf[0] = (seqno >> 24) & 0xff;
	buf[1] = (seqno >> 16) & 0xff;
	buf[2] = (seqno >> 8) & 0xff;
	buf[3] = (seqno) & 0xff;
	/* record timestamp - 1 byte of seconds, 4 bytes of microseconds */
	buf[4] = now.tv_sec & 0xff;
	buf[5] = (now.tv_usec >> 24) & 0xff;
	buf[6] = (now.tv_usec >> 16) & 0xff;
	buf[7] = (now.tv_usec >> 8) & 0xff;
	buf[8] = (now.tv_usec) & 0xff;

	rv = send(fd, buf, payload_len, 0);
	if (rv == -1)
	{
	    perror("send");
	    return;
	}
	seqno++;

	usleep(pkt_interval);
	j++;
    } while (max_packets == 0 || j < max_packets);
}

void receiver(int fd)
{
    struct pollfd p;
    int rv;
    int numpkts = 0;
    u_int32_t seqno;
    u_int32_t seqno_max = 0;
    u_int32_t seqno_start = 0;
    int delay = 0; /* microsecond counter */
    int delta;
    struct timeval now;
    struct timeval when;
    int to;

    p.fd = fd;
    p.events = POLLIN;
    
	gettimeofday(&now, 0);
	when.tv_sec = now.tv_sec + 1;
	when.tv_usec = now.tv_usec;

    while(1)
    {
	gettimeofday(&now, 0);

	/* calculate the next timeout */
	to = (when.tv_sec - now.tv_sec)*1000 + (when.tv_usec - now.tv_usec)/1000;
	if (to <= 0)
		rv = 0;
	else
		rv = poll(&p, 1, to);
	if (rv == -1)
	{
	    perror("poll");
	    break;
	}
	else if (rv == 0)
	{
	    /* timeout - print stats */
	    if (seqno_start > 0)
	    printf("%d / %d packets received, %0.1f msec average RTT (est)\n",
		    numpkts, seqno_max - seqno_start + 1,
		    (double)(delay / 1000.0 / numpkts * 2.));
	    else
		puts("0 / 0 packets received");
	    fflush(stdout);

	    /* reset */
	    numpkts = 0;
	    seqno_start = 0;
	    delay = 0;
	    when.tv_sec++;
	}
	else
	{
	    gettimeofday(&now, 0);
	    rv = recv(fd, buf, sizeof(buf), 0);
	    if (rv == -1)
	    {
		perror("recv");
		return;
	    }
	    /* read the sequence number from the packet */
	    seqno = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3];
	    /* keep track of the highest sequence number seen so far */
	    if (seqno_start == 0)
	    {
		seqno_start = seqno;
		seqno_max = seqno;
	    }
	    else if (seqno > seqno_max)
	    {
		seqno_max = seqno;
	    }
	    numpkts++;

	    /* calculate 1-way delay */
	    delta = ((now.tv_sec & 0xff) - buf[4]) * 1000000;
//	    printf("delta=%d\n",delta);
	    delay += delta;
	    delay += now.tv_usec;
	    delta = (buf[5]<<24) | (buf[6]<<16) | (buf[7]<<8) | buf[8];
	    delay -= delta;
//	    printf("%d %d\n", delta, now.tv_usec);
//	    printf("delay=%d\n", delay);
	}
    }
}

int main(int argc, char **argv)
{
    u_int32_t remote_ip = 0;
    struct sockaddr_in src;
    struct sockaddr_in dst;
    int fd;
    int rv;
    int i;
    int is_sender = 0;
    int max_packets = 0;

    while((i = getopt(argc, argv, "-p:sS:n:l:h"))!=-1)
    {
	switch(i)
	{
	    case 'l':
		payload_len = atoi(optarg);
		if ((size_t)payload_len > sizeof(buf))
		{
		    fprintf(stderr,"%s: error: max payload length is %d bytes",
			    argv[0], sizeof(buf));
		    exit(1);
		}
		if (payload_len < 9)
		{
		    fprintf(stderr,"%s: error: min payload length is 9 bytes",
			    argv[0]);
		    exit(1);
		}
		break;
	    case 'n':
		max_packets = atoi(optarg);
		break;
	    case 'p':
		remote_ip = inet_addr(optarg);
		break;
	    case 's':
		is_sender++;
		break;
	    case 'S':
		pkt_interval = atoi(optarg);
		break;
	    case 'V':
		use_voip++;
		break;
	    default:
		usage(argv[0]);
	}
    }

    src.sin_family = dst.sin_family = AF_INET;
    src.sin_addr.s_addr = INADDR_ANY;

    if (is_sender)
    {
	if (remote_ip == 0)
	    usage(argv[0]);
	dst.sin_addr.s_addr = remote_ip;

	if (use_voip)
	{
	    src.sin_port = htons(8000);
	    dst.sin_port = htons(8000);
	}
	else
	{
	    src.sin_port = 0; //htons(45001);
	    dst.sin_port = htons(45002);
	}
    }
    else
    {
	if (use_voip)
	    src.sin_port = htons(8000);
	else
	    src.sin_port = htons(45002);
    }

    fd = socket(PF_INET, SOCK_DGRAM, 0);
    if (fd == -1)
    {
	perror("socket");
	exit(-1);
    }

    rv = bind(fd, (struct sockaddr *) &src, sizeof(src));
    if (rv == -1)
    {
	perror("bind");
	exit(1);
    }

    if (is_sender)
    {
	rv = connect(fd, (struct sockaddr *) &dst, sizeof(dst));
	if (rv == -1)
	{
	    perror("connect");
	    exit(1);
	}

	sender(fd, max_packets);
    }
    else
	receiver(fd);

    close(fd);

    exit(0);
}

/* vim:sw=4 cindent
 */
