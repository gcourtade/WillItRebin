# WillItRebin
WillItRebin, NEW: support of selecting  multiple files; run it without GUI, i.e. for scripting

# Examples
help:
-----
python WillItRebinMultiShell.py -h

start with GUI:
---------------
python WillItRebinMultiShell.py

run without GUI:
----------------
python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -n 0 -q ang -r log 1.04 -s 1.5
python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -n 5 -r lin 8 -s 1.5
python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -r log 1.06 
