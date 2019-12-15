# 服饰列表生成器
适用于[宝可梦 剑／盾](https://wiki.52poke.com/wiki/寶可夢_劍%EF%BC%8F盾)的服饰列表生成器，由[ClothTableGenerator-USUM](../ClothTableGenerator-USUM/)修改而来。

## Features
以 [Serebii.net 资料页面](https://www.serebii.net/swordshield/customisation.shtml)的 HTML 代码为基础，辅以游戏翻译文本，生成完整的、适用于神奇宝贝百科的表格代码，同时从 Serebii.net 上获取、处理相应的图片。

由于表格内容复杂且多有遗漏，需要经过人工处理才能使用。

## Requirements
### Environment and Packages
  * Python 3
  * [ImageMagick](http://www.imagemagick.org/script/index.php "ImageMagick")
  * [Wand](http://docs.wand-py.org/en/0.4.4/ "Wand")

### Files
| Filename               | Description
| :--------------------- | :----------
| `source.html`          | HTML 文件，需要自行从网页代码截选相应部分
| `cloth_zh.txt`         | 服饰中文文本
| `cloth_ja.txt`         | 服饰日文文本
| `cloth_en.txt`         | 服饰英文文本
| `cloth_zh_convert.txt` | 中文简繁转换文本（使用[生成器](../ZhConvertGenerator/)生成）
| `location_zh.txt`      | 地点名称中文文本
| `location_en.txt`      | 地点名称中文文本

生成器并不实际解析HTML，而是从每行中提取相应的文字，因此输入的`source.html`文件必须满足格式要求。

1. 文件的第一行必须是表格前的标题行，例如：
   ```html
   <p><h3><a name="mhat"></a>Hat</h3></p>
   <table class="dextable" align="center">
   ```
2. 文件的最后一行必须是表格的最后一行，即`</tr>`

## Changelog

```markdown
### [0.5.0] - 2019-12-TBA
首个版本
```

## Licence
本工具基于 [MIT 协议](../../LICENSE)。