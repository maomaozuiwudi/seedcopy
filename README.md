# SeedCopy - 商品信息复制与批量管理工具

SeedCopy 是一款商品信息复制与批量管理工具，帮助电商卖家快速抓取、复制和管理商品信息。

## 功能列表

- **商品信息抓取**：自动抓取商品详情信息
- **批量复制**：批量复制商品到多平台
- **数据清洗**：自动清洗和格式化商品数据
- **模板管理**：商品信息模板创建与使用
- **多语言翻译**：集成 DeepL 自动翻译

## 使用环境

- 操作系统：Windows 10 / Windows 11
- Python 3.11+（如需运行源码）
- 或直接运行编译后的 `SeedCopy.exe`

## 使用方法

### 方式一：运行编译版本
1. 从 Releases 下载最新版本的 `SeedCopy.exe`
2. 双击运行即可

### 方式二：源码运行
```bash
pip install -r requirements.txt
python main.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| main.py | 程序主入口 |
| engine.py | 核心引擎模块 |
| deepl.py | DeepL翻译集成 |
| license.py | 许可证管理 |
| rules.json | 处理规则配置文件 |
| _loader.py | 加载器 |
| build_obfuscated.py | 代码混淆打包脚本 |
| src/ | 源码模块目录 |

## 许可证

MIT License
