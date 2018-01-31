#!/usr/bin/env python3
# coding: utf-8

"""
神奇寶貝百科服飾列表生成器
Author:     Lucka
Version:    0.4.2
Licence:    MIT
"""

# 庫
import time
import urllib.request
from wand.image import Image

# 類
class Cloth:
    def __init__(self, typeSN, colorSN,
                 price,
                 locationSN, location,
                 version):
        """
        初始化 Cloth 類
        參數列表:
            typeSN:     int     服裝類型序列號
            colorSN:    int     顏色類型序列號
                                -1: 無顏色類型
            price:      int     價格
            locationSN: int     購買城市序列號
                                -1: 無且不生成鏈接
            location:   str     購買商店或地點
            version:    int     版本限定
                                0:  雙版本均有
                                1:  究極之日限定
                                2:  究極之月限定
        """
        self.typeSN = typeSN
        self.colorSN = colorSN
        self.price = price
        self.locationSN = locationSN
        self.location = location
        self.version = version

def getFullyMatchedSN(target, array):
    """
    獲取列表中完整匹配目标數值的序列號
    參數列表:
        target: int     目標數值
        array:  int     掃描的列表
    返回：
        int     列表中的序列號，如無匹配項則返回-1
    """
    for scanner in range(0, len(array)):
        if target == array[scanner]:
            return scanner
    return -1

def getPartlyMatchedSN(target, array):
    """
    獲取列表中部分匹配目标數值的序列號，倒序扫描
    參數列表:
        target: int     目標數值
        array:  int     掃描的列表
    返回：
        int     列表中的序列號，如無匹配項則返回-1
    """
    for scanner in range(len(array) - 1, -1, -1):
        if array[scanner] in target:
            return scanner
    return -1

def getImg(imgSN, typeSN, colorSN):
    """
    獲取圖片並重命名和裁切
    參數列表:
        imgSN:      int     Serebii.net 上的圖片編號
        typeSN:     int     服裝類型序列號
                            -1: 未識別
        colorSN:    int     顏色類型序列號
                            -1: 無顏色類型
    """

    # 聲明全局變量
    global sex
    global cropY
    global imgWidth
    global imgHeight
    global typeListCH

    print("正在處理圖片…")

    # 生成圖片 URL
    if sex == "M":
        url = ("https://serebii.net/ultrasunultramoon/clothing/male/{0}.png"
               .format(imgSN))
    else:
        url = ("https://serebii.net/ultrasunultramoon/clothing/female/{0}.png"
               .format(imgSN))

    # 生成圖片文件名
    if colorSN == -1:
        color = ""
    else:
        color = " {0}".format(colorListCH[colorSN])
    if typeSN == -1:
        # 未識別者直接以 imgSN 命名文件
        fileName = "USUM {0} {1}{2}.png".format("男生" if sex == "M" else "女生", imgSN, color)
    else:
        fileName = "USUM {0} {1}{2}.png".format("男生" if sex == "M" else "女生", typeListCH[typeSN], color)

    # 獲取圖片
    print("正在下載: {0}".format(url))
    try:
        urllib.request.urlretrieve(url, fileName)
        print("下載完成: {0}".format(fileName))
    except Exception as error:
        print("錯誤: {error}".format(error = error))

    try:
        with Image(filename = fileName) as image:
            cropX = int((image.width - imgWidth) / 2)
            image.crop(cropX, cropY, width = imgWidth, height = imgHeight)
            image.save(filename = fileName)
            print("圖片處理完成。")
    except Exception as error:
        print("錯誤: {error}".format(error = error))



def getColumn(rowspan, typeSN, colorSN,
              price,
              locationSN, location,
              version):
    """
    獲取 Wiki 各式的表格行代碼
    參數列表:
        rowspan:    int     合併的行數量
                            0:  本行被合併
                            1:  不合併
        typeSN:     int     服裝類型序列號
        colorSN:    int     顏色類型序列號
                            -1: 無顏色類型
        price:      int     價格
        locationSN: int     購買城市序列號
                            -1: 無且不生成鏈接
        location:   str     購買商店或地點
        version:    int     版本限定
                            0:  雙版本均有
                            1:  究極之日限定
                            2:  究極之月限定
    返回:
        String      Wiki 各式的表格行代碼
    """
    # 聲明全局變量
    global sex
    global imgWidth
    global typeListCH
    global typeListJP
    global typeListEN
    global locationListCH
    global colorListCH

    # 圖樣列和顏色列不會被合併
    # 圖樣列
    if colorSN == -1:
        color = ""
    else:
        color = " {0}".format(colorListCH[colorSN])
    imgRow = ("[[File:USUM {0} {1}{2}.png|{3}px]]"
              .format("男生" if sex == "M" else "女生", typeListCH[typeSN], color, imgWidth)
    )

    # 顏色列樣式
    colorRowStyle = ""
    if version == 1:
        colorRowStyle = "class = \"bgl-US\" | "
    elif version == 2:
        colorRowStyle = "class = \"bgl-UM\" | "

    # 颜色列
    if colorSN == -1:
        colorRow = "-"
    else:
        colorRow = "{0}".format(colorListCH[colorSN])

    # 如果被合併，僅輸出以上內容
    if rowspan == 0:
        result = ("|-\n| {0}\n| {1}{2}\n\n"
                  .format(imgRow, colorRowStyle, colorRow))
    else:
        # 名稱列
        nameRow = ("{0}<br/><small>{1}</small><br/><small>{2}</small>"
                   .format(typeListCH[typeSN],
                           typeListJP[typeSN],
                           typeListEN[typeSN]))

        # 價格列
        if price == 0:
            priceRow = "-"
        else:
            priceRow = "{{{{$}}}}{0:,}".format(price)

        # 購入地點列
        if locationSN == -1:
            locationRow = location
        else:
            locationRow = ("[[{0}]]<br/>[[{0}#{1}|{1}]]"
                           .format(locationListCH[locationSN], location))

        # 生成代碼
        if rowspan > 1:
            rowspanStyle = "rowspan = {0} |".format(rowspan)
            result = ("|-\n| {0}{1}\n| {2}\n| {3}{4}\n| {5}{6}\n| {7}{8}\n\n"
                      .format(rowspanStyle, nameRow,
                              imgRow,
                              colorRowStyle, colorRow,
                              rowspanStyle, priceRow,
                              rowspanStyle, locationRow))
        else:
            result = ("|-\n| {0}\n| {1}\n| {2}{3}\n| {4}\n| {5}\n\n"
                      .format(nameRow,
                              imgRow,
                              colorRowStyle, colorRow,
                              priceRow,
                              locationRow))
        # 修復常見的錯誤
        result = result.replace("Gracidea",
                                "[[好奥乐市]]<br/>[[购物广场]][[购物广场#葛拉西蒂亞|葛拉西蒂亞]]")
        result = result.replace("<br/>[[皮卡丘山谷#Win Pikachu Valley Quiz|Win Pikachu Valley Quiz]]",
                                "")
        result = result.replace("静市#Malie City Community Center|Malie City Community Center",
                                "居民中心")
        result = result.replace("Konikoni Jewelery Shop",
                                "[[可霓可市]]<br/>[[可霓可市#丽姿的宝石店|丽姿的宝石店]]")
        result = result.replace("From GAME FREAK Director after completing Alola Pokédex",
                                "[[慷待市]]<br/>[[慷待市#GAME FREAK办公室|GAME FREAK办公室]]<br/>完成[[阿罗拉图鉴]]后由游戏总监赠送")
        result = result.replace("Po Town Pokémon Center|Po Town Pokémon Center",
                                "宝可梦中心|宝可梦中心")
    return result


def main():
    # 主程序
    print(__doc__)

    # 聲明全局變量
    global sex
    global cropY
    global imgWidth
    global imgHeight
    global typeListCH
    global typeListJP
    global typeListEN
    global locationListCH
    global colorListCH

    # 设置基本参数
    print("請输入基本參數:")
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
    typeListCH = open('type_ch.txt').read().splitlines()
    typeListJP = open('type_jp.txt').read().splitlines()
    typeListEN = open('type_en.txt').read().splitlines()
    colorListCH = open('color_ch.txt').read().splitlines()
    colorListEN = open('color_en.txt').read().splitlines()
    locationListCH = open('location_ch.txt').read().splitlines()
    locationListEN = open('location_en.txt').read().splitlines()
    print("讀取完畢。")


    # 處理原文件
    print("正在處理 HTML 文件⋯")
    sourceFile = open("source.html", "r")
    sourceString = sourceFile.read()
    sourceFile.close()
    # 檢測性別
    sex = "M" if "clothing/male/" in sourceString else "F"
    versionCode = "US" if sex == "M" else "UM"
    # 檢測類型、圖片尺寸和裁切尺寸
    # 裁切圖片
    # 0 上衣:     96x96+(x)+50
    # 1 褲裙:     96x96+(x)+105
    # 2 襪子:     96x48+(x)+182
    # 3 鞋子:     96x48+(x)+182
    # 4 包包:     96x96+(x)+50
    # 5 帽子:     64x64+(x)+8
    # 6 眼鏡:     64x64+(x)+8
    # 7 髮飾:     64x64+(x)+8
    catalogType = ""
    if "<td class=\"fooinfo\">Shirt</td>" in sourceString:
        catalogType = "上衣"
        imgWidth = 96
        imgHeight = 96
        cropY = 50
    elif "<td class=\"fooinfo\">Trousers</td>" in sourceString:
        if sex == "M":
            catalogType = "裤子"
        else:
            catalogType = "裤子、裙子"
        imgWidth = 96
        imgHeight = 96
        cropY = 105
    elif "<td class=\"fooinfo\">Socks</td>" in sourceString:
        catalogType = "袜子"
        imgWidth = 96
        imgHeight = 48
        cropY = 182
    elif "<td class=\"fooinfo\">Shoes</td>" in sourceString:
        catalogType = "鞋子"
        imgWidth = 96
        imgHeight = 48
        cropY = 182
    elif "<td class=\"fooinfo\">Bag</td>" in sourceString:
        catalogType = "包包"
        imgWidth = 96
        imgHeight = 96
        cropY = 50
    elif "<td class=\"fooinfo\">Hat</td>" in sourceString:
        catalogType = "帽子"
        imgWidth = 64
        imgHeight = 64
        cropY = 8
    elif "<td class=\"fooinfo\">Glasses</td>" in sourceString:
        catalogType = "眼镜"
        imgWidth = 64
        imgHeight = 64
        cropY = 8
    elif "<td class=\"fooinfo\">Accessories</td>" in sourceString:
        if sex == "M":
            print("錯誤: 識別為男生但類型為髮飾。")
            exit()
        catalogType = "发饰"
        imgWidth = 64
        imgHeight = 64
        cropY = 8
    else:
        print("錯誤: 類型檢測失敗")
        exit()
    print("識別為{sex}的{catalogType}"
          .format(sex = "男生" if sex == "M" else "女生",
                  catalogType = catalogType))
    sourceString = sourceString.replace("<tr><td class=\"fooinfo\"><a href=\"clothing/male/", "\n")
    sourceString = sourceString.replace("<tr><td class=\"fooinfo\"><a href=\"clothing/female/", "\n")
    sourceString = sourceString.replace(".png\" rel=\"lightbox[ranger3]\" title=\"Clothing\"><img src=\"clothing/male/", "\n")
    sourceString = sourceString.replace(".png\" rel=\"lightbox[ranger3]\" title=\"Clothing\"><img src=\"clothing/female/", "\n")
    sourceString = sourceString.replace(".jpg\" border=\"0\" /></a></td><td class=\"fooinfo\">", "\n")
    sourceString = sourceString.replace("</td><td class=\"fooinfo\">", "\n")
    sourceString = sourceString.replace("</td></tr>", "\n")
    ## 處理原生錯誤
    sourceString = sourceString.replace("Grey", "Gray")
    sourceString = sourceString.replace("\nNavy\n", "\nNavy Blue\n")
    sourceString = sourceString.replace("Hau'oli", "Hau’oli")
    sourceString = sourceString.replace(" GI ", " Gi ")

    targetFile = open("list.txt", "w")
    targetFile.write(sourceString)
    targetFile.close()
    print("處理完畢，已生成 list.txt 文件。")


    # 讀取列表文件並生成列表及下載圖片
    if willGetImg:
        print("正在生成列表及下載圖片⋯")
    else:
        print("正在生成列表⋯")
    print("請注意，下列信息可能出現錯誤，本工具將在後續工作中進行修正，請以最終結果為準。")

    clothList = []
    listFile = open("list.txt", "r")
    # 錯誤列表
    errorList = []
    # 總價統計
    priceSum = 0

    while True:
        """
        list.txt 中一件服飾對應十行：

        ImgSN
        ImgSN       重複
        Type        服飾種類如Ｔ恤等
        Color
        Catalog     服飾類型如上衣、褲、裙等
        Price
        Location
        Version

        注意首位各有一空行
        """
        # 第1行若為空則退出循環
        line = listFile.readline()
        if len(line) == 0:
            break

        print("正在處理：")
        print("序號:\t\t{0}".format(len(clothList) + 1))
        line = listFile.readline()
        imgSN = int(line)
        print("圖片編號:\t{0}".format(imgSN))

        listFile.readline()

        line = listFile.readline()
        clothType = line.replace("\n", "")
        typeSN = getFullyMatchedSN(clothType, typeListEN)
        if typeSN == -1:
            print("警告: 未找到對應服飾，原文: {0}".format(clothType))
        else:
            print("服飾種類:\t{0} -> {1}".format(clothType, typeListCH[typeSN]))

        line = listFile.readline()
        color = line.replace("\n", "")
        if color == "":
            colorSN = -1
            print("顏色:\t\t無")
        else:
            colorSN = getFullyMatchedSN(color, colorListEN)
            print("顏色:\t\t{0} -> {1}".format(color, colorListCH[colorSN]))

        listFile.readline()

        line = listFile.readline()
        if line.replace("\n", "").isdigit():
            price = int(line)
        else:
            price = 0
        print("價格:\t\t{0:,}".format(price))

        line = listFile.readline()
        location = line.replace("\n", "")
        locationSN = getPartlyMatchedSN(location, locationListEN)
        print("獲得地點:\t{0} -> {1}"
              .format(location, locationListCH[locationSN]))
        if "Apparel Shop" in location:
            location = "时装店"

        line = listFile.readline()
        version = line.replace("\n", "")
        if version == "Both":
            version = 0
        elif version == "Ultra Sun":
            version = 1
        elif version == "Ultra Moon":
            version = 2
        print("版本限定:\t{0}".format(version))

        listFile.readline()

        # 加入列表並下載圖片
        # 若未成功識別種類則發出警告且不加入列表
        if typeSN == -1:
            if willGetImg:
                print("警告: 未成功處理第此項目，請檢查。\n但仍然下載並處理本圖片。")
                getImg(imgSN, typeSN, colorSN)
            else:
                print("警告: 未成功處理第此項目，請檢查。")
            errorList.append(len(clothList) + 1)
        else:
            priceSum = priceSum + price
            if willGetImg:
                getImg(imgSN, typeSN, colorSN)
            newCloth = Cloth(typeSN, colorSN, price, locationSN, location, version)
            clothList.append(newCloth)
        print("")

    listFile.close()
    print("處理完畢。\n")

    # 讀取列表並生成 Wiki 代碼
    print("正在生成 Wiki 代碼⋯")
    wikiFile = open("wiki.txt", "w")
    wikiTableHead = """=== {0} ===
{{| class = "a-l eplist roundy sortable bgd-{1} b-{1}"
|- class = "bg-{1}"
! class = "roundytl-6" rowspan = 4 | 名称
! class = "unsortable" rowspan = 4 | 图样
! 颜色／图案
! data-sort-type = "number" rowspan = 4 | 价格
! class = "roundytr-6" rowspan = 4 | 购入地点
|-
! class = "bgwhite" | 太阳／月亮均有
|-
! class = "bgl-US" | 仅究极之日
|-
! class = "unsortable bgl-UM" | 仅究极之月

""".format(catalogType, versionCode)
    wikiFile.write(wikiTableHead)

    scanner = 0
    while scanner < len(clothList):
        # 如果有同類型服飾則應當合併
        # 如果類型序列號、價格和購買城市序列號均一致則可判斷為同一類型並予以合併
        spanCount = 1
        print("{0}:\t".format(typeListCH[clothList[scanner].typeSN]), end = "")
        while (scanner + spanCount < len(clothList) and
               clothList[scanner].typeSN == clothList[scanner + spanCount].typeSN and
               clothList[scanner].price == clothList[scanner + spanCount].price and
               clothList[scanner].locationSN == clothList[scanner + spanCount].locationSN):
            spanCount += 1
        wikiColumn = getColumn(spanCount,
                               clothList[scanner].typeSN,
                               clothList[scanner].colorSN,
                               clothList[scanner].price,
                               clothList[scanner].locationSN,
                               clothList[scanner].location,
                               clothList[scanner].version)
        wikiFile.write(wikiColumn)
        if spanCount > 1:
            print("合併{0}行".format(spanCount))
            for spanScanner in range(1, spanCount):
                wikiColumn = getColumn(0,
                                       clothList[scanner + spanScanner].typeSN,
                                       clothList[scanner + spanScanner].colorSN,
                                       clothList[scanner + spanScanner].price,
                                       clothList[scanner + spanScanner].locationSN,
                                       clothList[scanner + spanScanner].location,
                                       clothList[scanner + spanScanner].version)
                wikiFile.write(wikiColumn)
        else:
            print("無須合併")
        scanner += spanCount

    wikiFile.write("""|-
| class = \"bg-{0}\" colspan = 5 | \'\'\'共{1}款{2}\'\'\'<br/>\'\'\'<small>价值{{{{$}}}}{3:,}</small>\'\'\'

|}}

{{{{-}}}}
""".format(versionCode,
           len(clothList) - len(errorList),
           catalogType,
           priceSum))
    wikiFile.close()
    if willGetImg:
        print("處理完畢，共處理{0}個服飾，已生成完整 wiki.txt 文件及圖片。".format(len(clothList)))
    else:
        print("處理完畢，共處理{0}個服飾，已生成完整 wiki.txt 文件。".format(len(clothList)))
    if len(errorList) > 0:
        print("未成功處理{0}個服飾，序號如下:".format(len(errorList)))
        for scanner in errorList:
            print("  {0}".format(scanner))
    print("運行耗時: {0:.2f}秒。".format(time.time() - startTime))

if __name__ == '__main__':
    main()
