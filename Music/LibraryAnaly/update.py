#!/usr/bin/env python3
# coding: utf-8

"""
LibraryAnaly for iTunes
Record Update Tool
Author:     Lucka
Version:    0.2.0
Licence:    MIT
"""

# 命令行參數說明
optionsHelp = """可使用的命令行參數：
    \033[1m-u --update  <filename>\033[0m   更新指定記錄的數據文件
    \033[1m-h --help\033[0m                 顯示本幫助文本
"""

# 庫
from datetime import datetime   # 處理日期
from datetime import timedelta  # 累計時間
import os                       # 建立文件夾、获取终端窗口尺寸
import pickle                   # 將對象存入文件
import sys, getopt              # 讀取命令行參數

# 舊的 Library 類
# Version 0.1.0
class Music:
    """
    class Music
    Version 0.1.0
    對應版本
        MusicAnaly  0.1.0   -   0.1.1
        Library     0.1.0
    成員變量
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

    Version 0.2.0
    對應版本
        MusicAnaly  0.2.0
        Library     0.2.0
    新增成員變量
        genre       str 音樂類型
        location    str 音頻文件路徑
    """
    def __init__(self,
                 trackID,
                 totalTime,
                 discNumber, trackNumber,
                 year, dateAdded,
                 playCount,
                 name, artist, album, genre,
                 location):
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
    """
    class Album
    Version 0.1.0
    對應版本
        MusicAnaly  0.1.0   -   0.1.1
        Library     0.1.0   -   0.2.0
    成員變量
        albumID     int         唯一序列號
        totalTime   timedelta   專輯總時長
        name        str         專輯
        trackCount  int         音軌數量
        dateAdded   datetime    加入音樂庫的時間
        playCount   int         總播放次數
    """
    def __init__(self,
                 albumID, totalTime, name, trackCount, dateAdded, playCount):
        self.albumID = albumID
        self.totalTime = totalTime
        self.name = name
        self.trackCount = trackCount
        self.dateAdded = dateAdded
        self.playCount = playCount

class MusicLibrary:
    """
    class MusicLibrary
    Version 0.1.0
    對應版本
        MusicAnaly  0.1.0   -   0.1.1
        Music       0.1.0
        Album       0.1.0
    成員變量
        musicList   [Music]     音樂列表
        albumList   [Album]     專輯列表
        date        datetime    音樂庫修改時間

    Version 0.2.0
    對應版本
        MusicAnaly  0.2.0
        Music       0.2.0
        Album       0.1.0
    新增成員變量
        version     str     Library 數據版本
    """
    def __init__(self, musicList, albumList, date):
        self.version = "0.2.0"
        self.musicList = musicList
        self.albumList = albumList
        self.date = date

    def getDateStr(self):
        return ("{year:0>4}-{month:0>2}-{day:0>2}"
                .format(year = self.date.year,
                        month = self.date.month,
                        day = self.date.day))

def getSampleLibrary():
    """
    獲取最新版本的音樂庫數據，用於糾正舊版數據
    返回:
        MusicLibrary    音樂庫類
    """
    libraryXMLFilename = "iTunes Music Library.xml"
    try:
        libraryXMLFile = open(libraryXMLFilename, "r")
    except Exception as error:
        print("ERROR: {error}".format(error = error))
        exit()

    # 時間字符串格式
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"

    # 讀取音樂庫修改時間並拋棄頭部
    libraryLine = libraryXMLFile.readline()
    while "<key>Date</key>" not in libraryLine:
        libraryLine = libraryXMLFile.readline()
    libraryLine = libraryLine.replace("\t<key>Date</key><date>", "")
    libraryLine = libraryLine.replace("</date>\n", "")
    libraryDate = datetime.strptime(libraryLine, dateFormat)
    while "<key>Tracks</key>" not in libraryLine:
        libraryLine = libraryXMLFile.readline()
    print("開始掃描 {filename}".format(filename = libraryXMLFilename))
    libraryXMLFile.readline()

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

    libraryLine = libraryXMLFile.readline()
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
            libraryLine = libraryXMLFile.readline()
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
        libraryLine = libraryXMLFile.readline()
    libraryXMLFile.close()

    library = MusicLibrary(musicList, albumList, libraryDate)
    return library

def detectLibreryVersion(library):
    """
    檢測音樂庫記錄的數據版本
    參數列表：
        library MusicLibrary    需檢測版本的音樂庫
    返回：
        str     版本號字符串
    """
    version = "0"
    try:
        version = library.version
    except Exception as error:
        # 僅 0.1.0 版的數據內無版本變量
        version = "0.1.0"
    return version

def update(oldLibrary):
    """
    更新音樂庫數據版本
    參數列表:
        oldLibrary  MusicLibrary    需要升級的音樂庫
    """
    print("開始更新")
    print("正在獲取最新版的樣本⋯")
    sampleLibrary = getSampleLibrary()
    print("獲取成功")
    # 檢測 trackID 的偏差
    print("正在檢測偏差…")
    deviation = 0
    # 總共檢測5次
    matchCount = 0
    for oldMusic in oldLibrary.musicList:
        didMatch = False;
        for sampleMusic in sampleLibrary.musicList:
            if (sampleMusic.name == oldMusic.name and
                sampleMusic.album == oldMusic.album):
                newDeviation = sampleMusic.trackID - oldMusic.trackID
                didMatch = True
                matchCount += 1
                break
        if didMatch:
            if matchCount == 1:
                deviation = newDeviation
            else:
                if deviation != newDeviation:
                    print("匹配異常，偏差不一致")
                    return
            if matchCount == 5:
                break
    print("偏差檢測完成，偏差為 {deviation}".format(deviation = deviation))

    changedMusicList = []
    version = detectLibreryVersion(oldLibrary)
    print("開始更新數據 {oldVersion} -> {lastVersion}"
          .format(oldVersion = version, lastVersion = lastVersion))

    newMusicList = []
    for sampleMusic in sampleLibrary.musicList:
        for oldMusic in oldLibrary.musicList:
            if sampleMusic.trackID == oldMusic.trackID + deviation:
                newMusic = Music(sampleMusic.trackID,
                                 sampleMusic.totalTime,
                                 sampleMusic.discNumber,
                                 sampleMusic.trackNumber,
                                 sampleMusic.year,
                                 sampleMusic.dateAdded,
                                 oldMusic.playCount,
                                 sampleMusic.name,
                                 sampleMusic.artist,
                                 sampleMusic.album,
                                 sampleMusic.genre,
                                 sampleMusic.location)
                newMusicList.append(newMusic)
    newLibrary = MusicLibrary(newMusicList,
                              oldLibrary.albumList,
                              oldLibrary.date)
    newLibraryFilename = ("./Library/{date}-new.data"
                          .format(date = newLibrary.getDateStr()))
    newLibraryFile = open(newLibraryFilename, "wb")
    pickle.dump(newLibrary, newLibraryFile)
    newLibraryFile.close()
    print("已生成文件：{filename}\n".format(filename = newLibraryFilename))

def main():
    # 检查并创建 Library 文件夹
    if not os.path.exists("./Library"):
        os.mkdir("./Library")
    # 創建起點時間
    zeroTime = datetime.fromtimestamp(0)

    # 處理命令行參數
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hu:",
                                   ["help", "update="])
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
        elif opt in ("-u", "--update"):
            oldLibraryFilename = argv
            oldLibraryFilename = "./Library/" + oldLibraryFilename
            try:
                oldLibraryFile = open(oldLibraryFilename, "rb")
            except Exception as error:
                print("ERROR: {error}".format(error = error))
                exit()
            oldLibrary = pickle.load(oldLibraryFile)
            oldVersion = detectLibreryVersion(oldLibrary)
            if oldVersion == lastVersion:
                print("{filename} 的數據版本為 {version}，不需升級"
                      .format(filename = oldLibraryFilename,
                              version = oldVersion))
            else:
                print("{filename} 的數據版本為 {version}，需要升級"
                      .format(filename = oldLibraryFilename,
                              version = oldVersion))
                update(oldLibrary)
        else:
            print("參數 {opt} 不可用。".format(opt))
            print(optionsHelp)

# 最新版本號
lastVersion = "0.2.0"
# 起點時間
zeroTime = datetime.fromtimestamp(0)
if __name__ == '__main__':
    main()
