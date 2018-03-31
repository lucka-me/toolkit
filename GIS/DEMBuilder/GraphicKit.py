#!/usr/bin/env python3
# coding: utf-8

"""
GraphicKit for DEMBuilder
Author:     Lucka
Version:    0.1.0
License:    MIT
"""

import math
from DEMKit import Point
from DEMKit import Grid
from DEMKit import Bound

# Matplotlib
import numpy
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D

# Generate SVG
def drawPointsWithGrids(pointList: [Point], bound: Bound, resolution: float, showElevation: bool = False, gridSize: int = 24, padding: int = 12) -> str:
    row = math.ceil(bound.height() / resolution)
    col = math.ceil(bound.width() / resolution)
    innerWidth = col * gridSize
    innerHeight = row * gridSize
    width = innerWidth + padding * 2
    height = innerHeight + padding * 2

    result = getPartHead(width, height)
    result += getPartFrame(row, col, gridSize, padding)
    result += getPartPoints(pointList, bound, showElevation, width, height, padding)
    result += "</svg>"
    return result

def drawGrayLevelGrids(gridList: [Grid], gridSize: int = 36, padding: int = 12) -> str:
    col = 0
    row = 0
    for grid in gridList:
        col = grid.col if grid.col > col else col
        row = grid.row if grid.row > row else row
    highest = False
    lowest = False
    for grid in gridList:
        if grid.elevation:
            highest = grid.elevation
            lowest = highest
            break
    for grid in gridList:
        if grid.elevation:
            highest = grid.elevation if highest < grid.elevation else highest
            lowest = grid.elevation if lowest > grid.elevation else lowest
    dElevation = highest - lowest

    result = getPartHead(padding * 2 + (col + 1) * gridSize, padding * 2 + (row + 1) * gridSize)

    for grid in gridList:
        result += ("<rect x=\"{x}\" y=\"{y}\" ".format(
                x = padding + grid.col * gridSize,
                y = padding + (row - grid.row) * gridSize
            ) +
            "width=\"{width}\" height=\"{height}\" ".format(
                width = gridSize, height = gridSize
            ) +
            "style=\"fill:rgb({r}, {g}, {b}); stroke:rgb({r}, {g}, {b})".format(
                r = int(255 * ((grid.elevation - lowest) / dElevation)) if grid.elevation else 255,
                g = int(255 * ((grid.elevation - lowest) / dElevation)) if grid.elevation else 0,
                b = int(255 * ((grid.elevation - lowest) / dElevation)) if grid.elevation else 0
            ) +
            "stroke-width:0;\"/>\n"
        )


    result += "</svg>"
    return result

def getPartHead(width: int, height: int) -> str:
    return ("<?xml version=\"1.0\" standalone=\"no\"?>\n" +
        "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" " +
        "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n" +
        "<svg width=\"{width}px\" height=\"{height}px\" version=\"1.1\" ".format(
            width = width, height = height
        ) +
        "xmlns=\"http://www.w3.org/2000/svg\">\n"
    )

def getPartFrame(row: int, col: int, gridSize: int, padding: int) -> str:
    # Draw Frame if padding > 0
    result = ""
    if padding > 0:
        result += ("<rect x=\"{x}\" y=\"{y}\" ".format(
                x = padding, y = padding
            ) +
            "width=\"{width}\" height=\"{height}\" ".format(
                width = col * gridSize, height = row * gridSize
            ) +
            "style=\"fill:none; stroke-width:1; stroke:#AAA\"/>\n"
        )
    currentCol = 1
    while currentCol < col:
        result += ("<line x1=\"{x1}\" y1=\"{y1}\" ".format(
                x1 = currentCol * gridSize + padding, y1 = padding
            ) +
            "x2=\"{x2}\" y2=\"{y2}\" ".format(
                x2 = currentCol * gridSize + padding, y2 = row * gridSize + padding
            ) +
            "style=\"stroke-width:1; stroke:#CCC\"/>\n"
        )
        currentCol += 1
    currentRow = 1
    while currentRow < row:
        result += ("<line x1=\"{x1}\" y1=\"{y1}\" ".format(
                x1 = padding , y1 = currentRow * gridSize + padding
            ) +
            "x2=\"{x2}\" y2=\"{y2}\" ".format(
                x2 = col * gridSize + padding, y2 = currentRow * gridSize + padding
            ) +
            "style=\"stroke-width:1; stroke:#CCC\"/>\n"
        )
        currentRow += 1
    return result

def getPartPoints(pointList: [Point], bound: Bound, showElevation: bool, width: int, height: int, padding: int) -> str:
    result = ""
    for point in pointList:
        centerX = padding + (point.x - bound.southWest.x) / bound.width() * (width - padding * 2)
        centerY = padding + (1.0 - (point.y - bound.southWest.y) / bound.height()) * (height - padding * 2)
        result += ("<circle cx=\"{cx}\" cy=\"{cy}\" ".format(
                cx = centerX, cy = centerY
            ) +
            "r=\"2\" stroke=\"black\" stroke-width=\"0\" fill=\"black\"/>\n"
        )
        result += ("<text x=\"{x}\" y=\"{y}\" ".format(
                x = centerX + 4.0, y = centerY + 2.0
            ) +
            "font-size=\"10\">{text:g}</text>\n".format(text = point.elevation if showElevation and point.elevation else point.index)
        )
    return result

# Display 3D with Matplotlib
#   Reference: https://matplotlib.org/examples/mplot3d/surface3d_demo.html
#   Reference: https://stackoverflow.com/questions/36668771/
#   Reference: https://blog.csdn.net/baoli1008/article/details/50531684
def display3D(gridList: [Grid]):
    # Get the size
    sizeX = 0
    sizeY = 0
    for grid in gridList:
        sizeX = grid.col if grid.col > sizeX else sizeX
        sizeY = grid.row if grid.row > sizeY else sizeY
    sizeX += 1
    sizeY += 1
    X = numpy.arange(sizeX * sizeY).reshape(sizeX, sizeY)
    Y = numpy.arange(sizeX * sizeY).reshape(sizeX, sizeY)
    Z = numpy.arange(sizeX * sizeY).reshape(sizeX, sizeY)
    for grid in gridList:
        X[grid.col, grid.row] = grid.x
        Y[grid.col, grid.row] = grid.y
        Z[grid.col, grid.row] = grid.elevation if grid.elevation else 0

    figure = plot.figure()
    axes = Axes3D(figure)
    axes.plot_surface(X, Y, Z, cmap = plot.get_cmap('rainbow'))
    plot.xlabel("x")
    plot.ylabel("y")
    plot.show()

if __name__ == '__main__':
    print("ERROR: Pleas run main.py instead of the module.")
