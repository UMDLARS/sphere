/*
 * Copyright (C) 2007 SPARTA, Inc.
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 */

#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include "fftw3.h"

struct ele
{
	float val;
	int pos;
};


void fatal(char *str)
{
	fputs(str, stderr);
	exit(-1);
}

#define MAX_COUNTS 20

int main(int argc,char *argv[])
{
	unsigned int firstSample, lastSample, NoSamples;
	int ii, jj, cc, lag, N;
	double *abval,*cumpsd, freq, sum;
	float average=0;
	char strbuf[40], *inputFile;
	char outputPSD[256], outputCPSD[256];
	FILE *fp;

	struct ele *x;
	struct ele *ax;
	fftw_complex *in,*out;
	fftw_plan p;

	unsigned long start = time(NULL);

	if (argc < 2)
	{
		fprintf(stderr, "Usage: %s <file> [<first sample> [<last sample>]]]\n", argv[0]);
		return 0;
	}

	inputFile = argv[1];
	sprintf(outputPSD, "%s.psd", argv[1]);
	sprintf(outputCPSD, "%s.cpsd", argv[1]);
	if (argc >= 3)
		firstSample = atoi(argv[2]);
	else
		firstSample = 0;

	if (argc == 4)
		lastSample = atoi(argv[3]);
	else
	{
		lastSample = 0;
		fp = fopen(inputFile, "r"); 
		if (!fp) fatal("Can't read input file.\n");
		while ((fgets(strbuf, sizeof(strbuf), fp)) != NULL)
			lastSample++;
		fclose(fp);
		lastSample--;
	}

// To calculate number of lines to be read */
	N = lastSample - firstSample + 1;
	x = (struct ele *)malloc(N*sizeof(struct ele));  //Storage allocation for input samples 
	ax = (struct ele *)malloc(2*(N-1)*sizeof(struct ele));  // Autocorrelation Samples storage

// read in the data
	printf("Reading %s from sample %d to %d\n", inputFile, firstSample, lastSample);
	fp = fopen(inputFile, "r"); 
	if (!fp) fatal("Can't read input file.\n");
	for(ii = 0; ii < firstSample; ii++)
	{
		if ((fgets(strbuf, sizeof(strbuf), fp)) == NULL)
			fatal("Ran out of data before firstSample\n");
	}

	for(ii = 0; ii < N; ii++)
	{
		if ((fgets(strbuf, sizeof(strbuf), fp)) == NULL)
			fatal("Ran out of data before lastSample\n");
		sscanf(strbuf, "%f", &x[ii].val);

		x[ii].pos=ii;
		average += x[ii].val;
	}
	fclose(fp);
    
// finish average and print some info
	average /= (float)N; 
	printf("average = %f of %d samples\n", average, N);

// Autocorrelation
	printf("%d: Autocorrelation...\n", (time(NULL)-start));
	//fp = fopen("Autocorrelation", "w");
	register float tt;
	for(lag = -N+1, cc=0; lag <= N-1; lag++, cc++)
	{
		ax[cc].val = 0;
		ax[cc].pos = lag;
	
		for(ii = 0; ii < N; ii++)
		{
			if (ii+lag >= N)
				tt = 0;
			else if(ii + lag < 0)
				tt = 0;
			else
				tt = x[ii+lag].val;
	
			ax[cc].val += (x[ii].val-average)*(tt-average);
		}

	//	fprintf(fp,"%d %g\n", lag, ax[cc].val);    
	}
//	fclose(fp);


// PSD
	printf("%d: PSD...\n", (time(NULL)-start));
	NoSamples = 2*N-1;

	in = fftw_malloc(sizeof(fftw_complex)*NoSamples);
	out = fftw_malloc(sizeof(fftw_complex)*NoSamples);

	for(ii = 0; ii < NoSamples; ii++)
		for(jj = 0; jj < 1; jj++)
		{
			in[ii][jj] = ax[ii].val;
			in[ii][jj+1] = 0;
		}

	p=fftw_plan_dft_1d(NoSamples,in,out,-1,FFTW_ESTIMATE);
	fftw_execute(p);

	abval=(double *)malloc(N*sizeof(double));
	fp = fopen(outputPSD,"w");
	for(ii = 0; ii < N; ii++)
		for(jj=0;jj<1;++jj)
		{
			abval[ii] = sqrt((out[ii][jj]*out[ii][jj])+(out[ii][jj+1]*out[ii][jj+1]));
			freq = ii/(float)NoSamples*1000;
			fprintf(fp,"%g %g\n",freq,abval[ii]);
		}
	fclose(fp);
	

// CPSD
	printf("%d: CPSD...\n", (time(NULL)-start));
	cumpsd=(double *)malloc(N*sizeof(double));
	for(ii = 0; ii < N; ii++)
	{
		sum = 0;
		for(jj = 0; jj <= ii; jj++)
		{  
			sum += abval[jj];
		} 
		cumpsd[ii] = sum;
	}

	fp = fopen(outputCPSD,"w");
	for(ii = 0; ii < N; ii++)
	{ 
		cumpsd[ii] = cumpsd[ii]/cumpsd[N-1];
		freq = ii/(float)NoSamples*1000;
		fprintf(fp,"%g %g\n",freq,cumpsd[ii]);
	}
	fclose(fp);

// Free memory
	free(x);
	free(ax);
	free(abval);
	free(cumpsd);

	fftw_destroy_plan(p);
	fftw_free(in);
	fftw_free(out);
}

