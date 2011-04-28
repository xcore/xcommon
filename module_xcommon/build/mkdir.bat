@echo off
IF EXIST %1 GOTO exit
MKDIR %1
:exit