#!/usr/bin/env python3
# coding: utf-8

"""
簡繁轉換代碼生成器
Author:     Lucka
Version:    0.1.0
Licence:    MIT
"""

def main():

    print(__doc__)

    print("開始處理。")

    # 讀取譯名列表
    print("正在讀取文本文件⋯")
    listSimp = open('zhs.txt').read().splitlines()
    listTrad = open('zht.txt').read().splitlines()
    listSimpToTrad = open('zhs_zht.txt').read().splitlines()
    listTradToSimp = open('zht_zhs.txt').read().splitlines()
    print("讀取完畢。")

    countLines = len(listSimp)
    if len(listTrad) != countLines:
        print("繁體詞彙數量不匹配")
        return
    if len(listSimpToTrad) != countLines:
        print("簡轉繁詞彙數量不匹配")
        return
    if len(listTradToSimp) != countLines:
        print("繁轉簡詞彙數量不匹配")
        return

    outputFile = open("output.txt", "w")

    for indexLine in range(countLines):
        textSimp = listSimp[indexLine]
        textTrad = listTrad[indexLine]
        textSimpToTrad = listSimpToTrad[indexLine]
        textTradToSimp = listTradToSimp[indexLine]

        if textSimp == textTrad:
            outputFile.write(textSimp)
        elif textSimpToTrad == textTrad:
            outputFile.write(textSimp)
        elif textSimp == textTradToSimp:
            outputFile.write(textTrad)
        else:
            outputFile.write("-{{zh-hans:{simp};zh-hant:{trad}}}-".format(
                simp = textSimp, trad = textTrad
            ))
        if indexLine < countLines - 1:
            outputFile.write("\n")

    outputFile.close()
    print("處理完畢。")

if __name__ == '__main__':
    main()
