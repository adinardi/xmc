XMC - Xen Management Console
====

This is the current incarnation of XMC used by the Computer Science House of RIT (http://www.csh.rit.edu).

It is a home-grown system built on top of the network/technologies/systems available at the time. The code can be a mess at times since this was my (Angelo) first large project using python. This is some pretty terrible Javascript too, since the original version had very little and my focus was getting the (much harder) backend functionality working first. Famous last words, I've never had time to go back and do it right.

At the moment the project is on hold due to a possible replacement being implemented to replace the older hardware setup.


Features
----
* Creation of virtual machines based on pre-built images
* Allocation of VMs to users and their ability to manage the VMs they are assigned (boot/reboot/shutdown).
* Live Migrations
* Overview of system and which physical machine VMs are located on and their memory usage.
* Basic load balancing so that when a VM is booted it will be placed on the machine with the most available memory.