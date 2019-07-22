What?
=====
These are the scripts I use to run game servers for our local LAN on a Debian Linux host; they've also been used on a Raspberry Pi running Raspbian Linux.  This setup should also have application to other Linux environments with some tweaking of init scripts.

This is just a raw file dump for now.  There's much more that could be done with this: proper packaging, customizing some bits on install, packages for the actual server files... well, maybe someday.

On my server, all game server executables and content are kept under the home directory of a particular user ("gameservers").  They can be started through init scripts, but even in that case they are always run as that user.

Init Scripts
============

overview
------------------------------

Init scripts are useful if you want to autostart one or more servers when the host boots up, and stop servers nicely on host shutdown.  (I won't go into details about configuring init scripts here; that's generic Debian/Linux behavior that is documented in plenty of other spots.)

Even if you don't want that behavior, init scripts can also be invoked manually to stop/start/restart servers and check whether a server is running, and they will refuse to start a particular server if it is already running.  Servers run through these init scripts will be run as background "daemon" processes, so they don't tie up a terminal window.  Init scripts also provide a nice hook to use with Webmin.

__\* ! \*__ Currently if you try to start a server when it is already running, the script will just silently do nothing.  It would be better to have it print a warning.

In this setup, a distinct "server" is not just an executable but also some combination of options and assets.  Each init script specifies some variables that define a specific server.

So for example you could have one init script for a Quake 3 CTF server, another script for a small-playercount Quake 3 DM server, and another script for a large-playercount Quake 3 DM server.  Even though they all use a Quake 3 executable, you could run them all at the same time (if your host is beefy enough).  But if you tried to start "small-playercount Quake 3 DM server" while an instance of "small-playercount Quake 3 DM server" was already running, that start command would be rejected.

game server init scripts
------------------------

Each init script represents a particular server configuration.  Installing or uninstalling a server involves (among other things) adding or removing an init script.  An init script describes a particular server (by specifying the "gameserver.sh" variables listed below) and then runs the "gameserver.sh" code.

The need to have a separate init script for each game server, rather than having an UberScript that takes an argument about which server to control, is basically a constraint of the way init scripts are handled at startup/shutdown time.  You need separate scripts for separate services, if you don't want to replicate existing service-management functionality in your own special snowflake of a configuration system.  With a small number of game server scripts the current approach seems OK to me.

If you want a particular game server to be ready to run, but *not* automatically start when the host starts, you should still have an init script for that game server.  Just configure your host's init script behavior so that the game server does not autostart.

Reconfiguring a server should *not* involve any modification of an init script; instead reconfiguration would involve changing the command scripts (described below), and/or modifying server assets like configuration files.

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

* The working directory for executing COMMAND will be the directory where the COMMAND file is located.
* The PID file will be created as ${COMMAND}.pid

The PID file location is not configurable in the init script because I want to make sure that normal fiddling with server configuration won't make the init script and command script disagree about where the PID file is located.  Similarly on the command-script side of things, the PID file location is determined internally rather than being affected by normal configuration changes.

Command Scripts
===============

overview
------------------------------

The files under "/home/gameservers" in this repository are the scripts that actually run the servers.  Most of these are the commands that are launched by the init scripts, and the rest are utility/subroutine scripts used by the command scripts.

There's a pretty clean separation between this stuff and the init scripts.  The init scripts don't know anything about the internals of the commands or the other scripts used to run the servers.

Conversely, the commands don't need to be invoked through the init scripts; you could run the commands manually, if you don't care about any of the niceties described in the Init Scripts section.  Note that a command script started manually will be a foreground process that prints some basic engine messages to the terminal; normally this is just a waste of a terminal window, but if you're trying to debug some issue with your server this might be helpful.

The files directly in "/home/gameservers" are some example command scripts.

The files in the "scriptlib" subdirectory contain code shared among the command scripts.

The executables and data files for the game servers should be placed in their own separate subdirectory.  (In my case, "/home/gameservers/servers".)  There's nothing from that directory in this repository (yet?) but I'll discuss its structure below.

game server command scripts
---------------------------

Each command script represents a particular server configuration.  Installing or uninstalling a server involves (among other things) adding or removing a command script.  A command script describes how to launch a particular game server (by specifying the "server\_loop" variables listed below) and then runs the "server\_loop" code.

Reconfiguring a server may involve modifying a command script and/or modifying server assets like configuration files.

The various files under "/home/gameservers" in this repository are examples of command scripts.  They're the command scripts that I use for our QuakeWorld and Quake 3 servers.  The command-line options and config file names in these example scripts are just the ones that I happen to use for our local LAN; they may not be right for anyone else.  (Although if you notice something I'm doing that is just plain wrong, please let me know.)

__\* ! \*__ Particularly note that the Quake 3 server command lines set the "sv\_dlURL" variable, because my host has a webserver that provides pk3 files for high-speed downloads supported by the ioquake3 client.  Each server has its own directory of downloadable files that is related to the SERVERDIR variable.  You would *not* want to set "sv\_dlURL" in your command line if you don't have such a webserver configured.  (The webserver setup is kind of interesting so I may add some info about that at a later date.)

__\* ! \*__ There's still quite a bit of common code between various command scripts.  Might be good to factor that out and dump it into "scriptlib".  On the other hand, having every relevant configuration in the command script makes things simpler to understand.

Command scripts should have execute permissions if you want to run them manually.

common code: "myip"
-------------------

"scriptlib/myip" is a script that returns the IP address that will be used to connect to a server, since server launch invocations tend to need that information.  This is a dumb/simple script that only works if the host has a single net interface.  It is used by "server\_loop".

Also I run it manually every now and then, since I actually run these servers in a portable VM that gets a dynamic IP address.  It's a quick way to find the address the servers will be using.

"myip" should have execute permissions if you want to run it manually.

__\* ! \*__ On a multi-interface host, "myip" will pick one of the IP addresses. There's currently no way to tell it which one to pick.

common code: "server\_loop"
---------------------------

"scriptlib/server\_loop" is the main script that runs a server executable and restarts it if it crashes.  "server\_loop" manages creating and deleting the PID files that the init scripts use to determine if a server is currently running.  You should *not* need to modify "server\_loop" in any way when installing, uninstalling, or reconfiguring a server.

A command script should set up these variables before using "server\_loop":

* SERVERROOT : working directory used when launching the server
* CMDLINE : command line for launching the server

The section below on the servers directory structure has some discussion on how you might want to arrange the working directories for your servers.

Servers Directory
===================

When you pick the working directories that you want to use for your servers, at first glance you might think about using the same working directory for all servers that share a given server executable.

That is what I did when I was running Skulltag servers with this setup.  (I've ripped out the Skulltag stuff for now; may add a Zandronum configuration back in later.)  It was convenient to just dump all the Skulltag/Doom related stuff into one directory, regardless of whether those files were used to launch a co-op server or a deathmatch server.  The distinction between the Skulltag server varieties was just a matter of specifying some options, rather than using different game code and data.  Overall it didn't cause any problems to run multiple servers out of the same directory.

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

__\* ! \*__ Take this exact arrangement with a grain of salt.  It involves having a "server.cfg" file in the "ktx" directory that executes various other config files, including "../mvdsv.cfg".  However I started another setup using the latest mvdsv built from source, and it is no longer happy with config file paths that start with "../".  So some things need to be shuffled around, but the basic idea is the same.

Those "excoop\_server", "ktx\_ctf\_server", and "ktx\_dm\_server" directories are the different working directories specified by my command scripts for those three servers.  (You can check the command script examples to see how they specify SERVERROOT.)

Basically I wanted to have *some* sharing of assets between servers, because when I change or update common stuff I don't want to have to remember to change it in multiple places.  But some other things shouldn't be shared.  Obviously the specific server config files must differ; also it was better to have separate map collections so that (for example) map voting options wouldn't be flooded with irrelevant stuff.  And any serverside-recorded demos from different servers will be nicely segregated with this layout.  Ditto for logging.

Note that having a different working directory for each server also means that you don't need as much (if any) variety in your command scripts for the different servers.  For example you can always tell the server to use "mylan.cfg" and it will pick up the one relative to its own working directory, rather than having to have a different config file name for each server.

Anyway all of that is just my own personal setup.  The scripts largely don't care how you lay out your server assets; you can give "server\_loop" whatever working directory and command line you like.

Webmin Plugin
=============

The "gameservers.wbm.gz" file is a plugin that you can import into Webmin, to get a serviceable web interface for starting/stopping these game servers. It makes liberal use of existing service-management code provided by Webmin ... it's a hasty "My First Webmin Plugin" sort of exercise but I've found it handy. I've tried it with both Webmin 1.620 (shown below) and 1.920.

![Webmin plugin screenshot](webmin_plugin/webmin-1-620_screenshot.png?raw=true)

The individual plugin files are also included here if you want to examine or change them.  The importable plugin "gameservers.wbm.gz" is just a tar package of the "gameservers" directory and contents -- given the "wbm" extension instead of "tar" -- that is then gzipped.

One ripe-for-improvement bit is that the "config" and "config.info" files hardcode the available server scripts.  If you have a different set of scripts then you have to edit those files...  preferably before importing the plugin, or else you'll need to edit both the installed plugin (files located in "/usr/share/webmin/gameservers" on my system) as well as the current stored configuration ("/etc/webmin/gameservers/config").

Final note: the "os_support" field of "module.info" specifies "debian-linux".  That may be overly restrictive and you can certainly change it (e.g. to "\*-linux") or remove that line entirely if you want to experiment with it on other Linux flavors.
