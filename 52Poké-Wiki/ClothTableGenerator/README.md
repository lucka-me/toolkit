# 服饰列表生成器
适用于[精灵宝可梦 究极之日／究极之月](https://wiki.52poke.com/wiki/精灵宝可梦_究极之日／究极之月)的服饰列表生成器。

## Functions
以 [Serebii.net 资料页面](https://serebii.net/ultrasunultramoon/customisation.shtml)的 HTML 代码为基础，辅以游戏翻译文本，生成完整的、适用于神奇宝贝百科的表格代码，同时从 Serebii.net 上获取、处理相应的图片。

## Requirements
### Environment and Packages
  * Python 3
  * [ImageMagick](http://www.imagemagick.org/script/index.php "ImageMagick")
  * [Wand](http://docs.wand-py.org/en/0.4.4/ "Wand")

### Files
| Filename        | Description
| :-------------- | :--------------------------
| source.html     | HTML 文件，需要手动截选相应部分
| type_ch.txt     | 服饰类型中文文本
| type_jp.txt     | 服饰类型日文文本
| type_en.txt     | 服饰类型英文文本
| color_ch.txt    | 颜色名称中文文本
| color_en.txt    | 颜色名称中文文本
| location_ch.txt | 地点名称中文文本
| location_en.txt | 地点名称中文文本

## Changelog
### [0.4.1] - 2018-01-31
#### Fixed
- 识别为发饰时会误判性别导致错误

### [0.4.0] - 2018-01-31
#### Added
- 图片处理时的简单错误处理

#### Changed
- 手动选择性别和服饰类型改为自动识别
- 未识别服饰类型时仍然可以下载和处理图片

#### Fixed
- 处理女生服饰 HTML 代码时会出现错误

### [0.3.2] - 2018-01-13
#### Fixed
- 设定性别时可能无法成功

### [0.3.1] - 2017-12-22
#### Fixed
- 显示及输出价格无千分位符

### [0.3.0] - 2017-12-22
#### Added
- 合并相同类型的服饰行（类型序列号、价格及购买城市序列号一致者）

### [0.2.0] - 2017-12-18
#### Added
- 处理前的参数设置，包括性别、服饰类型
- 根据参数自动设置变量
- 选择是否下载和处理图片
- 表格底栏，包括数量和价格统计

#### Changed
- 表头背景色，浅色 -> 普通色

#### Removed
- `Manual Operation`

#### Fixed
- 输出文本修复：`仅太阳/月亮` -> `仅究极之日/究极之月`

### [0.1.1] - 2017-12-17
#### Added
- 运行计时器
- 源文件错误处理： `GI` -> `Gi`
- 图片裁切尺寸注释
- 图片尺寸的手动修改标记
- 本 Changelog

#### Changed
- 运行提示中添加图片尺寸的注释

#### Fixed
- 显示文本修正

### [0.1] - 2017-12-17
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
