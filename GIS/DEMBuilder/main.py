#!/usr/bin/env python3
# coding: utf-8

"""
DEMBuilder
Author:     Lucka
Version:    0.1.0
License:    MIT
"""

# Command line options
optionsHelp = """Command line options:
    \033[1m-i --input       <filename>\033[0m   Filename of raw data, suffix required
    \033[1m-o --output      <filename>\033[0m   Filename for result, suffix not required
    \033[1m-r --resolution  <number>\033[0m     Resolution for analysis, in meter
    \033[1m   --minimum     <number>\033[0m     The minimum of points in search circle
    \033[1m-h --help\033[0m                     Display this help text
"""

# Modules
import sys, getopt, time
import DEMKit
from DEMKit import Bound
import GraphicKit

def main():
    # Process the command line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hi:o:r:",
            ["help", "input=", "output=", "resolution=", "minimum="])
    except getopt.GetoptError as error:
        print("Error: {error}".format(error = error))
        print(optionsHelp)
        exit()

    print(__doc__)
    if len(opts) == 0:
        print("Command line options are required.")
        print(optionsHelp)
        exit()

    inputFilename = ""
    outputFilename = ""
    resolution = 10.0
    minimum = 3

    for opt, argv in opts:
        if opt in ("-h", "--help"):
            print(optionsHelp)
            return

        elif opt in ("-i", "--input"):
            inputFilename = argv

        elif opt in ("-o", "--output"):
            outputFilename = argv

        elif opt in ("-r", "--resolution"):
            resolution = float(argv)

        elif opt in ("--minimum"):
            minimum = int(argv)

        else:
            print("The option \`{opt}\` is invalid.".format(opt))
            print(optionsHelp)

    if inputFilename == "":
        print("Input filename undefined, use -i or --input.")
        exit()
    if outputFilename == "":
        print("Output filename undefined, use -o or --output.")
        exit()

    # Read the data and generate SVG
    print("Loading data from {filename}...".format(filename = inputFilename))
    pointList = DEMKit.loadData(inputFilename)
    print("Loaded {count} points.".format(count = len(pointList)))
    open(outputFilename + ".svg", "w").write(GraphicKit.drawPointsWithGrids(pointList, Bound(pointList), resolution))

    startTime = time.time()
    print("Building DEM...")
    gridList = DEMKit.calculateDEM(pointList, resolution, minimum)
    print("Spent {0:.2f} seconds.".format(time.time() - startTime))
    GraphicKit.display3D(gridList)

    print("Generate result files...")
    open(outputFilename + "-result.svg", "w").write(GraphicKit.drawPointsWithGrids(gridList + pointList, Bound(gridList + pointList), resolution, showElevation = True))
    open(outputFilename + "-grid.svg", "w").write(GraphicKit.drawGrayLevelGrids(gridList))
    outputStr = ""
    for grid in gridList:
        outputStr += "{x:g} \t{y:g} \t{elevation:g}\n".format(x = grid.x, y = grid.y, elevation = grid.elevation)
    open(outputFilename + ".txt", "w").write(outputStr)
    print("Finished.")

if __name__ == '__main__':
    main()
