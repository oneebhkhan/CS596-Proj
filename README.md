# Parallel Rendering for multiple plant lightings in simulation 🌱🌱🌱

We are interested in optimizing the study of computational agroceology by simulating ecosystem and individual plant using Mitsuba, a physics engine that renders the environment and simulate incident light. 

## Overview
1. [Introduction](#introduction)
3. [Problem Statement](#problem-statement)
4. [Resources and Platform](#resources-and-platform)
5. [Methods](#methods)
6. [Prelimary Results](#prelimary-results)
7. [Work Distribution](#work-distribution)
8. [Acknowledgement](#acknowledgment)

## Introduction
We model the growth of plant objects in simulation as a decision-making process and construct the rewards and penalties based of the incident light on plant objects. We trained the plant growing agent using a reinforcement learning (RL) algorithm. 

Rendering and calculation of incident light on one plant object takes approximately 1 second on a 6 cores i7 CPU. As the RL agent sows more plants in the environment, each individual rendering could end up taking 2 or 3 orders of magnitude longer. 

In the current set up, each training episode, that represents 1 year, comprises of 365 steps, with each step representing 1 day. Currently, the render time for 1 episode is > 15 hours. It is very computationally expensive to simulate 1-year incident lights for plants in the envivronment to effectively understand the growth of plants. 

Therefore, we aim to optimize the rendering of light incidents for multiple plant objects in mitsuba environment using parallel computing techniques running on CPUs and GPUs.

## Problem Statement

## Resources and Patform

## Methods

## Prelimary Results

## Work Distribution

We are a team of three and all works are split equally as follow:

Oneeb: 

Iris: Generate results and visualizations in plots. Working on parallelism using MPI4py and multi-threading and processes in python. 

Armaghan: 

## Acknowledgment

Our team is very grateful to Tomek Osinski from CARC who was of great help in setting up the mitsuba library for us on Discovery, a process which turned out to be rather convoluted and complicated.

CS596 Semester Project Fall 2021

## Tasks Outlined
1. Save timing data to .out file
2. Run on CPU on Discovery Cluster
3. Look into profiler for python
4. Multithreading for python
5. Identify where the code is being run in a parallel way \n
	Local m/c 16 threads for mitsuba, EPYC 64 threads for mitsuba
6. Identify how to visualize information


