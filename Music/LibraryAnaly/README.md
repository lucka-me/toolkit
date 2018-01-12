# 音乐库分析
适用于 iTunes 音乐库的分析器。

## Functions
扫描 XML 格式的 iTunes 音乐库文件，生成 `.data` 记录，对比历史记录，生成报告。

音乐库记录会记录歌曲的下列信息：

| Key Name      | Description
| :------------ | :----------
| `trackID`     | 歌曲唯一序列号
| `totalTime`   | 歌曲时长
| `discNumber`  | 光盘序号
| `trackNumber` | 音轨序号
| `year`        | 歌曲发行年份
| `dateAdded`   | 加入音乐库的时间
| `playCount`   | 播放次数
| `name`        | 歌曲标题
| `artist`      | 艺术家
| `album`       | 专辑名称

音乐库记录会记录专辑的下列信息：

| Key Name     | Description
| :----------- | :----------
| `albumID`    | 专辑唯一序列号
| `totalTime`  | 专辑总时长
| `name`       | 专辑
| `trackCount` | 音轨数量
| `dateAdded`  | 加入音乐库的时间
| `playCount`  | 总播放次数

单个音乐库的报告内容包括以下内容：

* 歌曲总数、专辑总数、总时长
* 总播放次数、总播放时长
* 播放次数和播放时长的 TOP 10 列表（分歌曲和专辑）

两个音乐库对比的报告内容包括以下内容：

* 新增歌曲数、新增专辑数
* 期间播放次数、期间播放时长
* 期间播放次数和播放时长的 TOP 10 列表（分歌曲和专辑）

## Requirements
### Environment
  * Python 3

### Files
| Filename                 | Note
| :----------------------- | :---
| iTunes Music Library.xml | iTunes 音乐库文件

## Useage
本工具需要通过命令行参数使用。

生成的 `.data` 记录储存在 `./Library` 文件夹中。

### Command Line Option List
| Opt / Long Opt   | Args         | Note
| :--------------- | :----------- | :---
| `-a` `--add`     |              | 扫描新的 iTunes 音乐库 XML 文件并保存数据
| `-r` `--report`  | `<filename>` | 生成指定音乐库记录的报告
| `-c` `--compare` | `<filename>` | 比较当前音乐库和过去指定音乐库记录并生成报告
| `-h` `--help`    |              | 显示帮助文本

## Changelog
### [0.1.1] - 2018-01-12
#### Fixed
- 对比记录时未将新增歌曲和专辑的播放次数和总播放时间计算在内

### [0.1.0] - 2018-01-03
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
