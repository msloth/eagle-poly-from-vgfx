# eagle-poly-from-vgfx #

_Tool for creating Cadsoft Eagle polygons from vector graphics._

This tool allows you to create polygons in the Cadsoft Eagle PCB
design software. These polygons can be placed on silkscreen or
copper layer, or just any layer, and be named whatever.

This allows you to create PCB artwork in e.g. Inkscape and import
it to Eagle. Eagle has crappy support for creating this in itself
so one has to rely on external tools.

## Method ##

0. You have a Eagle project in which you want some nice artwork.
   You also have a .svg vector graphics file with this artwork.
1. Run this tool on the .svg, with the parameters set as you want.
2. Save the output to a file, e.g. through the > operator, named 
   whatever.scr.
3. In Eagle board layout you run a "User script" (find it in the
   menues) and pick the script you created in 2).
4. The script will create the polygons.
5. If it went haywire, you probably didn't follow the instructions
   for preparing the .svg correctly, or the stars were not aligned.

## Prerequisites ##

Nothing specific really. Python. Someway of running the script:
* _Linux_ a shell
* _OSX_ a shell (the terminal)
* _Windows_ a shell, e.g. Cygwin

## Limitations and won't fix ##

* Cannot handle curves of any kind. Thus, they should be converted to straight paths first. Follow the guide below.
* Cannot handle hollow polygons (or whatever to call them) due to the way Eagle works. Examples are the letters d, a, o, p etc. Follow the instructions and you should be fine.

## Instructions ##

Instructions on how to prepare the SVG before running the script. The reason we do this is that we can't handle curves or hollow shapes, so we convert everything to linear paths with plenty of nodes, and split up any hollow shapes.
This is adapted from the inspiration to this script: https://github.com/cmonr/Eagle-ULPs.

* In Inkscape 0.47 or newer, Preferences > SVG output > Path data, untick "Allow relative coordinates"
* Type out the text that you want. Format it and such.
* Lock the height/width ratio
* Change height to 100 (this helps with changing the ratio)
* Ctrl-Shift-C (Object to Path)
* Select all (w/ Node Cursor)
* Extensions > Modify Path > Add Nodes (Default settings are alright)
* Extensions > Modify Path > Flatten Beziers (Default settings are alright)
* For the closed loop letters O,o,D,d,etc...
- Draw a rectangle dividing the letter ( O => ([)] )
- Select the rectangle and the letter
- Ctrl-/ (Division)
- Repeat with all closed letters
- Select all (w/ Node Cursor)
* Ctrl-Shift-K (Break Apart) <- important step
* Save As > Plain SVG

## Todo ##

A few things I will do a rainy day unless I get a pull request before that (hint hint nudge nudge).

* functionality: mirror x/y
* bug: rotation, it shifts it a bit from 0,0 so re-calculate and shift back
* usability: make the bounding box first of all in the output, makes easier to ctrl-z in eagle until just before script
* functionality: perform rotation not around (0,0), but around a centerpoint/center of gravity
* functionality: handle lines in list of points, eg L, V, H, as they may have only one datapoint, not x,y
* cleaning: change string handling to more handy %s/%d etc notation

### Won't fix ###

ie things/features that I won't implement probably ever

* handle curves in the list of points, as designated by 'c', 'b' - instead, follow the instructions above.
* the bounding box will include lots of dead space if (-r || -o) - minor issue.

## Background and cred ##

I wanted to have some nice PCB artwork but Eagle, the one PCB design sw I could use, had lousy support for this. There already existed a tool, written in Eagle ULP (user language program) scripting notation (similar to C but APIs to learn and whatnot). When I used it, it crashed with no explanation and instead of learning Eagle ULP (useless apart from this) I instead wrote this to parse a SVG and output a Eagle script instead. Now I have much more features than the previous one, but I owe the author(-s) to the script at https://github.com/cmonr/Eagle-ULPs a great deal as they outlined the method to convert SVG's with curves into linear path-only SVGs suitable for this script. So, thanks a lot! I hope you have use of this tool!

