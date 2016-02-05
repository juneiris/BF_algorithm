What's in the folder:
1.BF algorithm implementation program--bfclient.py
2.readme.txt:describes running instruction and general infomation of code



Develop environment:
Python 2.7.2.



How to run the code:
There's no makefile, type the following to command window to invoke:
	python PATH/bfclient.py localport timeout [ipaddress1 port1 cost1]……

The localip is initially got by socket.getbostbyname(socket.gethostname()). If clients can't receive its neighbors routing table, first check if the ip address is got correctly and if neighbor's ip are input correctly. If neighbor information is not input in triples, a 'Wrong information of neighbors.Ip address, port and cost of each neighbor are required.Please type CLOSE' message will print, and the user will need to restart the program.
If there are hidden neighbors(neighbors that are not input in command line during invoke), hidden neighbors are better run after those initialized neighbor. And wait a bit longer before you do any LINKDOWN or CLOSE operation in case that not all clients have heard from the new neighbor( if so, bug will be trigger that clients won't be able to find the original cost to the new neighbor after the shortest path has been LINKDOWN).For example, client A and client B set each other as neighbor in command line, and there is another client C, user told C that A and B are its neighbors in command line but didn't tell A and B that C is their neighbor. In this case, A and B should be run before C for shorter convergence time.(Hidden neighbor could be run first ,and in most cases there will be no error, but it will take longer for other nodes to find the hidden neighbor)

ps. there may be some "print" that I forget to comment, so there may be some data print on screen even if you didn't type in SHOWRT. Please ignore those information.




Constants and variables:
INF=100000 is defined as INFINITY, means the node is unreachable.

ndict is defined as routing table. It has three properties: 'address' means destination ip and port, 'cost' means the cost of the link, 'link' means next hop.

ncheat is defined for poison reverse. If A finds it has a link through B, it will send B ncheat with the infinity cost to destination from A.

neifirst is defined to store the initial cost to neighbors.

originalcost is defined to store the cost and link when a link is destoryed by LINKDOWN.

mynei is defined to store neighbors' addresses and the timestamp when the client last heard from them.





Data messages:
1.ROUTE UPDATE message is the client's routing table. Every time a modification is made to routing table or a timeout time passes, client convert ndict to a str in the following format and send it along with its own address to neighbors:
	Destination=ip:port, Cost=.., Link=(ip:port)
The entire message is like: localip:localport;Destination=ip:port, Cost=.., Link=(ip:port)\n……
When neighbors receive the message, they split the string and process it line by line.

2. When LINKDOWN is used, a string 'LINKDOWN' is sent to the linkdown target as a notification to tell the target to delete sender from its neighbor and set all links pass through sender cost to INF.
3. When LINKDOWN is used, a string 'LINKDOWN' is sent to the linkdown target as a notification to tell the target to restore the link to sender and add sender to its neighbor list.





Commands:
SHOWRT: convert the routing table ndict to a string and print it on terminal. 
LINKDOWN:destroy a link between sender and target. If the target is not a neighbor of sender, or if the target is the sender itself, the link cannot be destroyed, a notification message will print, you need to change a target.The sender deletes the target from its neighbor and set all links pass through the target cost to INF.
LINKUP:restore a link to its original value after it was destroyed by LINKDOWN. If the target is not a neighbor of sender, or the link didn't exist, a notification will print.The sender finds back the link and cost to target and add the target back to its neighbor list.
CLOSE: shut down the client, same as CTRL+C




Features:
1.hidden neighbors and hidden nodes can be found, and starting sequence usually only effect convergence time.
2.Poison reverse is used to help routing table converge faster and partly help to solve count to infinity problem, but it cannot solve count to infinity problem entirely.






Bug:
Happens occasionally: I think the bug is triggered by asynchronization since a use seperate threads to receive and process routing table from neighbors and use another thread to send my own routing table every timeout time. It happens ocassionally in circle topologies when a link is destroyed by LINKDOWN. For example, A,B,C are each other's neighbor, B LINKDOWN C, but before B finish its processing(already set the cost to C to INF, but hasn't set the linkcost through C to INF and delete C from its neighbor list yet), it receive A's routing table that hasn't been updated(old version), then B will set its cost to C as what A told it(newcost = costtoA+ AcosttoC, new next hop=A).Because B uses A's old version table, wrong result will happen in B's cost to C and all links through C.
I set various of judgement statement, but i'm not sure if this sometimes-happen issue is completely solved because i don't know when it will happen.




