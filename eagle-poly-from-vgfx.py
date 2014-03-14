#!/usr/bin/python
# 
# Convert svg to a script that in Cadsoft Eagle (PCB designer software) will be realized as a 
# filled polygon on any layer. Run the script with no arguments for a list of options.
# 
# Author: Marcus Linderoth <linderoth.marcus@gmail.com>
# 
# Limitations
#  Cannot process curves of any kind, only straight lines, but it can easily be worked around (see below)
#  
# 
# Instructions on how to prepare an SVG for this script
# (adapted from the inspiration to this script: https://github.com/cmonr/Eagle-ULPs)
#   In Inkscape 0.47 or newer, Preferences > SVG output > Path data, untick "Allow relative coordinates"
#   Type out the text that you want. Format it and such.
#   Lock the height/width ratio
#   Change height to 100 (this helps with changing the ratio)
#   Ctrl-Shift-C (Object to Path)
#   Select all (w/ Node Cursor)
#   Extensions > Modify Path > Add Nodes (Default settings are alright)
#   Extensions > Modify Path > Flatten Beziers (Default settings are alright)
#   For the closed loop letters O,o,D,d,etc...
#     Draw a rectangle dividing the letter ( O => ([)] )
#     Select the rectangle and the letter
#     Ctrl-/ (Division)
#     Repeat with all closed letters
#     Select all (w/ Node Cursor)
#   Ctrl-Shift-K (Break Apart) <- important step
#   Save As > Plain SVG
# 
# Todos
#   mirror x/y!
#   make the bounding box first of all in the output, makes easier to ctrl-z in eagle until just before script
#   rotation, it shifts it a bit from 0,0 so re-calculate and shift back
#   perform rotation not around (0,0), but around a centerpoint/center of gravity
#   handle lines in list of points, eg L, V, H, as they may have only one datapoint, not x,y
#   change string handling to more handy %s/%d etc notation
# 
# Won't fix, ie things/features that I won't implement probably ever
#   handle curves in the list of points, as designated by 'c', 'b'. Too much work, instead follow instructions above.
#   the bounding box will include lots of dead space if (-r || -o), but this is a minor issue.
#   There may be issues with relative coordinates, so if you experience problems, try shutting those off in Inkscape preferences.
#   
# ------------------------------------------------------------------------------
import os
import sys
import xml.etree.ElementTree as ET
import logging
import math
# ------------------------------------------------------------------------------
def die(diestr = "", exitcode = 1, show_howto = True):
  if show_howto:
    print("Parse SVG points, convert to cadsoft eagle polygon")
    print("usage: " + sys.argv[0] + " filename.svg")
    print("Optional switches:")
    print("     -mxy == mirror the image in x ('-mx'), y ('-my'), or xy ('-mxy') axis, (not yet implemented)")
    print("     -nNAME == name the polygon NAME, eg -nGND for ground fill. Default VCC.")
    print("     -b == do /not/ draw a bounding box, that would indicate the min/max of the generated image. Very helpful, thus is default")
    print("     -sx,y == maxsize x, y mm, eg -s100,20.5. Default 100/50.")
    print("     -ox,y == origin at x, y mm. Default 0/0")
    print("     -rD == rotate by D degrees")
    print("     -px == custom scale X, useful for making sure a figure is scaled as a previously parsed one")
    print("     -la,b,c,... == output on layers a, b, c, ..., eg -lTop,tStop,Bottom,bStop")
    print("     -d == turn on debug output")
    print("     -uX == use unit X (mm, mil, in). Default is mm")
    print
    print("*** Error ***: " + diestr)
  else:
    print(diestr)
  sys.exit(exitcode)
# ------------------------------------------------------------------------------
def extract_figure(node, namespace = "", translate_x = 0.0, translate_y = 0.0, object_output = []):
  # print(node.text)
  # print(node.keys)
  # print(node.attrib)
  # print(node.items)
  # print(node.tag)
  # print(str(node))
  # ['__class__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__len__', '__module__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_children', 'append', 'attrib', 'clear', 'copy', 'extend', 'find', 'findall', 'findtext', 'get', 'getchildren', 'getiterator', 'insert', 'items', 'iter', 'iterfind', 'itertext', 'keys', 'makeelement', 'remove', 'set', 'tag', 'tail', 'text']
  has_matrix_transform = False
  if node == None:
    die("extraction error, argument was None", -1)

  # find any translation, ie if this figure has origin at some x,y != 0,0
  if node.attrib.has_key("transform"):
    transform = str(node.attrib.get("transform")).lower()
    if transform.count("translate") > 0:
      transform = transform.replace("translate(", "").replace(")", "")
      transform = transform.split(",")
      translate_x = float(transform[0])
      translate_y = float(transform[1])
    else:
      has_matrix_transform = True

  # find points
  if node.attrib.has_key("d") and has_matrix_transform == False:
    this_output = []
    path_field = str(node.attrib.get("d"))
    # check for relative of absolute coordinates
    if path_field[0] == 'M':
      points_are_relative = False
      # print('absolute coordinates')
    elif path_field[0] == 'm':
      points_are_relative = True
      # print('relative coordinates')

    # check for curve commands, they are not supported
    if path_field.count('c') > 0 or path_field.count('C') > 0:
      path_field = path_field.replace('c ', '').replace('C ', '')
      # print("******* there's a curve in the path-field, shouldn't be there. The result will likely look messed up.")

    # remove start and end letters, make lower case so we can remove other commands (l, c, etc)
    points = path_field.lower().replace("m ", "").replace(" z", "")

    # XXXXXX remove all references to curves, lines, etc, as even if they are not supported
    #   we don't want them to fail our conversion. The result may be ok anyway.
    points = points.replace(" c", "").replace(" l", "").replace(" h", "").replace(" v", "")# XXXXXX temporary until line etc are done (see below)
    points = points.split(' ')

    # parse points
    relative_x = translate_x
    relative_y = translate_y
    for point_pair in points:
      # XXXX this is todo; parse line/horiz line/vert line, etc
      # if point_pair.count('l') > 0 or point_pair.count('L') > 0:
      # line to x,y
      # if point_pair.count('h') > 0 or point_pair.count('H') > 0:
      # horiz line to y
      # if point_pair.count('v') > 0 or point_pair.count('V') > 0:
      # vertical line to x
      try:
          px, py = point_pair.split(',')
          if points_are_relative:
            xr = float(px)
            yr = float(py)
            relative_x += xr
            relative_y += yr
            this_output.append([relative_x, relative_y])
          else:
            this_output.append([float(px) + translate_x, float(py) + translate_y])
      except Exception, e:
        die("error when processing " + str(point_pair) + " " + str(e), -1)

    # ensure endpoint == startpoint
    if this_output[-1][0] != this_output[0][0] or this_output[-1][1] != this_output[0][1]:
      this_output.append([this_output[0][0], this_output[0][1]])

    # add this parsed figure to the total output
    object_output.append(this_output)

  # also parse children, except for clipPath as it has a 'd'-element but is not part of the figure
  if node.tag.replace(namespace, "").lower().count("clippath") == 0:
    for kid in node:
      extract_figure(kid, namespace, translate_x, translate_y, object_output)

# ------------------------------------------------------------------------------
def main():
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)

  # by default, we put this on Top and tStop layers
  #layers = ["Top"]
  layers = ["Top", "tStop"] # name of layers that the polygons will be drawn at
  # layers = ["Bottom", "bStop"]
  # layers = ["tPlace", "bPlace"]
  mirrorx = False           # mirror in X-axis
  mirrory = False           # mirror in Y-axis
  custom_scale = False      # use a custom scale, provided on the command line
  origin_mm_x = 0.0         # origin at (x,y)
  origin_mm_y = 0.0         # origin at (x,y)
  max_mm_x = 100.0          # default value of figure size, x
  max_mm_y = 50.0           # default value of figure size, y
  stroke_width = "0.01"     # width of polygon outline (why did I go with 0.01? Why not 0.0?)
  debug = False             # print out some more debug information during parsing
  bounding_box = True       # box around the whole figure, easy to remove and of great aid as sanity check
  polygon_name = "VCC"      # default name of polygon, pref not GND as it would disappear in ground plane
  rotation = 0.0            # angle of rotation
  unit = "mm"               # unit of measurements, mm, mil, in

  # check file
  if len(sys.argv) == 1:
    die('No arguments specified', -1)
  filename = sys.argv[1]
  if not os.path.isfile(filename):
    die("file does not exist", -2)

  # check and parse args --------------------------------------
  if len(sys.argv) > 2:
    for arg in sys.argv[2:]:
      if arg[0] != '-':
        die("error parsing arguments (missing '-'?)", -1)

      if arg[1] == 'm':       # -m == mirror the image
        if len(arg) <= 2:
          die("arg fail, specify -mx, -my, or -mxy", -1)
        for xy in arg[1:]:
          if xy == 'x':
            mirrorx = True
          if xy == 'y':
            mirrorx = True
        die("Mirror is not implemented yet.")
      
      elif arg[1] == 'n':     # -nNAME == name the polygon NAME
        polygon_name = arg.replace("-n", "")

      elif arg[1] == 'b':     # -b == do not draw a bounding box, that would indicate the min/max of the generated image
        bounding_box = False
        
      elif arg[1] == 's':     # -sx,y == maxsize x, y mm
        try:
          argp = arg.replace("-s", "")
          argcoord = argp.split(",")
          max_mm_x = float(argcoord[0])
          max_mm_y = float(argcoord[1])
        except Exception, e:
          die("arg fail (size): " + arg + "error string:" + str(e), -1)
      
      elif arg[1] == 'o':     # -ox,y == origin at x, y mm
        try:
          argp = arg.replace("-o", "")
          argcoord = argp.split(",")
          origin_mm_x = float(argcoord[0])
          origin_mm_y = float(argcoord[1])
        except Exception, e:
          die("arg fail (origin): " + arg + "error string:" + str(e), -1)
      
      elif arg[1] == 'p':     # -px == custom scale X
        try:
          scale = float(arg.replace("-p", ""))
          custom_scale = True
        except Exception, e:
          die("arg fail (scale): " + arg + "error string:" + str(e), -1)

      elif arg[1] == 'r':     # -ro == custom rotation by o degrees
        try:
          rotation = float(arg.replace("-r", ""))
        except Exception, e:
          die("arg fail (rotation): " + arg + "error string:" + str(e), -1)

      elif arg[1] == 'u':     # -uX == use unit mil, mm, in (default mm)
        try:
          unit = str(arg.replace("-u", "")).lower()
          if not unit in ["mil", "mm", "mm"]:
            die("arg fail (unit): not mm, mil, or in", -1)  
        except Exception, e:
          die("arg fail (unit): " + arg + "error string:" + str(e), -1)

      elif arg[1] == 'd':     # -d == turn on debug output
        debug = True
      
      elif arg[1] == 'l':     # -la,b,c,... == layers a, b, c, ...
        try:
          argp = arg.replace("-l", "")
          layers = argp.split(",")
        except Exception, e:
          die("arg fail (layers): " + arg + "error string:" + str(e), -1)
      else:
        die("arg fail: " + arg, -1)

  if debug:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
  else:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  logging.info('Polygon name: %s', polygon_name)
  logging.info("Size X: %f", max_mm_x)
  logging.info("Size Y: %f", max_mm_y)
  logging.info("origin X: %f", origin_mm_x)
  logging.info("origin Y: %f", origin_mm_y)
  logging.info("unit: %s", unit)
  if custom_scale:
    logging.info("Custom scale: %f", custom_scale)

  prescriptum = "grid " + unit + ";\n"
  prescriptum += "set wire_bend 2;\n"
  prescriptum += "change width 0;\n"
  prescriptum += "change thermals off;\n"
  prescriptum += "change orphans on;\n"
  prescriptum += "change isolate 0;\n"
  prescriptum += "change pour solid;\n"
  prescriptum += "change rank 1;\n"
  prescriptum += "change spacing 0.254;\n"

  postscriptum = "grid mil;\n"
  postscriptum += "change thermals on;\n"
  postscriptum += "change orphans off;\n"

  # parse the file XML
  try:
    tree = ET.parse(filename)
    root = tree.getroot()
  except Exception, e:
    die("failed to parse the SVG file for some reason:" + str(e), -1)

  # the prolog outputs some debug info, such as filename, scale etc
  prolog = "# file: " + filename + "\n"

  # find namespace, if any
  namespace = root.tag.rstrip("svg")
  logging.info('Namespace: ' + namespace)
  prolog += "# namespace: " + namespace + "\n"

  # -------------------------------------------------------------
  # parse the SVG XML for polygon paths
  parsed = []
  extract_figure(root, namespace, 0.0, 0.0, parsed)

  # -------------------------------------------------------------
  # now treat the whole figure as a unit, re-shape, report.
  min_x = min_y =  9999999999999999999999
  max_x =  max_y = 0.0
  scale_x = 1.0
  scale_y = 1.0

  # correct the coordinates to fit and see that we have a proper origin
  for part in parsed:
    # find boundaries of the object -> real size
    for point in part:
      x = point[0]
      y = point[1]
      if x > max_x:
        max_x = x
      if x < min_x:
        min_x = x
      if y > max_y:
        max_y = y
      if y < min_y:
        min_y = y
  logging.info("Max parsed X: %f", max_x)
  logging.info("Min parsed X: %f", min_x)
  logging.info("Max parsed Y: %f", max_y)
  logging.info("Min parsed Y: %f", min_y)
  prolog += "# (parsed) Max X: " + str(max_x) + ", "
  prolog += "Min X: " + str(min_x) + ", "
  prolog += "Max Y: " + str(max_y) + ", "
  prolog += "Min Y: " + str(min_y) + "\n"

  # if the figure has not origin at 0,0 we may need to bump it, ie displace it
  bump_x = -min_x
  bump_y = -min_y
  logging.info("Bump to origo, X: %f", bump_x)
  logging.info("Bump to origo, Y: %f", bump_y)
  
  # find scaling values to fit in maximum size constraints
  if not custom_scale:
    if min_x < 0.0:
      scale_x = max_mm_x / (max_x + abs(min_x))
    else:
      scale_x = max_mm_x / (max_x - min_x)
    if min_y < 0.0:
      scale_y = max_mm_y / (max_y + abs(min_y))
    else:
      scale_y = max_mm_y / (max_y - min_y)

  logging.info("Calculated Scale X: %f", scale_x)
  logging.info("Calculated Scale Y: %f", scale_y)
  if custom_scale:
    logging.info("Custom Scale chosen: %f", scale)
  else:
    scale = min(scale_x, scale_y)
    logging.info("Calculated Scale: %f", scale)

  prolog += "# Bump to origo X: " + str(bump_x) + ", "
  prolog += "Bump Y: " + str(bump_y) + ", "
  prolog += "Calculated Scale X: " + str(scale_x) + ", "
  prolog += "Scale Y: " + str(scale_y) + "\n"
  prolog += "# Chosen Scale: " + str(scale) + ", "
  prolog += "Rotation " + str(rotation) + "\n"

  # output to eagle format
  min_x = min_y =  max_x =  max_y = 0.0

  outstr = prolog
  outstr += prescriptum
  logging.info("Rotation: %f degrees", rotation)
  rotation_rad = 2 * math.pi * rotation/360
  rot_cos = math.cos(rotation_rad)
  rot_sin = math.sin(rotation_rad)

  # create commands for all the polygons, eg poly GND 0.1 (0 1) (1.3 41) (41 462) (0 1)
  part_string = ""
  for part in parsed:
    part_string += "poly " + polygon_name + " " + stroke_width
    for point in part:
      # if you rotate point (px, py) around point (ox, oy) by angle theta you'll get:
      # p'x = cos(theta) * (px-ox) - sin(theta) * (py-oy) + ox
      # p'y = sin(theta) * (px-ox) + cos(theta) * (py-oy) + oy
      x = (point[0] + bump_x) * scale
      y = (point[1] + bump_y) * scale
      if rotation != 0.0:
        xp = x * rot_cos - y * rot_sin
        yp = x * rot_sin + y * rot_cos
      else:
        xp = x
        yp = y
      x = xp + origin_mm_x
      y = yp + origin_mm_y

      if x > max_x:
        max_x = x
      if x < min_x:
        min_x = x
      if y > max_y:
        max_y = y
      if y < min_y:
        min_y = y
      part_string += " (" + str(x) + " " + str(y) + ")"
    part_string += ";\n\n"

  # for each layer we want the polygons on, we repeat the 'poly'-command
  for layer in layers:
    logging.info("Doing layer: %s", layer)
    outstr += "# Layer: " + layer + "\n"
    outstr += "change layer " + layer + ";\n"
    outstr += part_string

  # optionally draw a box around everything, so we see in Eagle if there are any rogue polygons somewhere
  if bounding_box == True:
    outstr += "# Bounding box\n"
    outstr += "poly " + polygon_name + " " + stroke_width
    outstr += " (" + str(min_x) + " " + str(min_y) + ") "
    outstr += " (" + str(min_x) + " " + str(max_y) + ")"
    outstr += " (" + str(max_x) + " " + str(max_y) + ")"
    outstr += " (" + str(max_x) + " " + str(min_y) + ")"
    outstr += " (" + str(min_x) + " " + str(min_y) + ");\n"

  outstr += postscriptum
  print(outstr)
  logging.info("Max generated X: %f", max_x)
  logging.info("Min generated X: %f", min_x)
  logging.info("Max generated Y: %f", max_y)
  logging.info("Min generated Y: %f", min_y)
  logging.info("Rotation: %f degrees", rotation)
    # print("-----------------------------------------")
# ------------------------------------------------------------------------------
if __name__=="__main__":
    main()
# ------------------------------------------------------------------------------


