# RTS 转换器
可将全站仪输出的 RTS 转换为 CASS 可读文件的转换器。

## WARNING
**本工具是2017年6月临时编写并只经过短暂的使用，仅有基本功能且可能存在错误。**
**如无必要，本工具将不再更新。**

## Functions
测量学实习中使用的全站仪型号存在差异，输出的数据文件可能是 `.RTS` 文件而不是 CASS 可以直接读取的 `.DATA` 文件。  
本工具可将 `.RTS` 转换为 `.DATA` 文件，剔除无效数据并转换坐标系。

## Requirements
### Compatibility
  * CASS 9.0
    * 其它版本未经测试

### Files
| Filename | Description
| :------- | :----------
| `*.RTS`  | 全站仪输出的 RTS 文件

## Changelog
### [0.1] - 2018-01-13
- 首个基础功能完整的版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。
