# tabsave [![CI](https://github.com/Zierman/tabsave/actions/workflows/ci.yml/badge.svg)](https://github.com/Zierman/tabsave/actions/workflows/ci.yml)
Save file backup utility for the game They Are Billions

## A Word About Cheating
When I designed this software and decided to make it open source, I envisioned it being useful for anyone interested in 
testing game mechanics as well as content creators.
Generally I would recommend most people play the game without this tool. 

This software makes backing up and restoring save files very easy and convenient when compared to doing it manually, 
but it doesn't do anything that you can't accomplish manually.

That said, using backups to circumvent the intentional save mechanics in They Are Billions is without question cheating.

If you don't want to cheat, then don't use this software.

## Installation

### Prerequisites

#### Windows 11 (others might work)
This program was originally written to work on Windows 11. 
We're working on testing other operating systems, and wish to make the program as portable as possible.
It is very likely that this software will function just fine on 
other systems, but more testing is needed.

#### Python 3
To run the software you will need to have Python 3 installed. 
I designed the software to run on Python 3.7+. 

### Clone the Repository or Download the Files
At the moment the only file that is needed to run the program is the `tabsave.py` file. Where you save/clone is 
insignificant.

### Make tabsave Command (optional)
The goal with this step is to make using the command as easy as possible from the command line. 

This is nice if you would rather type `tabsave backup Survival1` instead of 
`python3 "C:\Users\<username>\tabsave\tabsave.py" backup Survival1`

There are a number of ways to accomplish this. You could create an alias, a function, create a script (or batch file) 
in your `bin` directory, or add the directory where you saved the script to your `Path` environment variable 
(and add `.py` to `PATHEXT`).

Eventually we may create an installer to do this automatically but for now you'll have to figure it out for yourself if 
you want the convenience.

## Usage
The following are going to assume you mannage to get things set up to run like a command named `tabsave`.

Otherwise, just replace `tabsave` with `python3 "C:\Users\<username>\tabsave\tabsave.py"` replacing 
`"C:\Users\<username>\tabsave\tabsave.py"`with the absolute path to the tabsave python file.

### Help
To get a help message use the `-h` or `--help` option.

Example:
```commandline
tabsave --help
```

#### Subcommand Help
To get a help message for a subcommand, use `-h` or `--help` with that subcommand.

For example to get help for the `list` command use the following:
```commandline
tabsave list --help
```

### Backup
Create a backup of a specified save file.    
*Note: To manually trigger the game to save you must exit the current game before running this command.*

To create a backup of the save named Survival1, use the following:
```commandline
tabsave backup Survival1
```
or this alias:
```commandline
tabsave b Survival1
```

#### Backup with a Message
Sometimes it is nice to label your backups. You can do this by using the `-m` or `--message` option.

Examples:

```commandline
tabsave backup Survival1 --message "Built First Sawmill"
```
```commandline
tabsave backup Survival1 -m "Final Wave"
```

#### Declaring Backup Number
By default, each time the backup command is executed a new backup is created. If no backups exist, the first backup will
be number 1, otherwise it uses the number following the largest backup for the save.



Occasionally you may wish to overwrite a specific backup. You can do this by using the `-n`  option.

The following will create backup number 3 or overwrite it if it already exists:

```commandline
tabsave backup Survival1 -n 3
```

*Note: Backup number 0 is treated like a temprory backup and will be overwritten anytime the restore command is invoked.
Don't use `-n 0`.*


### Restore
This will overwrite the game's save file with a backup.

With the default operation the highest backup number is selected. Unless the `-n` option was used during backup, it will be the
most recent backup.

Examples:
```commandline
tabsave restore Survival1
```
```commandline
tabsave r Survival1
```

#### Declaring Backup Number
If you need to restore a different backup than the one with the greatest number, you can use the `-n` option similar to 
how it was used in the backup command.
```commandline
tabsave restore Survival1 -n 3
```
#### Automatic Backup During Restore
To allow for corrective measures in case the restore command is accidentally invoked, we create a temporary backup number 
0 of the save before actually overwriting the save. If you need to try recovering a save named `Survival1` that was 
just overwritten with a backup, you would use the following command:
```commandline
tabsave restore Survival1 -n 0
```

### List Backups
You can list all backups for a given save using the `list` command.

By default, it will only list the backup numbers that exist

Example:
```commandline
tabsave list Survival1
```
or this alias
```commandline
tabsave l Survival1
```
will output something like this:
```
Number
------
1
2
3
4
```
#### Show Messages

To show the messages use the `-m` or `--message` option.

```commandline
tabsave list Survival1 -m
```
will output something like this:
```
Number         Message
----------------------------
1              -------
2         Just Built Sawmill
3         Just Built Farm
4         Just Built Bank
```


#### Show Paths

To show the paths use the `-p` or `--path` option.

```commandline
tabsave list Survival1 -p
```
will output something like this:
```
Number                          Path_to_Directory
------------------------------------------------------------------------
1         "C:\Users\user\MyDocuments\My Games\They Are Billions\Saves\backups\Survival1\1"
2         "C:\Users\user\MyDocuments\My Games\They Are Billions\Saves\backups\Survival1\2"
3         "C:\Users\user\MyDocuments\My Games\They Are Billions\Saves\backups\Survival1\3"
4         "C:\Users\user\MyDocuments\My Games\They Are Billions\Saves\backups\Survival1\4"
```

### List All Saves
You may want to list all saves. You can achieve this with the `list-all` command. 

Example:
```commandline
tabsave list-all
```
or this alias
```commandline
tabsave L
```
will output something like this:
```
Josh1 has 2 backups
Josh2 has 3 backups
Survival1 has 5 backups
```
*Note: You don't need to provide a save name for this command.*


#### Verbose Output
If you use the `-v` or `--verbose` option, you'll get more output.

You can get more fields in this output with the `-p`/`--path` and `m`/`--message` options.

Example: 
```commandline
tabsave list-all -v -m
```
will output something like this:
```
**********************************
*                                *
*      Josh1 has 2 backups       *
*................................*
*                                *
*  Number    Message             *
*  -----------------             *
*  0         -------             *
*  1         -------             *
*                                *
**********************************
*                                *
*      Josh2 has 3 backups       *
*................................*
*                                *
*  Number    Message             *
*  -----------------             *
*  0         -------             *
*  1         -------             *
*  2         -------             *
*                                *
**********************************
*                                *
*    Survival1 has 4 backups     *
*................................*
*                                *
*  Number         Message        *
*  ----------------------------  *
*  1              -------        *
*  2         Just Built Sawmill  *
*  3         Just Built Farm     *
*  4         Just Built Bank     *
*                                *
**********************************
```



### Delete

#### Delete a Specific Save's Backups
If you need to delete all the backups for a specific save file, use the `delete` command.

Example: 
```commandline
tabsave delete Survival1
```

[comment]: <> (#### Delete specified backups)

[comment]: <> (If you wish to only delete a subset of the save's backups, use the `-n` option.)

[comment]: <> (Example - Delete backup 1: )

[comment]: <> (```commandline)

[comment]: <> (tabsave delete Survival1 -n 1)

[comment]: <> (```)

[comment]: <> (Example - Delete backup 1 and 3: )

[comment]: <> (```commandline)

[comment]: <> (tabsave delete Survival1 -n 1 -n 3)

[comment]: <> (```)

