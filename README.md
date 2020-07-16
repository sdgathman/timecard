# Timecard

A simple CLI for time tracking.

The command is installed as "tcf" to avoid conflict with "tc" for linux traffic control.

Simplest use:

    $ tcf myproj write some documentation
    Thu Jul 16 09:00:03 EDT 2020

This records the user, host, timestamp, proj, description.  Now, you take a break:

    $ tcf break 
    Thu Jul 16 09:10:24 EDT 2020

You go back to work, but after a few minutes, realize that you forgot to record this.  Looking
at some file timestamps, you figure out you started working again around 9:20:

    $ tcf 0920 myproj
    Thu Jul 16 09:20:45 EDT 2020

Feeling bored, you check how long you've been working today:

    $ tcf -l1
    myproj             Thu Jul 16 09:00:03 2020     0.17 write some documentation
    break              Thu Jul 16 09:10:24 2020     0.17 
    myproj             Thu Jul 16 09:20:45 2020     0.62 
    None     myproj                 0.80
    None     break                  0.17

    TOTAL    None                   0.97

