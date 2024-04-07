# Network Queue Simulations and Resolvers

This repository contains simulation tools for analyzing network queues, along with DNS Resolution and HTTP Resolver implementations. The primary focus is on the M/M/1 and M/M/1/K queue models and creating a simple HTTP web server and DNS server-client architecture.

## Simulators

## M/M/1 Queue Simulator

The M/M/1 queue simulation aims to determine key performance metrics such as average number of packets in the queue (e_n) and the proportion of time the queue is idle (p_idle).

### Simulation Parameters:
- `T`: Total simulation time
- `L`: Average length of a packet in bits
- `C`: Transmission rate of the output link in bits per second
- `ρ`: Utilization of the queue

### Methodology:
The simulation uses these parameters to calculate arrival and service rates, using exponential random variables for packet interarrival and service times. Events are pre-generated for arrivals, and departures are determined during simulation runtime.

The system state is captured through observer events, with metrics being calculated based on the observer's perspective of the queue.

## M/M/1/K Queue Simulator

The M/M/1/K simulator extends the M/M/1 model to incorporate a finite buffer size `K`.

### Simulation Parameters:
- All parameters from M/M/1
- `K`: Queue size (buffer capacity)

### Design Differences:
Departure events are generated dynamically during the simulation, considering the queue's finite size. Lost packets are recorded when the queue capacity is reached.

### Metrics:
In addition to `e_n` and `p_idle`, `p_loss` is calculated to reflect the probability of packet loss due to a full queue.

## Resolvers

### HTTP Resolver

A minimalistic HTTP server written in Python that can handle GET and HEAD requests. It responds with the appropriate content or a 404 error if the requested file is not found.

#### Features:

- Listens on `127.0.0.1:10200` for incoming HTTP requests.
- Generates dynamic HTTP response headers including last modified time, content type, and content length.
- Supports file retrieval and directory listing with proper MIME type detection.
- Gracefully handles file not found errors by serving a default 404 page.

### DNS Resolution

Implements a basic DNS client-server architecture that allows domain name queries and returns IP addresses associated with them.

#### Client:

- Sends DNS queries to the server for specified domain names.
- Parses the response and prints out the record details like IP address and TTL.

#### Server:

- Listens on `127.0.0.1:10500` for DNS queries.
- Responds with A records for predefined domain names.
- Supports multiple IP addresses for a single domain.

## File Structure:

- `DNS Resolution & HTTP Resolver/`: Contains the implementations of the DNS client-server and HTTP server.
- `M/M/1 & M/M/K Networks Queue Simulator/`: Holds the core logic for queue simulations.

