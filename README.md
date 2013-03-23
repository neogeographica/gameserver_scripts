What?
========
These are the scripts I use to run game servers for our local LAN on a Debian Linux host.  This setup should also have application to other Linux environments with some tweaking of init scripts.

This is just a raw file dump for now.  There's much more that could be done with this: proper packaging, customizing some bits on install, packages for the actual server files... well, maybe someday.

On my server, all game server executables and content are kept under the home directory of a particular user ("gameservers").  They can be started through init scripts, but even in that case they are run as that user.

Init Scripts
============

Init scripts are useful if you want to autostart one or more servers when the host boots up, and stop servers nicely on host shutdown.  (I won't go into details about configuring init scripts here; that's generic Debian/Linux behavior that is documented in plenty of other spots.)

Even if you don't want that behavior, init scripts can also be invoked manually to stop/start/restart servers and check whether a server is running, and they will refuse to start a particular server if it is already running.  They might also provide a nice hook to use with Webmin although I haven't investigated that yet.

In this setup, a distinct "server" is not just an executable but also some combination of options and assets.  Each init script specifies some variables that define a specific server.

So for example you could have one init script for a Quake 3 CTF server, another script for a small-playercount Quake 3 DM server, and another script for a large-playercount Quake 3 DM server.  Even though they all use a Quake 3 executable, you could run them all at the same time (if your host is beefy enough).  But if you tried to start "small-playercount Quake 3 DM server" while an instance of "small-playercount Quake 3 DM server" was already running, that start command would be rejected.

common code
-----------

The core of the init scripts is in "/lib/init/gameserver.sh".  This is generic code that implements start/stop/restart/status commands for any game server.  An init script that uses "gameserver.sh" should first define these variables to describe a specific game server:

* COMMAND : complete path to the command used to launch the server
* WORKINGDIR : complete path to the working directory to use when executing the command
* PIDFILE : complete path where a PID file will be created
* USER : user to run the server as
* DESCRIPTION : description of the server (printed in various messages)

example init scripts
--------------------

The various files under "/etc/init.d" in this repository are init scripts that I use for our QuakeWorld and Quake 3 servers.  The way I have things set up, the COMMAND and PIDFILE for an init script will have the same basename as the init script itself, but you could use some other naming convention if you like.

**\* Warning:** there is one brittle coupling between the init scripts and the server scripts that I need to get rid of.  My init scripts expect that the PID file will be created as ${NAME}.pid where NAME is the name of the init script.  The server scripts create the PID file at ${SERVERTYPE}\_${GAMETYPE}.pid ... so this system only works if the init script is named as ${SERVERTYPE}\_${GAMETYPE}.  I need to remove that dependence one way or another.

The init scripts are not going to differ much.  (In my case literally the only thing that differs is the script filename and the description of the service.)  The different server behaviors come from the different commands that each script runs.

The need to have a separate init script for each server configuration, rather than having an UberScript that takes an argument about which server to control, is basically a constraint of the way init scripts are handled at startup/shutdown time.  You need separate scripts for separate services.

These init scripts should have standard permissions (755) so that they can be executed by USER as well as by root.

Server Commands and Scripts
===========================

overview
------------------------------

The files under "/home/gameservers" in this repository are the scripts that actually run the servers.  Some of these are the commands that are launched by the init scripts, and the rest are utility/subroutine scripts used by the command scripts.

There's a pretty clean separation between this stuff and the init scripts.  The init scripts don't know anything about the internals of the commands or the other scripts used to run the servers.  Conversely, the commands don't need to be invoked through the init scripts; you could run the commands manually, if you don't care about any of the niceties described in the Init Scripts section.

The files directly in "/home/gameservers" are some example commands and the utility "myip" script.

The "scriptlib" directory contains the actual brains of the commands.

The "servers" directory contains the actual executables and data files for the game servers.  There's nothing from that directory in this repository (yet?) but I'll discuss its structure below because the scripts work with that structure.

"myip" script
-------------

"myip" is a script that returns the IP address that will be used to connect to a server, since server launch invocations tend to need that information.  This is a dumb/simple script that only works if the host has a single net interface.  It is used by "scriptlib/server\_loop".

Also I tend to use it manually every now and then, since I actually run these servers in a portable VM that gets a dynamic IP address.  "myip" should probably be moved into the "scriptlib" directory, but I got used to just logging into the VM console and quickly typing "myip".

"myip" should have execute permissions if you want to run it manually.

example commands
----------------

Other than "myip", all the files that live directly in "/home/gameservers" are commands that are invoked by the init script of the same name.  Each of these commands just sets up some variables and hands off to "scriptlib/server\_loop".

Command scripts should have execute permissions if you want to run them manually.

"scriptlib" directory
---------------------

"server\_loop" is the main script that runs a server executable and restarts it if it crashes.  A command script should set up these variables before using "server\_loop":

* BASEDIR : directory where the "servers" and "scriptlib" directories and "myip" are, and where the PID files will be created (in my case, this is always "/home/gameservers")
* SERVERTYPE : designator for the server executable (in my case, either "q1" or "q3"); used in naming conventions for PID files, server launch scripts, and the directory containing the server executable
* GAMETYPE : designator for the game/mod code to be used by this server (in my case, "ktx\_ctf", "cpma\_arena", etc.); used in naming conventions for PID files and server launch scripts
* SERVERPORT : port that clients should contact the server on
* SERVERDIR : optional; the name of a subdirectory where the server executable is... more on this below

When "server\_loop" executes, it first chooses a new working directory.  If SERVERDIR is defined, then the working directory will be ${BASEDIR}/servers/${SERVERTYPE}_server/${SERVERDIR}

If SERVERDIR is not defined then the working directory will just be ${BASEDIR}/servers/${SERVERTYPE}_server

The section below on the "servers" directory structure has some discussion on why you might or might not want to have a unique SERVERDIR for each server.

To actually launch the server, "server\_loop" runs some other script from "scriptlib", chosen according to this naming convention: ${SERVERTYPE}\_${GAMETYPE}\_server

The other files in "scriptlib" in this repository are examples of these server launch scripts, for our QuakeWorld and Quake 3 servers.

The "q1\_ktx\_common\_server" and "q3_cpma\_common\_server" scripts are common logic for launching most of our QuakeWorld or Quake 3 servers.  Usually the environment variables and the different working directories provide all the distinction we need for the different server behaviors.  So you'll see that most of the server launch scripts just run this common code.

But "q1\_excoop\_server" needs to use slightly different command-line options than the other QuakeWorld servers, so it gets its own unique launch script rather than using "q1\_ktx\_common\_server".

The command-line options in these example scripts are just the ones that I happen to use for our local LAN; they may not be right for anyone else.  (Although if you notice something I'm doing that is just plain wrong, please let me know.)

Also note that the Quake 3 servers set the "sv\_dlURL" variable, because my host has a webserver that provides pk3 files for high-speed downloads supported by the ioquake3 client.  Each server has its own directory of downloadable files that is related to the SERVERDIR variable.  You would *not* want to set "sv\_dlURL" in your command line if you don't have such a webserver configured.  (The webserver setup is kind of interesting so I may add some info about that at a later date.)

"servers" directory
-------------------

The actual game server executables and data live in the ${BASEDIR}/servers directory, which in my case is "/home/gameservers/servers".  The executables are placed in a particular directory structure according to what the server launch scripts expect.

The subdirectories under "servers" are named with this convention: ${SERVERTYPE}\_server

The server executable (such as "mvdsv" or "ioq3ded.i386") may live in such a subdirectory.  However, if the command script defined the SERVERDIR variable, then the executable is expected to be placed in a further subdirectory with the name defined by SERVERDIR.  (If that is unclear, look inside the "server\_loop" script to see how it deals with these variables.)

The reason I have this difference in behavior is that when I ran some Skulltag servers, I found it convenient to just dump all the Skulltag/Doom related stuff into one directory, regardless of whether those files were used to launch a co-op server or a deathmatch server.  The distinction between the servers was just a matter of specifying some options, rather than using different game code and data.  (I know there's no Skulltag server stuff in here at the moment; I've ripped it out for some later reworking and moving to Zandronum.)

For my QuakeWorld and Quake 3 servers though, it was nicer to use a different folder structure.  Here's an example of how the QuakeWorld stuff is laid out:

* servers
    * q1\_server
        * common
            * id1 directory and contents
            * ktx mod directory and contents
            * mvdsv
            * mvdsv.cfg
        * excoop\_server
            * coop mod directory and contents
            * symbolic links to id1, mvdsv, mvdsv.cfg
        * ktx\_ctf\_server
            * ktx
                * maps directory with CTF maps
                * mylan.cfg
                * symbolic links to other stuff in common/ktx
            * symbolic links to id1, mvdsv, mvdsv.cfg
        * ktx\_dm\_server
            * ktx
                * maps directory with DM maps
                * mylan.cfg
                * symbolic links to other stuff in common/ktx
            * symbolic links to id1, mvdsv, mvdsv.cfg

Basically I wanted to have *some* sharing of assets between servers, because when I change or update common stuff I don't want to have to remember to change it in multiple places.  But some other things shouldn't be shared.  Obviously the specific server config files must differ; also it was better to have separate map collections so that (for example) map voting options wouldn't be flooded with irrelevant stuff.  And any serverside-recorded demos from different servers will be nicely segregated with this layout.  Ditto for logging.

Note that having a different working directory for each server also means that you don't need as much (if any) variety in your launch scripts for the different servers.  For example you can always tell the server to use "mylan.cfg" and it will pick up the one relative to its own working directory, rather than having to have a different config file name for each server.

Anyway all of that is just my own personal setup.  The scripts largely don't care how you lay out your server assets; server launch really just boils down to two things:

* "server\_loop" will pick a working directory based on the SERVERTYPE and (if specified) SERVERDIR variables
* "server\_loop" runs some other script selected from the "scriptlib" directory based on a naming convention (${SERVERTYPE}\_${GAMETYPE}\_server), and that script does... whatever you want.
