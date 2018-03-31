#!/usr/bin/env python3
# coding: utf-8

"""
DEMKit for DEMBuilder
Author:     Lucka
Version:    0.1.0
License:    MIT
"""

import math

class Point:
    """
    class Points
    """
    def __init__(self, index: int = -1,
        x: float = -1.0, y: float = -1.0, elevation: float = 0):
        self.index = index
        self.x = x
        self.y = y
        self.elevation = elevation

    def loadFromRawData(self, rawDataLine: str):
        data = rawDataLine.replace(" ", "").split("\t")
        self.index = int(data[0])
        self.x = float(data[1])
        self.y = float(data[2])
        self.elevation = float(data[3])
        return self

    def copy(self):
        return Point(self.index, self.x, self.y, self.elevation)

    def distanceSquareTo(self, point) -> float:
        return (point.x - self.x) * (point.x - self.x) + (point.y - self.y) * (point.y - self.y)

    def distanceTo(self, point) -> float:
        return math.sqrt(self.distanceSquareTo(point))

    def searchCircleIncluds(self, point, searchCircleRadius: float) -> bool:
        return self.distanceSquareTo(point) <= searchCircleRadius * searchCircleRadius

class Grid(Point):
    """
    class Grid
    """
    def __init__(self, row: int, col: int,
        index: int = -1, x: float = -1.0, y: float = -1.0, elevation: float = 0,
        ):
        Point.__init__(self, index, x, y, elevation)
        self.row = row
        self.col = col


class Bound:
    """
    class Bound
        Bound of points
    """
    def __init__(self, pointList: [Point]):
        self.southWest = pointList[0].copy()
        self.northEast = pointList[0].copy()
        for point in pointList:
            self.southWest.x = point.x if point.x < self.southWest.x else self.southWest.x
            self.southWest.y = point.y if point.y < self.southWest.y else self.southWest.y
            self.northEast.x = point.x if point.x > self.northEast.x else self.northEast.x
            self.northEast.y = point.y if point.y > self.northEast.y else self.northEast.y

    def width(self) -> float:
        return self.northEast.x - self.southWest.x

    def height(self) -> float:
        return self.northEast.y - self.southWest.y

    def area(self) -> float:
        return self.width() * self.height()

# Functions

def loadData(filename: str):
    dataString = open(filename).read().splitlines()
    pointList = []
    for line in dataString:
        if line == "":
            continue
        point = Point().loadFromRawData(line)
        pointList.append(point)
    return pointList

def calculateDEM(pointList: [Point], resolution: float, minimum: int):
    bound = Bound(pointList)
    row = math.ceil(bound.height() / resolution)
    col = math.ceil(bound.width() / resolution)
    print("Build {row} rows, {col} cols.".format(row = row + 1, col = col + 1))
    searchCircleRadius = math.sqrt(5 * bound.area() / (len(pointList) * math.pi))
    print("Search Circle Radius: {r:.3}".format(r = searchCircleRadius))
    result = []
    currentX = bound.southWest.x
    colCount = 0
    while colCount <= col :
        currentY = bound.southWest.y
        rowCount = 0
        while rowCount <= row:
            pointCount = 0
            sumPower = 0.0
            sumElevation = 0.0
            newPoint = Grid(rowCount, colCount, -1, currentX, currentY)
            for point in pointList:
                if newPoint.searchCircleIncluds(point, searchCircleRadius):
                    p = 1.0 / newPoint.distanceSquareTo(point)
                    sumPower += p
                    sumElevation += p * point.elevation
                    pointCount += 1
            # Expand search circle if it has too less points
            newSCRadius = searchCircleRadius
            while pointCount <= minimum:
                newSCRadius = newSCRadius * 2
                for point in pointList:
                    if newPoint.searchCircleIncluds(point, newSCRadius):
                        p = 1.0 / newPoint.distanceSquareTo(point)
                        sumPower += p
                        sumElevation += p * point.elevation
                        pointCount += 1
            newPoint.elevation = sumElevation / sumPower if sumPower > 0 else False
            result.append(newPoint)
            currentY += resolution
            rowCount += 1
        currentX += resolution
        colCount += 1

    return result


if __name__ == '__main__':
    print("ERROR: Pleas don not run the module directly.")
