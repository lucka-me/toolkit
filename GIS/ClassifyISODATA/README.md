# ISODATA 影像分类器
使用 ISODATA 算法对影像像素进行分类。

## Functions
使用 ISODATA 算法对影像像素进行分类，并生成结果图像。

仅为算法的实现，运行速度极慢，没有实用价值。

## Requirements
### Environment and Packages
* Python 3
* [Pillow](http://python-pillow.org "Pillow")
* [NumPy](http://www.numpy.org "numpy")
* [matplotlib](https://matplotlib.org "matplotlib")

### File
| Filename | Description
| :------- | :----------
| `*.*`    | 源图像文件（可被 Pillow 解析的格式）

## Useage
本工具需要通过命令行参数使用。

### Command Line Option List
| Long Opt / Opt | Args         | Note
| :------------- | :----------- | :---
| `--input`      | `<filename>` | 源图像文件名
| `--output`     | `<filename>` | 输出图像文件名
| `--rgb`        |              | 以彩色进行分类（更慢）
| `--gray`       |              | 以灰度图进行分类（默认）
| `--K`          | `<number>`   | 类别数（期望）（默认为3）
| `--TN`         | `<number>`   | 每个类别中样本最小数目（期望）（默认为3）
| `--TS`         | `<number>`   | 每个类别的标准差（默认为4.0）
| `--TC`         | `<number>`   | 每个类别间的最小距离（默认为40）
| `--L`          | `<number>`   | 每次允许合并的最大类别对的数量（默认为10）
| `--I`          | `<number>`   | 允许迭代的次数上限（默认为8）
| `--help` `-h`  |              | 显示帮助文本

## Changelog
### [0.1.2] - 2018-05-29
#### Added
- 合并和分裂时显示结果

### [0.1.1] - 2018-05-27
#### Fixed
- 彩色分类的一些算法错误

### [0.1.0] - 2018-05-13
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
