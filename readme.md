# devtool
***
Devtool is a build framework to make cross-platform baremetal development simple across a variety of devices.  It uses a combination of GNU make, Python and kconfig.

Devtool has relatively few dependencies which you should install or have installed:

* build-essential (gcc, make, and friends)
* libncurses-dev
* python

You'll also need git to obtain the source.

### Supported devices
* Pollux/LF1000 
  - Augen e-go
  - LeapFrog Didj
  - NC600
* Samsung Exynos3
  - FriendlyARM mini210s

## Initial setup
Clone the devtool repository:
> `git clone git://github.com/jkent/devtool.git`

Put devtool's bin directory in your path:
> `export PATH=/path/to/devtool/bin:$PATH`

Create a new device profile _(substitue profilename for whatever you wish)_:
> `dt profile new profilename`

Set the options however you like, exit, and save.  Now enter a shell for your profile:
> `dt shell profilename`

You should end up with a prompt that looks somewhat like this:
> `hostname@user:~ [dt:profilename]$`

## Project usage
Alright, so now that you have devtool setup, lets go ahead and use it with a project.  Lets say you just cloned the hypothetical 'wirligig' project.  Change directory into it:
> `cd whirligig`

You should be in your devtool shell still.  Go ahead and configure the whirligig project:
> `dt config`

And once again, set the options how you wish.  Now that you configured the project, the only thing left to do is to build it.  You have two options here; you can either build the project using _`make`_ directly, or using _`dt build`_.  If you have not used the toolchain you selected for your device profile before, devtool will automatically download and extract it inside the devtools/build-tools directory.  Simple!

## Further information
Devtool has a help system; _`dt help`_ will show you a list of commands you can use and _`dt help command`_ will show you usage information and details on that particular command.  Don't be afraid to use it!

Devtool is also designed to be friendly for development.  Check out developer.md
