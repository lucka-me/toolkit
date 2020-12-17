# Beldum
维基编辑自动化用户脚本。

## Feature
根据 `Beldum.data` 的配置项执行相关操作。

| Property | Type | Description
| :------- | :--- | :----------
| `title` | `string` / `Regex` | 匹配标题后进行处理
| `replaceList` | `Array<[string | Regex, string]>` | 字符串/正则表达式替换列表
| `procList` | `Array<(code: string) => string>` | 代码处理器列表
| `minorEdit` | `boolean` | 是否勾选「小编辑」
| `summary` | `string` | 编辑摘要

## Changelog
### [0.1.0] - 2020-12-17
首个版本

## Licence
本工具基于 [MIT 协议](../../LICENSE)。