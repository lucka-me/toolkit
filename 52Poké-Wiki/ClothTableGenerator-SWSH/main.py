#!/usr/bin/env python3
# coding: utf-8

"""
神奇寶貝百科服飾列表生成器 for SWSH
Author:     Lucka
Version:    0.5.0
Licence:    MIT
"""

# 庫
import time
import os
import urllib.request
import re
from wand.image import Image

# 服飾類
class Cloth:
    def __init__(
        self,
        typeSN: int, colorSN: int,
        price: int,
        locationSN: int, location: str
    ):
        """
        初始化服飾類
        參數列表:
            typeSN:     服裝類型序列號
            colorSN:    顏色類型序列號
                        -1: 無顏色類型
            price:      價格
            locationSN: 購買城市序列號
                        -1: 無且不生成鏈接
            location:   購買商店或地點
        """
        self.typeSN = typeSN
        self.colorSN = colorSN
        self.price = price
        self.locationSN = locationSN
        self.location = location


def getFullyMatchedSN(target: str, array: list) -> int:
    """
    獲取列表中完整匹配目标的序列號
    參數列表:
        target: 目標
        array:  掃描的列表
    返回：
        列表中的序列號，如無匹配項則返回-1
    """
    for index in range(0, len(array)):
        if target == array[index]:
            return index
    return -1


def getPartlyMatchedSN(target: str, array: list) -> int:
    """
    獲取列表中部分匹配目标的序列號，倒序扫描
    參數列表:
        target: 目標
        array:  掃描的列表
    返回：
        列表中的序列號，如無匹配項則返回-1
    """
    for index in range(len(array) - 1, -1, -1):
        if array[index] in target:
            return index
    return -1


def getGenderStr() -> str:
    # 聲明全局變量
    global gender

    return "男生" if gender == 0 else "女生"


def getImgFilename(typeSN: int, colorSN: int, typeFallback: str = "") -> str:
    # 聲明全局變量
    global clothListZH

    return "SWSH {gender} {type}{color}.jpg".format(
        gender = getGenderStr(),
        type = typeFallback if typeSN == -1 else clothListZH[typeSN],
        color = "" if colorSN == -1 else " " + clothListZH[colorSN]
    )


def processImg(path: str, typeSN: int, colorSN: int):
    """
    獲取圖片並重命名和裁切
    參數列表:
        path:       Serebii.net 上的圖片路徑
        typeSN:     服裝類型序列號
                    -1: 未識別
        colorSN:    顏色類型序列號
                    -1: 無顏色類型
    """

    # 聲明全局變量
    global folder
    global gender
    global imgTop
    global imgLeft
    global imgWidth
    global imgHeight

    print("正在處理圖片…")

    # 生成圖片文件名
    filename = folder + getImgFilename(
        typeSN, colorSN,
        re.sub(r'/swordshield/custom/(fe)?maleclothing/', "", path)
    )

    # 檢查文件是否已存在
    if(os.path.exists(filename)):
        willProcessImg = input("圖片已存在，是否重新下載和處理 (Y/N): ")
        willProcessImg = willProcessImg.upper()
        while willProcessImg != "Y" and willProcessImg != "N":
            print("警告: 輸入錯誤")
            willProcessImg = input("是否重新下載和處理 (Y/N): ")
            willProcessImg = willProcessImg.upper()
        if willProcessImg == "N":
            return

    # 生成圖片 URL
    url = "https://serebii.net{path}".format(path = path)

    # 獲取圖片
    print("正在下載: {0}".format(url))
    try:
        urllib.request.urlretrieve(url, filename)
        print("下載完成: {0}".format(filename))
    except Exception as error:
        print("錯誤: {error}".format(error = error))
        return

    try:
        with Image(filename = filename) as image:
            cropX = int((image.width - imgWidth) / 2) if imgLeft == -1 else imgLeft
            image.crop(cropX, imgTop, width = imgWidth, height = imgHeight)
            image.save(filename = filename)
            print("圖片處理完成。")
    except Exception as error:
        print("錯誤: {error}".format(error = error))
        return

def getColumn(rowspan: int, cloth: Cloth):
    """
    獲取 Wiki 各式的表格行代碼
    參數列表:
        rowspan:    合併的行數量
                    0:  本行被合併
                    1:  不合併
        cloth:      服裝
    返回:
        str Wiki 格式的表格行代碼
    """
    # 聲明全局變量
    global gender
    global imgWidth
    global clothListZH
    global clothListJA
    global clothListEN
    global clothListZHConvert
    global locationListZH

    # 圖樣列和顏色列不會被合併
    # 圖樣列
    rowImg: str = "[[File:{filename}|100px]]".format(
        filename = getImgFilename(cloth.typeSN, cloth.colorSN)
    )

    # 颜色列
    rowColor = "-" if cloth.colorSN == -1 else clothListZHConvert[cloth.colorSN]

    # 如果被合併，僅輸出以上內容
    if rowspan == 0:
        return "|-\n| {rowImg}\n| {rowColor}\n\n".format(
            rowImg = rowImg, rowColor = rowColor
        )

    # 名稱列
    rowName = "{textCH}<br/><small>{textJP}</small><br/><small>{textEN}</small>".format(
        textCH = clothListZHConvert[cloth.typeSN],
        textJP = clothListJA[cloth.typeSN],
        textEN = clothListEN[cloth.typeSN]
    )

    # 價格列
    rowPrice = "-" if cloth.price == 0 else "{{{{$}}}}{0:,}".format(cloth.price)

    # 購入地點列
    rowLocation = cloth.location if cloth.locationSN == -1 else "[[{town}]]<br/>[[{town}#{location}|{location}]]".format(
        town = locationListZH[cloth.locationSN], location = cloth.location
    )

    # 生成代碼
    result = "|-\n| {rowspanStyle}{rowName}\n| {rowImg}\n| {rowColor}\n| {rowspanStyle}{rowPrice}\n| {rowspanStyle}{rowLocation}\n\n".format(
        rowspanStyle = "" if rowspan < 2 else "rowspan = {rowspan} | ".format(rowspan = rowspan),
        rowName = rowName,
        rowImg = rowImg,
        rowColor = rowColor,
        rowPrice = rowPrice,
        rowLocation = rowLocation
    )

    return result


def main():
    # 主程序
    print(__doc__)

    # 聲明全局變量
    global folder
    global gender
    global imgTop
    global imgLeft
    global imgWidth
    global imgHeight
    global clothListZH
    global clothListJA
    global clothListEN
    global clothListZHConvert
    global locationListZH

    # 设置基本参数
    print("請输入基本參數:")
    folder = input("文件夹: ")
    if (len(folder) > 0):
        folder = folder + "/"
    willGetImg = input("是否需要下載圖片 (Y/N): ")
    willGetImg = willGetImg.upper()
    while willGetImg != "Y" and willGetImg != "N":
        print("警告: 輸入錯誤")
        willGetImg = input("是否需要下載圖片 (Y/N): ")
        willGetImg = willGetImg.upper()
    if willGetImg == "Y":
        willGetImg = True
    else:
        willGetImg = False

    print("初始化完畢，開始處理。")

    # 設置計時器
    startTime = time.time()

    # 讀取譯名列表
    print("正在讀取文本文件⋯")
    clothListZH = open('cloth_zh.txt').read().splitlines()
    clothListJA = open('cloth_ja.txt').read().splitlines()
    clothListEN = open('cloth_en.txt').read().splitlines()
    clothListZHConvert = open('cloth_zh_convert.txt').read().splitlines()
    locationListZH = open('location_zh.txt').read().splitlines()
    locationListEN = open('location_en.txt').read().splitlines()
    print("讀取完畢。")

    # 處理原文件
    print("正在處理 HTML 文件⋯")
    htmlFile = open(folder + "source.html", "r")
    htmlLines: list = htmlFile.readlines()
    htmlFile.close()

    indexLine = 0
    headerLine = htmlLines[indexLine]

    # 檢測性別
    gender = 0 if "<h3><a name=\"m" in headerLine else 1

    # 檢測類型、圖片尺寸和裁切尺寸
    # 裁切圖片
    # 0 上衣:     300x96+(x)+50
    # 1 褲裙:     96x96+(x)+105
    # 2 襪子:     96x48+(x)+182
    #   女生:     96x96+(x)+134
    # 3 鞋子:     96x48+(x)+182
    # 4 包包:     96x96+(x)+50
    # 5 帽子:   300x300+(x)+0
    # 6 眼鏡:     64x64+(x)+8
    # 7 髮飾:     64x64+(x)+8
    catalogType = ""
    imgLeft = 100
    imgWidth = 300
    imgHeight = 400
    if "</a>Hat</h3></p>" in headerLine:
        catalogType = "帽子"
        imgTop = 0
        imgHeight = 300
    elif "</a>Glasses</h3></p>" in headerLine:
        catalogType = "眼镜"
        imgTop = 30 if gender == 0 else 70
        imgLeft = 156 if gender == 0 else 150
        imgWidth = 200
        imgHeight = 200
    elif "</a>Tops</h3></p>" in headerLine:
        catalogType = "上衣"
        imgTop = 130 if gender == 0 else 160
    elif "</a>Jackets</h3></p>" in headerLine:
        catalogType = "外套"
        imgTop = 130 if gender == 0 else 160
    elif "</a>Dress</h3></p>" in headerLine:
        if gender == 0:
            print("錯誤：檢測到男生-連身裝，請檢查輸入文本。")
            exit()
        catalogType = "连身装"
        imgTop = 200
    elif "</a>Bag</h3></p>" in headerLine:
        catalogType = "包包"
        imgTop = 150 if gender == 0 else 180
        imgLeft = 20 if gender == 0 else 70
    elif "</a>Gloves</h3></p>" in headerLine:
        catalogType = "手套"
        imgTop = 370 if gender == 0 else 380
        imgHeight = 200
    elif "</a>Bottoms</h3></p>" in headerLine:
        catalogType = "下装"
        imgTop = 400
    elif "</a>Legwear</h3></p>" in headerLine:
        catalogType = "袜子"
        imgTop = 400
    elif "</a>Shoes</h3></p>" in headerLine:
        catalogType = "鞋子"
        imgTop = 649
        imgLeft = -1 if gender == 0 else 100
        imgHeight = 200
    else:
        print("錯誤: 類型檢測失敗")
        exit()
    print("識別為{gender}的{catalogType}".format(gender = getGenderStr(), catalogType = catalogType))

    # 跳過<table>及表頭
    indexLine += 9

    # 跳過表頭
    countLines = len(htmlLines)
    indexRow = 0

    clothList = []
    priceSum = 0

    imgPath = ""
    typeSN = -1
    colorSN = -1
    location = ""
    locationSN = -1
    price = 0

    regexImgPath = re.compile(r'(/swordshield/custom/(fe)?maleclothing/.*\.jpg)" rel')
    regexCellText = re.compile(r'>(.*)<')

    if willGetImg:
        print("正在解析數據及下載圖片⋯")
    else:
        print("正在解析數據⋯")

    while indexLine < countLines:

        line = htmlLines[indexLine]
        if "</tr>" in line:

            if typeSN == -1:
                print("警告: 未成功處理此項目，請檢查。")
                if willGetImg:
                    print("但仍然下載並處理本圖片。")
                    processImg(imgPath, typeSN, colorSN)
            else:
                priceSum = priceSum + price
            if willGetImg:
                processImg(imgPath, typeSN, colorSN)
            newCloth = Cloth(typeSN, colorSN, price, locationSN, location)
            clothList.append(newCloth)
            print("")

            imgPath = ""
            typeSN = -1
            colorSN = -1
            location = ""
            locationSN = -1
            price = 0

            indexRow = 0
            indexLine += 1

            continue
    
        if indexRow == 0:
            imgPath = regexImgPath.search(line).group(1)
            print("圖片: {url}".format(url = imgPath))
        else:
            cellText = regexCellText.search(line).group(1)
            if indexRow == 1:
                cellText = cellText.replace("  ", " ")
                typeSN = getFullyMatchedSN(cellText, clothListEN)
                print("類型: {text} -> {type}".format(
                    text = cellText,
                    type = "未識別" if typeSN == -1 else clothListZH[typeSN])
                )
            elif indexRow == 2:
                colorSN = getFullyMatchedSN(cellText, clothListEN)
                print("顏色: {text} -> {color}".format(
                    text = cellText,
                    color = "無" if colorSN == -1 else clothListZH[colorSN])
                )
            elif indexRow == 3:
                locationSN = getPartlyMatchedSN(cellText, locationListEN)
                location = "时装店" if "Boutique" in cellText else cellText
                print("地點: {text} -> {town} {location}".format(
                    text = cellText,
                    town = locationListZH[locationSN],
                    location = location
                ))
            elif indexRow == 4:
                price = int(cellText) if cellText.isdigit() else 0
                print("價格: {price}".format(price = price))

        indexLine += 1
        indexRow += 1

    print("解析完畢")

    # 讀取列表並生成 Wiki 代碼
    cssColor = "Sh" if gender == 1 else "Sw"
    print("正在生成 Wiki 代碼⋯")
    wikiFile = open(folder + "wiki.txt", "w")

    wikiFile.write("""
=== {header} ===
{{| class = "a-l eplist roundy sortable bgd-{css} b-{css}"
|- class = "bg-{css}"
! class = "roundytl-6" | 名称
! class = "unsortable" | 图样
! 颜色／图案
! data-sort-type = "number" | 价格
! class = "roundytr-6" | 购入地点

""".format(header = catalogType, css = cssColor))

    scanner = 0
    while scanner < len(clothList):
        # 如果有同類型服飾則應當合併
        # 如果類型序列號、價格和購買城市序列號均一致則可判斷為同一類型並予以合併
        spanCount = 1
        print("{0}:\t".format(clothListZH[clothList[scanner].typeSN]), end = "")
        while (scanner + spanCount < len(clothList) and
               clothList[scanner].typeSN == clothList[scanner + spanCount].typeSN and
               clothList[scanner].price == clothList[scanner + spanCount].price and
               clothList[scanner].locationSN == clothList[scanner + spanCount].locationSN):
            spanCount += 1
        wikiColumn = getColumn(spanCount, clothList[scanner])
        wikiFile.write(wikiColumn)
        if spanCount > 1:
            print("合併{0}行".format(spanCount))
            for spanScanner in range(1, spanCount):
                wikiColumn = getColumn(0, clothList[scanner + spanScanner])
                wikiFile.write(wikiColumn)
        else:
            print("無須合併")
        scanner += spanCount

    wikiFile.write("""
|-
| class = \"bg-{css}\" colspan = 5 | \'\'\'共{count}款{category}\'\'\'<br/>\'\'\'<small>价值{{{{$}}}}{price:,}</small>\'\'\'

|}}

{{{{-}}}}
""".format(css = cssColor,
           count = len(clothList),
           category = catalogType,
           price = priceSum))
    wikiFile.close()
    if willGetImg:
        print("處理完畢，共處理{count}個服飾，已生成完整 wiki.txt 文件及圖片。".format(count = len(clothList)))
    else:
        print("處理完畢，共處理{count}個服飾，已生成完整 wiki.txt 文件。".format(count = len(clothList)))
    print("運行耗時: {interval:.2f}秒。".format(interval = time.time() - startTime))

if __name__ == '__main__':
    main()
