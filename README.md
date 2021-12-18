# tabsave
Save file backup utility for the game They Are Billions

## A Word About Cheating
When I designed this software and decided to make it open source, I envisioned it being useful for anyone interested in 
testing game mechanics as well as content creators.
Generally I would recommend most people play the game without this tool. 

This software makes backing up and restoring save files very easy and convenient when compared to doing it manually, 
but it doesn't do anything you can't manually.

That said, using backups to circumvent the intentional save mechanics in They Are Billions is without question cheating.

If you don't want to cheat, then don't use this software.

## Installation

### Prerequisits

#### Windows 11 (others might work)
This software was designed for and tested on Windows 11. It is very likely that this software will function just fine on 
other systems, but thus far it hasn't been tested. 

#### Python 3
To run the software you will need to have Python 3 installed. 
I designed the software to run on Python 3.9, but you may find that it runs on some older versions of Python 3. 

###Clone the Repository or Download the Files
At the moment the only file that is needed to run the program is the `tabsave.py` file. Where you save/clone is 
insignificant.

### Make tabsave Command (optional)
The goal with this step is to make using the command as easy as possible from the command line. 

This is nice if you would rather type `tabsave Survival1` instead of `python3 "C:\Users\<username>\tabsave\tabsave.py" Survival1`

There are a number of ways to accomplish this. You could create an alias, a function, create a script (or batch file) 
in your `bin` directory, or add the directory where you saved the script to your `Path` environment variable 
(and add `.py` to `PATHEXT`).

Eventually we may create an installer to do this automatically but for now you'll have to figure it out for yourself if 
you want the convenience.

## Usage
The following are going to assume you mannage to get things set up to run like a command named `tabsave`.

Otherwise, just replace `tabsave` with `python3 "C:\Users\<username>\tabsave\tabsave.py"` replacing 
`"C:\Users\<username>\tabsave\tabsave.py"`with the absolute path to the tabsave python file.

### Backup
Create a backup of a specified save file.    
*Note: To manually trigger the game to save you must exit the current game before running this command.*
#### default mode
The default mode is to create a backup. 
This means that if you only provide the save name the program will try to create a backup.

To back up a save named `Survival1` simply run the following:  
```commandline
tabsave Survival1
```
#### Explicitly Invoke Backup
If you prefer you can also use the `-b` or `--backup` options to explicitly invoke the backup command.

```commandline
tabsave Survival1 -b
```
```commandline
tabsave Survival1 --backup
```

#### Backup with a Message
Sometimes it is nice to label your backups. You can do this by using the `-m` or `--message` option.
```commandline
tabsave Survival1 -m "Final Wave"
```
```commandline
tabsave Survival1 --message "Built First Sawmill"
```

#### Declaring Backup Number
By default, each time the backup command is executed a new backup is created. If no backups exist, the first backup will
be number 1, otherwise it uses the number following the largest backup for the save.



Occasionally you may wish to overwrite a specific backup. You can do this by using the `-n`  option.

The following will create backup number 3 or overwrite it if it already exists:

```commandline
tabsave Survival1 -n 3
```

*Note: Backup number 0 is treated like a temprory backup and will be overwritten anytime the restore command is invoked.
Don't use `-n 0`.*


### Restore
This will overwrite the game's save file with a backup.

With the default operation the highest backup number is selected. Unless the `-n` option was used during backup, it will be the
most recent backup.

To invoke the restore command you use the `-r` or `--restore` options
```commandline
tabsave Survival1 -r
```
```commandline
tabsave Survival1 --restore
```

#### Declaring Backup Number
If you need to restore a different backup than the one with the greatest number, you can use the `-n` option similar to 
how it was used in the backup command.
```commandline
tabsave Survival1 --restore -n 3
```
#### Automatic Backup During Restore
To allow for corrective measures in case the restore command is accidentally invoked, we create a temporary backup number 
0 of the save before actually overwriting the save. If you need to try recovering a save named `Survival1` that was 
just overwritten with a backup, you would use the following command:
```commandline
tabsave Survival1 -r -n 0
```

### List Backups
You can list all backups for a given save using the `-l` or `--list` option.

By default, it will only list the backup numbers that exist

```commandline
tabsave Survival1 -l
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

To show the paths use the `-m` or `--message` option.

```commandline
tabsave Survival1 -l -m
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
tabsave Survival1 -l -p
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
You may want to list all saves. You can acheave this with the `-L` or `-list-all` option. 

Example:
```commandline
tabsave -L
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
tabsave -L -v -m
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
If you need to delete all the backups for a specific save file, use the `--delete` option

Example: 
```commandline
tabsave Survival1 --delete
```

[comment]: <> (#### Delete specified backups)

[comment]: <> (If you wish to only delete a subset of the save's backups, use the `-n` option.)

[comment]: <> (Example - Delete backup 1: )

[comment]: <> (```commandline)

[comment]: <> (tabsave Survival1 --delete -n 1)

[comment]: <> (```)

[comment]: <> (Example - Delete backup 1 and 3: )

[comment]: <> (```commandline)

[comment]: <> (tabsave Survival1 --delete -n 1 -n 3)

[comment]: <> (```)

