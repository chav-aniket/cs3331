# CS3331 Lab06

z5265106 | Aniket Chavan

## Exercise 1: Setting up NS2 simulation for measuring TCP throughput

### Question 1

*Why the throughput achieved by flow tcp2 is higher than tcp1 between time span 6 sec to 8 sec?*

n3 --> n2 --> n4 --> n5 has one transmissions with 2.5Mbps bottleneck between n2 --> n4 while n0 --> n1 --> n2 --> n4 --> n5 has two transmissions with the 2.5Mbps bottleneck between n1 --> n2 --> n4. This means n3 can get more packets to n2 than n0 can. With the adjustment allowing the route of n3 --> n2 --> n4 --> n5 at around 6 seconds, this shows by TCP2 overtaking TCP1.

### Question 2

*Why the throughput for flow tcp1 is fluctuating between time span 0.5 sec to 2 sec?*

It uses the slow start method for determining window size as its means of congestion control, using the period of 0.5 - 2 seconds to adjust its window size.

### Question 3

*Why is the maximum throughput achieved by any one flow capped at around 1.5Mbps?*

n2 drops packets from both n0 and n3 due overload which will lead to the window size decreasing and entering a slow start phase for incremental window size increase. The TCP2 flow causes this packet loss and shifting in window size for both TCP1 and TCP2, stopping either flow from reaching their maximum throughput and capping it at 1.5Mbps.

## Exercise 2: Understanding IP Fragmentation

### Question 1

*Which data size has caused fragmentation and why?*

- Sizes 2000 and 3000 have caused fragmentation since 1500 is the maximum default and any larger quantity will automatically be fragmented.

*Which host/router has fragmented the original datagram?*

- 192.168.1.103

*How many fragments have been created when data size is specified as 2000?*

- 2 fragments were created

### Question 2

*Did the reply from the destination 8.8.8.8. for 3500-byte data size also get fragmented? Why and why not?*

Yes, the reply will be echoing the same quantity of bytes as was sent in the ping request and as it is above 1500, it will therefore need to be fragmented. 

### Question 3

*Give the ID, length, flag and offset values for all the fragments of the first packet sent by 192.168.1.103 with data size of 3500 bytes?*

| ID   | Length | Flag                    | Offset       |
| ---- | ------ | ----------------------- | ------------ |
| 7a7b | 1514   | 0x2000 (More Fragments) | 0            |
| 7a7b | 1514   | 0x20b9 (More Fragments) | 1480 --> 185 |
| 7a7b | 582    | 0x0172                  | 2960 --> 370 |

### Question 4

*Has fragmentation of fragments occurred when data of size 3500 bytes has been used? Why and why not?*

Yes, the maximum transfer unit is exceeded and so there is fragmentation. 

### Question 5

*What will happen if for our example one fragment of the original datagram from 192.168.1.103 is lost?*

If any fragment of a datagram is lost, the entire datagram received is discarded and the entire tcp package must be resent from the source. 

## Exercise 3: Understanding the Impact of Network Dynamics on Routing

### Question 1

*Which nodes communicate with which other nodes? Which route do the packets follow? Does it change over time?*

The routes are as follows:

udp0 --> n0 --> n1 --> n4 --> n5

udp1 --> n2 --> n3 --> n5

This does not change over time. 

### Question 2

*What happens at time 1.0 and at time 1.2? Does the route between the communicating nodes change as a result of that?*

The route to n4 from n0 is set to down, causing udp0 to experience package loss. The route does not change.

### Question 3

*Did you observe any additional traffic as compared to Step 3 above? How does the network react to the changes that take place at time 1.0 and time 1.2 now?*

Yes, as n4 was inaccessible, udp0 rerouted packets from n0 --> n2.

### Question 4

*How does this change affect the routing? Explain why.*

As there is the increase in cost from 1 to 3 for travelling from n1 --> n4, the initial route of n1 --> n4 --> n5 now has a cost of 4 where before it was 2. Udp0 uses the distance vector algorithm to instead travel by the second route n1 --> n2 --> n3 --> n5 which has a cost of 3, even if the first route has less links to travel. Udp1 is unaffected.

### Question 5

*Describe what happens and deduce the effect of the line you just uncommented.*

#### UDP1:

**Route 1 - ** n0 --> n1 --> n4 --> n5, **Cost:**  4

**Route 1 - ** n0 --> n1 --> n2 --> n3 --> n5, **Cost:**  5

#### UDP2:

**Route 1 - ** n2 --> n3 --> n5, **Cost:**  4

**Route 1 - ** n2 --> n1 --> n4 --> n5, **Cost:**  4

As UDP1 has equal costs in both routes, it uses both. Line 29 must allow for the use of 2 routes. 