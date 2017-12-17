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
|      文件名      |            说明             |
| :-------------- | :-------------------------- |
| source.html     | HTML 文件，需要手动截选相应部分 |
| type_ch.txt     | 服饰类型中文文本              |
| type_jp.txt     | 服饰类型日文文本              |
| type_en.txt     | 服饰类型英文文本              |
| color_ch.txt    | 颜色名称中文文本              |
| color_en.txt    | 颜色名称中文文本              |
| location_ch.txt | 地点名称中文文本              |
| location_en.txt | 地点名称中文文本              |

### Manual Operation
请在源代码中搜索 `# MARK: - Manual Operation`。

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
