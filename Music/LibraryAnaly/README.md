# LibraryAnaly
适用于 iTunes 音乐库的分析工具。

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
| `genre`       | 音乐类型
| `location`    | 音频文件路径

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

对于旧版本生成的记录，可使用数据更新工具更新记录。

## Requirements
### Environment
  * Python 3

### Files
| Filename                 | Note
| :----------------------- | :---
| iTunes Music Library.xml | iTunes 音乐库文件

## Useage
本工具及数据更新工具均需要通过命令行参数使用。

生成的 `.data` 记录储存在 `./Library` 文件夹中。

### LibraryAnaly
工具的主程序文件为 `main.py`。

#### Command Line Option List
| Opt / Long Opt   | Args         | Note
| :--------------- | :----------- | :---
| `-a` `--add`     |              | 扫描新的 iTunes 音乐库 XML 文件并保存数据
| `-r` `--report`  | `<filename>` | 生成指定音乐库记录的报告
| `-c` `--compare` | `<filename>` | 比较当前音乐库和过去指定音乐库记录并生成报告
| `-h` `--help`    |              | 显示帮助文本

### Data Update Tool
数据更新工具的主程序文件为 `update.py`，需要 `iTunes Music Library.xml` 文件作为更新样本。

#### Command Line Option List
| Opt / Long Opt   | Args         | Note
| :--------------- | :----------- | :---
| `-u` `--update`  | `<filename>` | 更新制定记录的数据文件
| `-h` `--help`    |              | 显示帮助文本

## Changelog
### [0.2.0] - 2018-01-12
#### Version
| Tool / File      | Version
| :--------------- | :------
| LibraryAnaly     | 0.2.0
| Data Update Tool | 0.2.0
| Data             | 0.2.0

#### Added
- 歌曲记录中增加以下项目：

| Key Name   | Description
| :--------- | :----------
| `genre`    | 音乐类型
| `location` | 音频文件路径

- 对记录进行版本管理
- 独立的数据更新工具，用于将较旧的记录更新为新版 LibraryAnaly 可读的格式
- 主函数

#### Changed
- 更新注释和代码内文档

### [0.1.1] - 2018-01-12
#### Fixed
- 对比记录时未将新增歌曲和专辑的播放次数和总播放时间计算在内

### [0.1.0] - 2018-01-03
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
