# DEM 生成器
根据高程采样点数据建立 DEM。

## Functions
根据不规则分布采样点，通过搜索圆和加权平均法建立规则格网 DEM。

利用 [matplotlib](https://matplotlib.org "matplotlib") 生成 DEM 三维预览。

### Output files
* `.txt` 格式的结果数据
* `.svg` 格式的采样点分布图、DEM 分布图
* `.svg` 格式的 DEM 灰度图

## Requirements
### Environment and Packages
* Python 3
* [matplotlib](https://matplotlib.org "matplotlib")

### File
| Filename | Description
| :------- | :----------
| `*.*`    | 源数据文件

### Source Data Format
```
1   <Coordinate X>  <Coordinate Y>  <Elevation>
```
每行各项数据以 Tab 分隔。

#### Example
```
1	1000.000 	1000.000 	1138.000
2	1066.510 	978.184 	1126.163
3	1096.171 	1002.457 	1128.254
...
```

## Useage
本工具需要通过命令行参数使用。

### Command Line Option List
| Opt / Long Opt      | Args         | Note
| :------------------ | :----------- | :---
| `-i` `--input`      | `<filename>` | 源数据文件名，带后缀
| `-o` `--output`     | `<filename>` | 输出文件名，不带后缀（会生成多个文件）
| `-r` `--resolution` | `<number>`   | 分辨率（米）
| `--minimum`         | `<number>`   | 搜索圆内采样点个数最小值
| `-h` `--help`       |              | 显示帮助文本

## Changelog
### [0.1.0] - 2018-03-31
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
