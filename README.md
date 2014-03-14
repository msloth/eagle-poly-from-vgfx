eagle-poly-from-vgfx
====================

Tool for creating Cadsoft Eagle polygons from vector graphics.

This tool allows you to create polygons in the Cadsoft Eagle PCB
design software. These polygons can be placed on silkscreen or
copper layer, or just any layer, and be named whatever.

This allows you to create PCB artwork in e.g. Inkscape and import
it to Eagle. Eagle has crappy support for creating this in itself
so one has to rely on external tools.

Method
======

0) You have a Eagle project in which you want some nice artwork.
   You also have a .svg vector graphics file with this artwork.
1) Run this tool on the .svg, with the parameters set as you want.
2) Save the output to a file, e.g. through the > operator, named 
   whatever.scr.
3) In Eagle board layout you run a "User script" (find it in the
   menues) and pick the script you created in 2).
4) The script will create the polygons.
5) If it went haywire, you probably didn't follow the instructions
   for preparing the .svg correctly, or the stars were not aligned.

Prerequisites
=============

Nothing specific really. Python. Someway of running the script:
  Linux: a shell
  OSX: a shell (the terminal)
  Windows: a shell, e.g. Cygwin
