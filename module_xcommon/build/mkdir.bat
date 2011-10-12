@ECHO OFF
:Loop
IF "%1"=="" GOTO Continue
IF EXIST %1 GOTO Skip
MKDIR %1
:Skip
CD %1
SHIFT
GOTO Loop
:Continue
