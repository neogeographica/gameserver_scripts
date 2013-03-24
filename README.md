What?
=====
These are the scripts I use to run game servers for our local LAN on a Debian Linux host.  This setup should also have application to other Linux environments with some tweaking of init scripts.

This is just a raw file dump for now.  There's much more that could be done with this: proper packaging, customizing some bits on install, packages for the actual server files... well, maybe someday.

On my server, all game server executables and content are kept under the home directory of a particular user ("gameservers").  They can be started through init scripts, but even in that case they are always run as that user.

Init Scripts
============

overview
------------------------------

Init scripts are useful if you want to autostart one or more servers when the host boots up, and stop servers nicely on host shutdown.  (I won't go into details about configuring init scripts here; that's generic Debian/Linux behavior that is documented in plenty of other spots.)

Even if you don't want that behavior, init scripts can also be invoked manually to stop/start/restart servers and check whether a server is running, and they will refuse to start a particular server if it is already running.  Servers run through these init scripts will be run as background "daemon" processes, so they don't tie up a terminal window.  Init scripts might also provide a nice hook to use with Webmin although I haven't investigated that yet.

In this setup, a distinct "server" is not just an executable but also some combination of options and assets.  Each init script specifies some variables that define a specific server.

So for example you could have one init script for a Quake 3 CTF server, another script for a small-playercount Quake 3 DM server, and another script for a large-playercount Quake 3 DM server.  Even though they all use a Quake 3 executable, you could run them all at the same time (if your host is beefy enough).  But if you tried to start "small-playercount Quake 3 DM server" while an instance of "small-playercount Quake 3 DM server" was already running, that start command would be rejected.

game server init scripts
------------------------

Each init script represents a particular server configuration.  Installing or uninstalling a server involves (among other things) adding or removing an init script.  An init script describes a particular server (by specifying the "gameserver.sh" variables listed below) and then runs the "gameserver.sh" code.

The need to have a separate init script for each game server, rather than having an UberScript that takes an argument about which server to control, is basically a constraint of the way init scripts are handled at startup/shutdown time.  You need separate scripts for separate services.

If you want a particular game server to be ready to run, but *not* automatically start when the host starts, you should still have an init script for that game server.  Just configure your host's init script behavior so that the game server does not autostart.

Reconfiguring a server should *not* involve any modification of an init script; instead reconfiguration would involve changing the server scripts (described below), and/or modifying server assets like configuration files.

The various files under "/etc/init.d" in this repository are examples of init scripts.  They're the init scripts that I use for our QuakeWorld and Quake 3 servers.  The way I have things set up, the COMMAND for an init script will have the same basename as the init script itself, but you could use some other naming convention if you like.

These init scripts should have standard permissions (755) so that they can be executed by USER as well as by root.

common code: "gameserver.sh"
----------------------------

The core of the game server init script logic is in "/lib/init/gameserver.sh".  This is generic code that implements start/stop/restart/status commands for any game server.  You should *not* need to modify "gameserver.sh" in any way when installing, uninstalling, or reconfiguring a server.

An init script that uses "gameserver.sh" should first define these variables to describe a specific game server:

* COMMAND : complete path to a file that can be executed to launch the server
* PATH : executables search path that should be used when launching the server
* USER : user to run the server as
* DESCRIPTION : description of the server (printed in various init-script messages)

The "gameserver.sh" code makes a couple of assumptions based on these variables:

* The working directory (when launching the server) will be the directory where the COMMAND file is located.
* The PID file will be created as ${COMMAND}.pid

The PID file location is not configurable in the init script because I want to make sure that normal fiddling with server configuration won't make the init script and server script disagree about where the PID file is located.  Similarly on the server-script side of things, the PID file location is determined internally rather than being affected by normal configuration changes.

Server Scripts
==============

overview
------------------------------

The files under "/home/gameservers" in this repository are the scripts that actually run the servers.  Some of these are the commands that are launched by the init scripts, and the rest are utility/subroutine scripts used by the command scripts.

There's a pretty clean separation between this stuff and the init scripts.  The init scripts don't know anything about the internals of the commands or the other scripts used to run the servers.

Conversely, the commands don't need to be invoked through the init scripts; you could run the commands manually, if you don't care about any of the niceties described in the Init Scripts section.  Note that a server started manually with a command script will be a foreground process that prints some basic engine messages to the terminal; normally this is just a waste of a terminal window, but if you're trying to debug some issue with your server this might be helpful.

The files directly in "/home/gameservers" are some example commands and the utility "myip" script.

The files in the "scriptlib" subdirectory contain the actual brains of the commands.

The executables and data files for the game servers should be placed in a "servers" subdirectory.  There's nothing from that directory in this repository (yet?) but I'll discuss its structure below because the scripts work with that structure.

game server commands
--------------------

Other than "myip", all the files that live directly in "/home/gameservers" are commands that are invoked by the init script of the same name.

Each command script represents a particular server configuration.  Installing or uninstalling a server involves (among other things) adding or removing a command script.  A command script describes a particular game server (by specifying the "server\_loop" variables listed below) and then runs the "server\_loop" code.

Reconfiguring a server may involve changing some variable values in a command script, or modifying the server launch scripts (described below) that specify the command-line arguments for the server executable, and/or modifying server assets like configuration files.

Command scripts should have execute permissions if you want to run them manually.

common code: "myip"
-------------------

"myip" is a script that returns the IP address that will be used to connect to a server, since server launch invocations tend to need that information.  This is a dumb/simple script that only works if the host has a single net interface.  It is used by "server\_loop".

Also I run it manually every now and then, since I actually run these servers in a portable VM that gets a dynamic IP address.  "myip" should probably be moved into the "scriptlib" directory, but I got used to just logging into the VM console and quickly typing "myip".

"myip" should have execute permissions if you want to run it manually.

**\* ! \*** On a multi-interface host, you'd need to be able to specify something in the command script that indicated which interface to use, then have "myip" make use of that selection, then use the appropriate command-line argument when launching the server to specifically ask the server to bind to the address returned by "myip".  Seems doable but I haven't experimented with it.

common code: "server\_loop"
---------------------------

"scriptlib/server\_loop" is the main script that runs a server executable and restarts it if it crashes.  "server\_loop" manages creating and deleting the PID files that the init scripts use to determine if a server is currently running.  You should *not* need to modify "server\_loop" in any way when installing, uninstalling, or reconfiguring a server.

A command script should set up these variables before using "server\_loop":

* BASEDIR : directory where the "servers" and "scriptlib" directories and "myip" are (in my case, this is always "/home/gameservers")
* SERVERTYPE : designator for the server executable (in my case, either "q1" or "q3"); used in naming conventions for server launch scripts and the directories containing server executables
* GAMETYPE : designator for the game/mod code to be used by this server (in my case, "ktx\_ctf", "cpma\_arena", etc.); used in naming conventions for server launch scripts
* SERVERPORT : port that clients should contact the server on
* SERVERDIR : optional; the name of a subdirectory where the server executable is... more on this below

When "server\_loop" executes, it chooses a new working directory.  If SERVERDIR is defined, then the working directory will be ${BASEDIR}/servers/${SERVERTYPE}_server/${SERVERDIR}

If SERVERDIR is not defined then the working directory will just be ${BASEDIR}/servers/${SERVERTYPE}_server

The section below on the "servers" directory structure has some discussion on why you might or might not want to have a unique SERVERDIR for each of the servers that share a particular executable.

To actually launch the server, "server\_loop" runs some other script from "scriptlib", chosen according to this naming convention: ${SERVERTYPE}\_${GAMETYPE}\_server

server launch scripts
---------------------

Other than "server\_loop", the files in the "scriptlib" directory are server launch scripts and any common code shared by those scripts.  This repository contains example server launch scripts; they're the scripts used for our QuakeWorld and Quake 3 servers.

The "q1\_ktx\_common\_server" and "q3_cpma\_common\_server" files contain common logic for launching most of our servers.  Usually the environment variables and the different working directories provide all the distinction we need for the different server behaviors.  So you'll see that most of the server launch scripts just run this common code.

But "q1\_excoop\_server" needs to use slightly different command-line options than the other QuakeWorld servers, so it gets its own unique launch script rather than using "q1\_ktx\_common\_server".

The command-line options and config file names in these example scripts are just the ones that I happen to use for our local LAN; they may not be right for anyone else.  (Although if you notice something I'm doing that is just plain wrong, please let me know.)

Particularly note that the Quake 3 server command lines set the "sv\_dlURL" variable, because my host has a webserver that provides pk3 files for high-speed downloads supported by the ioquake3 client.  Each server has its own directory of downloadable files that is related to the SERVERDIR variable.  You would *not* want to set "sv\_dlURL" in your command line if you don't have such a webserver configured.  (The webserver setup is kind of interesting so I may add some info about that at a later date.)

**\* ! \*** I'm thinking about getting rid of server launch scripts and having the command scripts just pass the command line down to the "server\_loop" code.  I'd probably still want to stash some shared command-line definitions in files in "scriptlib", and then pull the shared content into the command script, but at least that setup will allow you to see what affects the server launch/configuration just by looking at the command script code.

Servers Directory
===================

The actual game server executables and data live in the ${BASEDIR}/servers directory, which in my case is "/home/gameservers/servers".  The executables are placed in a particular directory structure according to what the server launch scripts expect.  None of those assets are in this repository, but it's worth describing the layout here.

Subdirectories under "servers" are named with this convention: ${SERVERTYPE}\_server

The server executable (such as "mvdsv" or "ioq3ded.i386") may live in such a subdirectory.  However, if the command script defines the SERVERDIR variable, then the executable is expected to be placed in a further subdirectory with the name defined by SERVERDIR.  (If that is unclear, look inside the "server\_loop" script to see how it deals with these variables.)

The reason I support this difference in executable placement:

When I ran some Skulltag servers, I found it convenient to just dump all the Skulltag/Doom related stuff into one directory, regardless of whether those files were used to launch a co-op server or a deathmatch server.  The distinction between the Skulltag server varieties was just a matter of specifying some options, rather than using different game code and data.  (I know there's no Skulltag server stuff in here at the moment; I've ripped it out and may replace it with Zandronum.)

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

(So because of this structure, the command scripts for the various QuakeWorld servers specify a SERVERDIR value of "excoop_server", "ktx_ctf_server", or "ktx_dm_server".)

Basically I wanted to have *some* sharing of assets between servers, because when I change or update common stuff I don't want to have to remember to change it in multiple places.  But some other things shouldn't be shared.  Obviously the specific server config files must differ; also it was better to have separate map collections so that (for example) map voting options wouldn't be flooded with irrelevant stuff.  And any serverside-recorded demos from different servers will be nicely segregated with this layout.  Ditto for logging.

Note that having a different working directory for each server also means that you don't need as much (if any) variety in your launch scripts for the different servers.  For example you can always tell the server to use "mylan.cfg" and it will pick up the one relative to its own working directory, rather than having to have a different config file name for each server.

Anyway all of that is just my own personal setup.  The scripts largely don't care how you lay out your server assets; server launch really just boils down to two things:

* "server\_loop" will pick a working directory based on the SERVERTYPE and (if specified) SERVERDIR variables
* "server\_loop" runs some other script selected from the "scriptlib" directory based on the naming convention ${SERVERTYPE}\_${GAMETYPE}\_server and that script does... whatever you want.
