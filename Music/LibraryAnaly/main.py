#!/usr/bin/env python3
# coding: utf-8

"""
LibraryAnaly for iTunes
Author:     Lucka
Version:    0.2.0
Licence:    MIT
"""

# 命令行參數說明
# 終端顯示效果
#   Refrence: https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
optionsHelp = """可使用的命令行參數：
    \033[1m-a --add\033[0m                  掃描新的 iTunes 音樂庫 XML 文件並保存數據
    \033[1m-r --report  <filename>\033[0m   生成指定音樂庫記錄的報告
    \033[1m-c --compare <filename>\033[0m   比較當前音樂庫和過去指定音樂庫記錄並生成報告
    \033[1m-h --help\033[0m                 顯示本幫助文本
"""

# 庫
from datetime import datetime   # 處理日期
from datetime import timedelta  # 累計時間
import os                       # 建立文件夾、获取终端窗口尺寸
import pickle                   # 將對象存入文件
import sys, getopt              # 讀取命令行參數

# 類
class Music:
    def __init__(self,
                 trackID,
                 totalTime,
                 discNumber, trackNumber,
                 year, dateAdded,
                 playCount,
                 name, artist, album, genre,
                 location):
        """
        初始化 Music 類
        參數/成員變量列表:
            trackID     int         唯一序列號
            totalTime   timedelta   歌曲時長
            discNumber  int         光盤序號
            trackNumber int         音軌序號
            year        int         歌曲年份
            dateAdded   datetime    加入音樂庫的時間
            playCount   int         播放次數
            name        str         歌曲標題
            artist      str         藝術家
            album       str         專輯名稱
            genre       str         音樂類型
            location    str         音頻文件路徑
        """
        self.trackID = trackID
        self.totalTime = totalTime
        self.discNumber = discNumber
        self.trackNumber = trackNumber
        self.year = year
        self.dateAdded = dateAdded
        self.playCount = playCount
        self.name = name
        self.artist = artist
        self.album = album
        self.genre = genre
        self.location = location

class Album:
    def __init__(self,
                 albumID, totalTime, name, trackCount, dateAdded, playCount):
        """
        初始化 Album 類
        參數/成員變量列表:
            albumID     int         唯一序列號
            totalTime   timedelta   專輯總時長
            name        str         專輯
            trackCount  int         音軌數量
            dateAdded   datetime    加入音樂庫的時間
            playCount   int         總播放次數
        """
        self.albumID = albumID
        self.totalTime = totalTime
        self.name = name
        self.trackCount = trackCount
        self.dateAdded = dateAdded
        self.playCount = playCount

class MusicLibrary:
    def __init__(self, musicList, albumList, date):
        """
        初始化 MusicLibrary 類
        參數/成員變量列表:
            musicList   [Music]     音樂列表
            albumList   [Album]     專輯列表
            date        datetime    音樂庫修改時間
        """
        self.version = "0.2.0"
        self.musicList = musicList
        self.albumList = albumList
        self.date = date

    def getDateStr(self):
        return ("{year:0>4}-{month:0>2}-{day:0>2}"
                .format(year = self.date.year,
                        month = self.date.month,
                        day = self.date.day))


# 函数
def getLibrary(filename):
    """
    讀取 iTunes 音樂庫 XML 文件
    參數列表:
        filename    str 文件名
    返回:
        MusicLibrary    音樂庫類
    """
    try:
        libraryFile = open(filename, "r")
    except Exception as error:
        print("ERROR: {error}".format(error = error))
        exit()

    # 時間字符串格式
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"

    # 讀取音樂庫修改時間並拋棄頭部
    libraryLine = libraryFile.readline()
    while "<key>Date</key>" not in libraryLine:
        libraryLine = libraryFile.readline()
    libraryLine = libraryLine.replace("\t<key>Date</key><date>", "")
    libraryLine = libraryLine.replace("</date>\n", "")
    libraryDate = datetime.strptime(libraryLine, dateFormat)
    while "<key>Tracks</key>" not in libraryLine:
        libraryLine = libraryFile.readline()
    print("開始掃描 {filename}".format(filename = libraryFile.name))
    libraryFile.readline()

    # 讀取
    """
    一個歌曲信息示例
    <key>1152</key>
    <dict>
        <key>Track ID</key><integer>1152</integer>
        ...
        <key>Total Time</key><integer>188995</integer>
        <key>Disc Number</key><integer>1</integer>
        <key>Track Number</key><integer>5</integer>
        <key>Year</key><integer>1999</integer>
        ...
        <key>Date Added</key><date>2013-06-13T14:51:02Z</date>
        ...
        <key>Play Count</key><integer>96</integer>
        ...
        <key>Name</key><string>The Imperial March</string>
        <key>Artist</key><string>John Williams</string>
        ...
        <key>Album</key><string>John Williams Conducts Music from the Star Wars Saga</string>
        <key>Genre</key><string>Soundtrack</string>
        ...
        <key>Location</key><string>file:///Media/Music/English/John%20Williams%20Conducts%20Music%20from%20the%20Star%20Wars%20Saga/05.%20The%20Imperial%20March.mp3</string>
        ...
    </dict>
    """

    # 音樂列表
    musicList = []
    # 專輯列表
    albumList = []

    libraryLine = libraryFile.readline()
    while "<key>Playlists</key>" not in libraryLine:
        trackID = 0
        totalTime = zeroTime
        discNumber = 0
        trackNumber = 0
        year = 0
        dateAdded = zeroTime
        playCount = 0
        name = ""
        artist = ""
        album = ""
        genre = ""
        while "</dict>" not in libraryLine:
            if "<key>Track ID</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Track ID</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                trackID = int(libraryLine)
            if "<key>Total Time</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Total Time</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                totalTime = datetime.fromtimestamp(int(libraryLine) / 1000) - zeroTime
            if "<key>Disc Number</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Disc Number</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                discNumber = int(libraryLine)
            if "<key>Track Number</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Track Number</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                trackNumber = int(libraryLine)
            if "<key>Year</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Year</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                year = int(libraryLine)
            if "<key>Date Added</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Date Added</key><date>", "")
                libraryLine = libraryLine.replace("</date>\n", "")
                dateAdded = datetime.strptime(libraryLine, dateFormat)
            if "<key>Play Count</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Play Count</key><integer>", "")
                libraryLine = libraryLine.replace("</integer>\n", "")
                playCount = int(libraryLine)
            if "<key>Name</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Name</key><string>", "")
                libraryLine = libraryLine.replace("</string>\n", "")
                name = libraryLine
            if "<key>Artist</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Artist</key><string>", "")
                libraryLine = libraryLine.replace("</string>\n", "")
                artist = libraryLine
            if "<key>Album</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Album</key><string>", "")
                libraryLine = libraryLine.replace("</string>\n", "")
                album = libraryLine
            if "<key>Genre</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Genre</key><string>", "")
                libraryLine = libraryLine.replace("</string>\n", "")
                genre = libraryLine
            if "<key>Location</key>" in libraryLine:
                libraryLine = libraryLine.replace("\t\t\t<key>Location</key><string>", "")
                libraryLine = libraryLine.replace("</string>\n", "")
                libraryLine = libraryLine.replace("%20", " ")
                location = libraryLine
            libraryLine = libraryFile.readline()
            libraryLine = libraryLine.replace("&#38;", "&")

        # 拋棄有聲書和最後一行
        if genre != "Books" and trackID != 0:
            # 加入歌曲列表
            newMusic = Music(trackID, totalTime,
                             discNumber, trackNumber,
                             year, dateAdded,
                             playCount,
                             name, artist, album, genre,
                             location)
            musicList.append(newMusic)
            # 更新專輯列表
            isAlbumExist = False
            for scanner in range(0, len(albumList)):
                if albumList[scanner].name == newMusic.album:
                    albumList[scanner].totalTime += newMusic.totalTime
                    albumList[scanner].trackCount += 1
                    albumList[scanner].playCount += newMusic.playCount
                    albumList[scanner].dateAdded = newMusic.dateAdded
                    isAlbumExist = True
                    break
            if not isAlbumExist:
                newAlbum = Album(trackID, totalTime, album, 1, dateAdded, playCount)
                albumList.append(newAlbum)
        libraryLine = libraryFile.readline()

    print("掃描完成，共掃描{musicCount}首歌曲，{albumCount}張專輯。\n"
          .format(musicCount = len(musicList), albumCount = len(albumList)))
    libraryFile.close()

    library = MusicLibrary(musicList, albumList, libraryDate)
    return library

def addLibrary():
    """
    掃描 iTunes 音樂庫 XML 文件並保存 MusicLibrary 對象到文件中
    """
    library = getLibrary("iTunes Music Library.xml")
    libraryFilename = ("./Library/{date}.data"
                       .format(date = library.getDateStr()))
    libraryFile = open(libraryFilename, "wb")
    pickle.dump(library, libraryFile)
    libraryFile.close()
    print("已生成文件：{filename}\n".format(filename = libraryFilename))
    getReport(library)

def getReport(library):
    """
    輸出音樂庫的報告，包括文件。
    參數列表:
        library MusicLibrary    要輸出報告的音樂庫
    """
    # 時間字符串格式
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"

    # 總時長
    totalTime = zeroTime - zeroTime
    for music in library.musicList:
        totalTime += music.totalTime
    # 總播放次數和時長
    totalPlayCount = 0
    totalPlayTime = zeroTime - zeroTime
    for music in library.musicList:
        totalPlayCount += music.playCount
        totalPlayTime += music.totalTime * music.playCount
    # 按播放次數排序
    # 用 lambda 函數進行排序
    #   Refrence: https://docs.python.org/3/howto/sorting.html
    musicListByPlayCount = sorted(library.musicList,
                                  key = lambda music: music.playCount,
                                  reverse = True)
    albumListByPlayCount = sorted(library.albumList,
                                  key = lambda album: album.playCount,
                                  reverse = True)
    # 按播放時長排序
    musicListByPlayTime = sorted(library.musicList,
                                 key = lambda music: music.playCount * music.totalTime,
                                 reverse = True)
    albumListByPlayTime = sorted(library.albumList,
                                 key = lambda album: album.playCount * album.totalTime,
                                 reverse = True)
    # 報告文本
    # 開頭
    reportText = ("音樂庫報告\n" + splitLine() + '\n' +
                  "音乐库日期：{date}\n".format(date = library.getDateStr()) +
                  "共{musicCount}首音樂，{albumCount}張專輯，全部播放一遍要{totalTime:.0f}小時。\n"
                  .format(musicCount = len(library.musicList),
                          albumCount = len(library.albumList),
                          totalTime = getHours(totalTime)) +
                  "總共播放了{totalPlayCount}遍，共計{totalPlayTime:.0f}小時。\n"
                  .format(totalPlayCount = totalPlayCount,
                          totalPlayTime = getHours(totalPlayTime)) +
                  splitLine() + '\n')
    # 播放次數 TOP 10
    # 歌曲排行
    reportText += ("播放次數 TOP 10\n" + splitLine('-') + '\n' +
                   "歌曲排行\n" + "排名\t播放次數\t標題\n")
    for scanner in range(0, 10):
        reportText += ("#{num:0>2}\t{playCount:0>4}\t{name}\n"
                       .format(num = scanner + 1,
                               playCount = musicListByPlayCount[scanner].playCount,
                               name = musicListByPlayCount[scanner].name))
    # 專輯排行
    reportText += (splitLine('-') + '\n' +
                   "專輯排行\n" + "排名\t播放次數\t標題\n")
    for scanner in range(0, 10):
        reportText += ("#{num:0>2}\t{playCount:0>4}\t{name}\n"
              .format(num = scanner + 1,
                      playCount = albumListByPlayCount[scanner].playCount,
                      name = albumListByPlayCount[scanner].name))
    reportText += splitLine() + '\n'
    # 播放時長 TOP 10
    # 歌曲排行
    reportText += ("播放時長 TOP 10\n" + splitLine('-') + '\n' +
                   "歌曲排行\n" + "排名\t播放小時數\t標題\n")
    for scanner in range(0, 10):
        playHours = getHours(musicListByPlayTime[scanner].playCount *
                             musicListByPlayTime[scanner].totalTime)
        reportText += ("#{num:0>2}\t{playHours:0>4.0f}\t{name}\n"
                       .format(num = scanner + 1,
                               playHours = playHours,
                               name = musicListByPlayTime[scanner].name))
    # 專輯排行
    reportText += (splitLine('-') + '\n' +
                   "專輯排行\n" + "排名\t播放小時數\t標題\n")
    for scanner in range(0, 10):
        playHours = getHours(albumListByPlayTime[scanner].playCount *
                             albumListByPlayTime[scanner].totalTime)
        reportText += ("#{num:0>2}\t{playHours:0>5.0f}\t{name}\n"
              .format(num = scanner + 1,
                      playHours = playHours,
                      name = albumListByPlayTime[scanner].name))
    reportText += splitLine() + '\n'
    print(reportText)
    # 報告文件
    reportFilename = ("{date} Report.txt".format(date = library.getDateStr()))
    reportFile = open(reportFilename, "w")
    reportFile.write(reportText)
    reportFile.close()
    print("已生成報告文件：{filename}".format(filename = reportFilename))

def compare(libraryA, libraryB):
    """
    對比兩個音樂庫紀錄，生成報告
    參數列表:
        libraryA    MusicLibrary    第一個音樂庫
        libraryB    MusicLibrary    第二個音樂庫
    """
    # 確定 libraryA 比 libraryB 更新
    if libraryA.date < libraryB.date:
        temp = libraryA
        libraryA = libraryB
        libraryB = temp
    # 時間差
    timeInterval = libraryA.date - libraryB.date
    # 期間播放次數和期間播放時間
    totalPlayCount = 0
    totalPlayTime = zeroTime - zeroTime

    # 新增的歌曲
    newMusicList = []
    for scanner in libraryA.musicList:
        if scanner.dateAdded > libraryB.date:
            newMusicList.append(scanner)
            totalPlayCount += scanner.playCount
            totalPlayTime += scanner.totalTime * scanner.playCount
    # 新增的專輯
    newAlbumList = []
    for scanner in libraryA.albumList:
        if scanner.dateAdded > libraryB.date:
            newAlbumList.append(scanner)
    # 發生變化的歌曲列表
    # trackID 可能會全部發生整數偏差，首先確定偏差
    print("正在檢測偏差…")
    deviation = 0
    for musicB in libraryB.musicList:
        if (libraryA.musicList[0].name == musicB.name and
            libraryA.musicList[0].album == musicB.album):
            deviation = libraryA.musicList[0].trackID - musicB.trackID
            print("匹配成功：{trackIDB} -> {trackIDA}，偏差為{deviation}"
                  .format(trackIDB = musicB.trackID,
                          trackIDA = libraryA.musicList[0].trackID,
                          deviation = deviation))
            break
    changedMusicList = []

    for musicA in libraryA.musicList:
        for musicB in libraryB.musicList:
            if musicA.trackID == musicB.trackID + deviation:
                if musicA.playCount > musicB.playCount:
                    changedMusic = musicA
                    changedMusic.playCount -= musicB.playCount
                    changedMusicList.append(changedMusic)
                    totalPlayTime += changedMusic.totalTime * changedMusic.playCount
                    totalPlayCount += changedMusic.playCount
                break
    # 發生變化的專輯列表
    # albumID 與專輯第一首歌 trackID 一致，因此存在同樣的偏差
    changedAlbumList = []
    for albumA in libraryA.albumList:
        for albumB in libraryB.albumList:
            if albumA.albumID == albumB.albumID + deviation:
                if albumA.playCount > albumB.playCount:
                    changedAlbum = albumA
                    changedAlbum.playCount -= albumB.playCount
                    changedAlbumList.append(changedAlbum)
                break
    # 按播放次數排序
    # 歌曲排行
    musicListByPlayCount = sorted(changedMusicList,
                                  key = lambda music: music.playCount,
                                  reverse = True)
    # 專輯排行
    albumListByPlayCount = sorted(changedAlbumList,
                                  key = lambda album: album.playCount,
                                  reverse = True)
    # 報告文本
    # 開頭
    reportText = ("音樂庫對比報告\n" + splitLine() + '\n' +
                  "音乐库日期：{start} -> {end}，共{interval}天。\n"
                  .format(start = libraryB.getDateStr(),
                          end = libraryA.getDateStr(),
                          interval = timeInterval.days))
    reportText += ("共新增{musicAdded}首音樂，{albumAdded}張專輯。\n"
                   .format(musicAdded = len(newMusicList),
                           albumAdded = len(newAlbumList)))
    reportText += ("聽了來自{albumPlayed}張專輯的{musicPlayed}首音樂，共聽了{playCount}次，{totalPlayTime:.0f}小時。\n"
                   .format(albumPlayed = len(changedAlbumList),
                           musicPlayed = len(changedMusicList),
                           playCount = totalPlayCount,
                           totalPlayTime = getHours(totalPlayTime)) +
                   splitLine() + '\n')
    reportText += ("播放次數 TOP 10\n" + splitLine('-') + '\n' +
                   "歌曲排行\n" + "排名\t播放次數\t標題\n")
    for scanner in range(0, 10):
        reportText += ("#{num:0>2}\t{playCount:0>4}\t{name}\n"
                       .format(num = scanner + 1,
                               playCount = musicListByPlayCount[scanner].playCount,
                               name = musicListByPlayCount[scanner].name))
    reportText += splitLine('-') + '\n' + "專輯排行\n" + "排名\t播放次數\t標題\n"
    for scanner in range(0, 10):
        reportText += ("#{num:0>2}\t{playCount:0>4}\t{name}\n"
              .format(num = scanner + 1,
                      playCount = albumListByPlayCount[scanner].playCount,
                      name = albumListByPlayCount[scanner].name))
    reportText += splitLine() + '\n'
    print(reportText)
    # 報告文件
    reportFilename = ("{dateA} vs {dateB} Report.txt"
                      .format(dateA = libraryA.getDateStr(),
                              dateB = libraryB.getDateStr()))
    reportFile = open(reportFilename, "w")
    reportFile.write(reportText)
    reportFile.close()
    print("已生成報告文件：{filename}".format(filename = reportFilename))

def splitLine(char = '=', length = 0):
    """
    生成分割線
    參數列表:
        [char]      str 分割線的字符串，默認為 "="
        [length]    int 分割線長度，若不填或為0則生成與終端寬度相同的分割線
    返回:
        str         分割線字符串
    """
    if length == 0:
        length = os.get_terminal_size().columns
    result = ""
    for i in range(0, length):
        result += char
    return result

def getHours(timeInterval):
    """
    獲取 timedelta 的小時數
    參數列表:
        timeInterval    timedelta
    返回:
        double          浮點小時數
    """
    return timeInterval.days * 24 + timeInterval.seconds / 3600

def main():
    # 检查并创建 Library 文件夹
    if not os.path.exists("./Library"):
        os.mkdir("./Library")

    # 處理命令行參數
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "har:c:",
                                   ["help",
                                    "add",
                                    "report=",
                                    "compare="])
    except getopt.GetoptError as error:
        print("Error: {error}".format(error = error))
        print(optionsHelp)
        exit()

    print(__doc__)
    if len(opts) == 0:
        print("請在命令行中添加參數。")
        print(optionsHelp)
        exit()

    for opt, argv in opts:
        if opt in ("-h", "--help"):
            print(optionsHelp)
        elif opt in ("-a", "--add"):
            addLibrary()
        elif opt in ("-r", "--report"):
            libraryFilename = argv
            libraryFilename = "./Library/" + libraryFilename
            try:
                libraryFile = open(libraryFilename, "rb")
            except Exception as error:
                print("ERROR: {error}".format(error = error))
                exit()
            library = pickle.load(libraryFile)
            try:
                version = library.version
            except Exception as error:
                print("記錄文件 {filename} 數據版本過低，請運行數據更新工具"
                      .format(filename = libraryFilename))
                exit()
            if version != lastVersion:
                print("記錄文件 {filename} 數據版本過低，請運行數據更新工具"
                      .format(filename = libraryFilename))
                exit()
            getReport(library)
        elif opt in ("-c", "--compare"):
            libraryA = getLibrary("iTunes Music Library.xml")
            # 載入記錄
            libraryBFilename = argv
            libraryBFilename = "./Library/" + libraryBFilename
            try:
                libraryBFile = open(libraryBFilename, "rb")
            except Exception as error:
                print("ERROR: {error}".format(error = error))
                exit()
            libraryB = pickle.load(libraryBFile)
            try:
                version = libraryB.version
            except Exception as error:
                print("記錄文件 {filename} 數據版本過低，請運行數據更新工具"
                      .format(filename = libraryBFilename))
                exit()
            if version != lastVersion:
                print("記錄文件 {filename} 數據版本過低，請運行數據更新工具"
                      .format(filename = libraryBFilename))
                exit()
            compare(libraryA, libraryB)
        else:
            print("參數 {opt} 不可用。".format(opt))
            print(optionsHelp)

# 全局變量
# 最新數據版本
lastVersion = "0.2.0"
# 起點時間
zeroTime = datetime.fromtimestamp(0)
if __name__ == '__main__':
    main()
