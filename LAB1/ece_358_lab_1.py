"""
ECE Lab 1 - M/M/1 and M/M/1/K Queue Simulation
Authors: Adel Pazoki and Larissa Troper
"""

# Question 1:
# Write a short piece of code to generate 1000 exponential random variable with lambda=75. What is the mean and
# variance of the 1000 random variables you generated? Do they agree with the expected value and the variance of an
# exponential random variable with lambda=75? (if not, check your code, since this would really impact the remainder of your
# experiment).

import math
import random
import statistics

def generate_random_exp_variable(lambda_value):
  """
  Takes in a lambda value and returns a exponential random variable.
  """
  import math, random
  r = random.random() # random number between 0 and 1
  return -(1/lambda_value)*math.log(1-r)

lambda_val = 75
expected_value = 1/lambda_val
variance = 1/(lambda_val ** 2)

print("Question 1: ")
print("Expected mean of an exponential random variable with lambda = 75: ", expected_value)
print("Expected variance of an exponential random variable with lambda = 75: ", variance)

exp_rand_vars = []

for i in range(1000):
  var = generate_random_exp_variable(lambda_val)
  exp_rand_vars.append(var)

computed_mean = statistics.mean(exp_rand_vars)
computed_variance = statistics.variance(exp_rand_vars)
print("Computed mean of 1000 generated exponential random variables with lambda = 75: ", computed_mean)
print("Computed variance of 1000 generated exponential random variables with lambda = 75: ",  computed_variance, "\n")



#########################################################################
########### Helper Functions for MM1 and MM1K Simulations ###############
#########################################################################

def generate_non_departure_events(simulation_time, lambda_value, event_type):
  """
  Method used to pre-generate arrival and observer events.

  Takes in the total time of the simulation and the lambda for generating
  the events.

  Returns an array of the events with their event type and arrival times.
  """
  curr_time = 0 # Keeps track of time passed in simulation
  events = []

  while(curr_time < simulation_time):
    interarrival_time = generate_random_exp_variable(lambda_value)
    curr_time += interarrival_time

    if curr_time > simulation_time:
      break

    events.append([curr_time, event_type])

  return events


def generate_service_time(packet_lambda, transmission_rate):
  """
  Takes in a lambda value to generate a random exponential variable for
  packet length and the transmission rate of the server.

  Returns a service time.
  """
  packet_length = int(generate_random_exp_variable(packet_lambda))
  service_time = packet_length/transmission_rate

  return service_time

#########################################################################
#########################################################################
#########################################################################
#########################################################################
#########################################################################

def mm1_simulation(T, L, C, r):

  packet_lambda = 1 / L  # Lambda value for generating packet length
  arrival_lambda = (r * C) / L # Lambda value for generating arrival events
  alpha = arrival_lambda * 5  # Lambda value for generating observer events

  def generate_departure_events(arrivals, packet_lambda, transmission_rate):
    """
    Takes an array of arrival events, the lambda used to generate packet length, and
    the server's transmission rate. The lambda and transmission rate are used to
    generate a service time to calculate departure times.

    Returns an array of corresponding departures for each arrival event.
    """
    departures = []

    for i in range(len(arrivals)):
      arrival_time = arrivals[i][0]

      service_time = generate_service_time(packet_lambda, transmission_rate)

      # If first arrival then departure is arrival + service time
      if i == 0:
         departures.append([arrival_time + service_time, "Departure"])
      else:
        if arrival_time < departures[i - 1][0]:
          # If the packet arrives before the last event departs:
          #   departure time = last events departure time + service time
          departures.append([departures[i-1][0] + service_time, "Departure"])
        else:
          departures.append([arrival_time + service_time, "Departure"])

    return departures

  def run_simulation(events):
    """
    Takes an array of events (arrivals, departures, observers) for the mm1 simulation.

    Returns the average number of packets in the queue (e_n) and the proportion
    of time the server is idle (p_idle). Since the queue is infinite, the probability
    of losing packets is 0%.
    """
    events.sort(key=lambda x:x[0]) # Sorts events by time in ascending order

    num_arrivals = 0
    num_departures = 0
    num_observations = 0
    idle_counter = 0 # Empty buffer count
    total_packets = 0 # observer increments total packets by # of packets in buffer

    for event in events:
      event_type = event[1]
      if event_type == "Arrival":
        num_arrivals += 1
      elif event_type == "Departure":
        num_departures += 1
      elif event_type == "Observer":
        num_observations += 1

        packets_in_queue = num_arrivals - num_departures

        if packets_in_queue == 0:
          idle_counter += 1

        total_packets += packets_in_queue

    e_n = total_packets/num_observations
    p_idle = (idle_counter/num_observations*100)

    return e_n, p_idle

  events = generate_non_departure_events(T, arrival_lambda, "Arrival")
  events.extend(generate_departure_events(events, packet_lambda, C))
  events.extend(generate_non_departure_events(T, alpha, "Observer"))

  e_n, p_idle = run_simulation(events)

  print("For MM1 simulation with utilization = ", round(r,2),":")
  print("E_n: ", e_n)
  print("P_idle: ", p_idle)

  return e_n, p_idle


def mm1k_simulation(T, L, C, r, K):
  """
  Takes in values for simulation time (T), average packet length (L), transmission
  rate (C), queue limit (K), and utilization (r). These parameters are used within
  the generation of events and the mm1k simulation.

  Returns the average number of packets in the queue (e_n), the proportion
  of time the server is idle (p_idle) and the packet loss probability (p_loss).
  """

  packet_lambda = 1 / L  # Lambda value for generating packet length
  arrival_lambda = (r * C) / L # Lambda value for generating arrival events
  alpha = arrival_lambda * 5  # Lambda value for generating observer events

  def run_simulation(events, K):
    """
    Takes an array of events (arrivals and observers) and a queue limit to run
    the mm1k simulation.

    Returns the average number of packets in the queue (e_n), the proportion
    of time the server is idle (p_idle) and the packet loss probability (p_loss).
    """
    
    events.sort(key=lambda x:x[0]) # Sorts events by time in ascending order

    num_arrivals = 0
    num_observations = 0

    queue = [] # Holds event departure times
    idle_counter = 0 # Empty buffer count
    lost_packets = 0 # Counts occurences when a packet is lost (full queue)
    total_packets = 0 # observer increments total packets by # of packets in buffer

    for event in events:
      curr_time = event[0]

      # If event departure time is less than current time, event can be removed from queue
      while (len(queue) > 0 and queue[0] <= curr_time):
        queue.pop(0)

      event_type = event[1]
      if event_type == "Arrival":
        num_arrivals += 1

        if len(queue) == K + 1:
          lost_packets += 1
        else:
          # If queue is not full, generate departure time
          service_time = generate_service_time(packet_lambda, C)

          if len(queue) > 0:
            departure_time = max(curr_time, queue[-1])
          else:
            departure_time = curr_time

          departure = departure_time + service_time
          queue.append(departure)

      elif event_type == "Observer":
        num_observations += 1

        packets_in_queue = len(queue)

        if packets_in_queue == 0:
          idle_counter += 1

        total_packets += packets_in_queue

    e_n = total_packets/num_observations
    p_idle = (idle_counter/num_observations*100)
    p_loss = lost_packets/num_arrivals

    return e_n, p_idle, p_loss

  # Pre-generate arrival and observer events
  events = generate_non_departure_events(T, arrival_lambda, "Arrival")
  events.extend(generate_non_departure_events(T, alpha, "Observer"))

  e_n, p_idle, p_loss = run_simulation(events, K)  # Run simulation

  print("For MM1K simulation with K = ", K, " and utilization = ", round(r,2),":")
  print("E_n: ", e_n)
  print("P_idle: ", p_idle)
  print("P_loss: ", p_loss, "\n")

  return e_n, p_idle, p_loss


import matplotlib.pyplot as plt
import numpy as np
import os

def plot_mm1_simulations(L, T, C, rho_values):
  """
  Returns plot of mm1 simulations with different utilization values (rho_values)
  """
  en_values = []
  p_idle_values = []

  for r in rho_values:
    e_n, p_idle = mm1_simulation(T, L, C, r)
    en_values.append(e_n)
    p_idle_values.append(p_idle)

  # Plot utilization as x values and en_values as y values
  fig1 = plt.figure()

  ax = fig1.add_subplot(1, 1, 1)
  ax.plot(rho_values, en_values)

  ax.set_title(f'E[N] vs. Utilization (T= {T} s, L= {L/10**3} kb/pkt, C= {C/10**6} Mbps)')
  ax.set_xlabel('Traffic intensity')
  ax.set_ylabel('E[N], average number of packets in queue')

  # Plot utilization as x values and p_idle as y values
  fig2 = plt.figure()

  ax2 = fig2.add_subplot(1, 1, 1)
  ax2.plot(rho_values, p_idle_values)

  ax2.set_title(f'P_idle vs. Utilization (T= {T} s, L= {L/10**3} kb/pkt, C= {C/10**6} Mbps)')
  ax2.set_xlabel('Traffic intensity')
  ax2.set_ylabel('Propotion of Idle')

  folder_name = "Plots_Question3"  
  if not os.path.exists(folder_name):
    os.makedirs(folder_name)

  file_name = "Question 3_1.png"  
  file_path = os.path.join(folder_name, file_name)
  fig1.savefig(file_path)
  file_name = "Question 3_2.png"  
  file_path = os.path.join(folder_name, file_name)
  fig2.savefig(file_path)
  plt.close(fig1)
  plt.close(fig2)


def plot_mm1k_simulations(T, L, C, rho_values, K):
  """
  Returns plots of mm1k simulations with different queue limits (K) and different
  utilization values (rho_values)
  """

  def run_mm1k_by_utilization_val(T, L, C, rho_values, K):
    """
    Given a K value, the method runs mm1k simulation through a range
    of utilization values (rho_vals).

    Returns list of average number of packets in the queue (e_n), proportion
    of time the server is idle (p_idle) and packet loss probability (p_loss) per
    each utilization value with queue limit of K.
    """

    en_list, p_idle_list, p_loss_list = [], [], []

    for r in rho_values:
      e_n, p_idle, p_loss = mm1k_simulation(T, L, C, r, K)
      en_list.append(e_n)
      p_idle_list.append(p_idle)
      p_loss_list.append(p_loss)

    return en_list, p_idle_list, p_loss_list

  def run_mm1k_by_queue_limit(T, L, C, rho_values, queue_limit_values):
    en_list, p_idle_list, p_loss_list = [], [], []

    for K in queue_limit_values:
      # Catch results from simulations
      en_list_k, p_list_idle_k, p_list_loss_k = run_mm1k_by_utilization_val(T, L, C, rho_values, K)
      en_list.append(en_list_k)
      p_idle_list.append(p_list_idle_k)
      p_loss_list.append(p_list_loss_k)

    return en_list, p_idle_list, p_loss_list

  en_list, p_idle_list, p_loss_list = run_mm1k_by_queue_limit(T, L, C, rho_values, K)

  en_fig, en_ax = plt.subplots(1, 1, figsize=(8, 6))
  pidle_fig, idle_ax = plt.subplots(1, 1, figsize=(8, 6))
  ploss_fig, loss_ax = plt.subplots(1, 1, figsize=(8, 6))

  for i in range(len(K)):
    en_ax.plot(rho_values, en_list[i], label=f"K={K[i]}")
    idle_ax.plot(rho_values, p_idle_list[i], label=f"K={K[i]}")
    loss_ax.plot(rho_values, p_loss_list[i], label=f"K={K[i]}")

  en_ax.set_ylabel('E[n], Avg Queue Size ')
  en_ax.set_xlabel('% Utilization')

  idle_ax.set_ylabel('% Idle')
  idle_ax.set_xlabel('% Utilization')

  loss_ax.set_ylabel('%  Loss')
  loss_ax.set_xlabel('% Utilization')

  en_ax.set_title(f'E[n] v Rho, K = {K[i]}, T= {T} s, L= {L/10**3} kb/pkt, C= {C/10**6} Mbps')
  idle_ax.set_title(f'P_Idle v Rho, K = {K[i]}, T= {T} s, L= {L/10**3} kb/pkt, C= {C/10**6} Mbps')
  loss_ax.set_title(f'P_Loss v Rho, K = {K[i]}, T= {T} s, L= {L/10**3} kb/pkt, C= {C/10**6} Mbps')

  en_ax.legend()
  idle_ax.legend()
  loss_ax.legend()
  
  folder_name = "Plots_Question6"  
  if not os.path.exists(folder_name):
    os.makedirs(folder_name)

  file_name = "Question 6_1.png"  
  file_path = os.path.join(folder_name, file_name)
  en_fig.savefig(file_path)
  file_name = "idle.png"  
  file_path = os.path.join(folder_name, file_name)
  pidle_fig.savefig(file_path)
  file_name = "Question 6_2.png"  
  file_path = os.path.join(folder_name, file_name)
  ploss_fig.savefig(file_path)
  plt.close(en_fig)
  plt.close(pidle_fig)
  plt.close(ploss_fig)


#########################################################################
################# Testing Simulation times for MM1 ######################
#########################################################################
print("Finding stable simulation time for MM1: \n")
T1 = 1000
L = 2000
C = 1000000
rho = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
en_values = 0
p_idle_values = 0

for r in rho:
  en_value, p_idle_value = mm1_simulation(T1, L, C, r)
  en_values += en_value
  p_idle_values += p_idle_value

T2 = 2000
en_values2 = 0
p_idle_values2 = 0

for r in rho:
  en_value, p_idle_value = mm1_simulation(T2, L, C, r)
  en_values2 += en_value
  p_idle_values2 += p_idle_value

print("\nSimulation Time ", T1)
print("Average E[N]: ", en_values/6)
print("Average P_idle: ", p_idle_values/6, "\n")

print("Simulation Time ", T2)
print("Average E[N]: ", en_values2/6)
print("Average P_idle: ", p_idle_values2/6, "\n")

#########################################################################
#########################################################################
#########################################################################


T = 2000
L = 2000
C = 1000000

# Question 3
print("Question 3: \n")
plot_mm1_simulations(T, L, C, np.arange(0.35, 0.95, 0.1))

# # Question 4
print("Question 4: \n")
mm1_simulation(T, L, C, 1.2)


#########################################################################
############ Testing Simulation times for MM1K ##########################
#########################################################################
# print("Finding stable simulation time for MM1K at K = 50: \n")
# T1 = 1000
# K = 50
# rho = np.arange(0.5, 1.6, 0.1)
# en_values = 0
# p_idle_values = 0
# p_loss_values = 0

# for r in rho:
#   en_value, p_idle_value, p_loss_value = mm1k_simulation(T1, L, C, r, K)
#   en_values += en_value
#   p_idle_values += p_idle_value
#   p_loss_values += p_loss_value

# T2 = 2000
# en_values2 = 0
# p_idle_values2 = 0
# p_loss_values2 = 0

# for r in rho:
#   en_value, p_idle_value, p_loss_value = mm1k_simulation(T2, L, C, r, K)
#   en_values2 += en_value
#   p_idle_values2 += p_idle_value
#   p_loss_values2 += p_loss_value


# print("\nSimulation Time ", T1)
# print("Average E[N]: ", en_values/6)
# print("Average P_idle: ", p_idle_values/6, "\n")
# print("Average P_loss: ", p_loss_values/6, "\n")

# print("Simulation Time ", T2)
# print("Average E[N]: ", en_values2/6)
# print("Average P_idle: ", p_idle_values2/6, "\n")
# print("Average P_loss: ", p_loss_values2/6, "\n")

#########################################################################
#########################################################################
#########################################################################

# Question 6
print("Question 6: \n")
plot_mm1k_simulations(T, L, C, np.arange(0.5, 1.6, 0.1), [10,25,50])
