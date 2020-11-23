# Timecard

A simple CLI for time tracking.

The command is installed as "tcf" (timecard fast enty) to avoid conflict with
"tc" for linux traffic control.

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

A customer calls, a lawn service company, and you switch gears:

    $ tcf lawns-phone
    Thu Jul 16 10:09:13 2020

When you hang up, you go back to myproj, and check how long you spent on the phone:

    $ tcf myproj
    Thu Jul 16 09:20:45 2020
    $ tcf -l1
    myproj             Thu Jul 16 09:00:03 2020     0.17 write some documentation
    break              Thu Jul 16 09:10:24 2020     0.17
    myproj             Thu Jul 16 09:20:45 2020     0.81
    lawns-phone        Thu Jul 16 10:09:13 2020     0.18
    myproj             Thu Jul 16 10:19:57 2020     0.00
    None     myproj                 0.98
    None     break                  0.17
    lawns    lawns-phone            0.18

    TOTAL    None                   1.15
    TOTAL    lawns                  0.18

Lawns was configured in ~/.timecard/timecard.cfg as a client.  (TODO: synchronize client list
between hosts and users.)

    $ cat ~/.timecard/timecard.cfg
    [main]
    user = stuart
    # default client
    dayjob = bms

    [clients]
    personal = foo,bar,baz
    lawns = lawns

BILLING
    List charges for a client

    $ tcf -c <client>

    Create a Bill
    $ tcf BILL-<client> Invoice #<12345>
    This becomes the Last bill for the client, by putting a marker record.
    This becomes a marker record which the "-c" method uses to filter only
    the unbilled time.

