# 数据集升级说明

## 升级概述

lexicon-lab 的数据集已从单一数据源升级为**多源合并数据集**，覆盖更全面，质量更高。

## 数据变化

### 原始数据集
- **来源**: chinese-xinhua
- **成语数**: 30,895 条
- **总词语**: 325,503 条

### 升级后数据集
- **来源**: chinese-xinhua + THUOCL + 手动补充
- **成语数**: **31,858 条** ✨ (+963)
- **总词语**: **326,466 条** ✨ (+963)

## 数据源详情

### 1. chinese-xinhua（主要数据源）
- **GitHub**: https://github.com/pwxcoo/chinese-xinhua
- **贡献**: 提供基础成语、词语、歇后语数据
- **优点**: 数据详细，包含释义、出处、例句等完整信息

### 2. THUOCL（清华大学开放中文词库）
- **GitHub**: https://github.com/thunlp/THUOCL
- **贡献**: 补充 961 条高频成语
- **优点**: 权威数据源，包含词频统计

### 3. 手动补充
- **贡献**: 2 条常用但缺失的成语
- **示例**: 
  - 扬名立万 (yáng míng lì wàn)
  - 走街串巷 (zǒu jiē chuàn xiàng)

## 合并策略

### 去重规则
- 以成语**词语本身**为唯一键
- 优先级: chinese-xinhua > THUOCL > 手动补充
- 手动补充的条目会强制覆盖已有数据（保证准确性）

### 字段映射
所有数据源统一为以下格式：
```json
{
  "word": "成语",
  "pinyin": "拼音",
  "explanation": "解释",
  "derivation": "出处",
  "example": "例句",
  "abbreviation": "拼音首字母缩写",
  "source": "数据来源"
}
```

## 如何重新生成数据

运行合并脚本：
```bash
python scripts/merge_datasets.py
```

这将：
1. 从 `data/raw/idiom.json` 加载原始数据
2. 从 `data/sources/` 加载补充数据源
3. 合并、去重并生成 `data/raw/idiom_merged.json`
4. 验证关键成语是否存在

## 数据文件说明

```
data/
├── raw/
│   ├── idiom.json          # 原始成语数据（保留备份）
│   ├── idiom_merged.json   # 合并后的成语数据（使用中）✨
│   ├── word.json           # 词语数据
│   └── xiehouyu.json       # 歇后语数据
└── sources/                # 补充数据源
    ├── crazywhale_idioms.json  # crazywhalecc/idiom-database
    └── thuocl_chengyu.txt      # THUOCL 成语库
```

## 验证数据质量

### 检查成语是否存在
```bash
lexicon search --regex "扬名立万"
lexicon search --regex "走街串巷"
```

### 查看统计信息
```bash
lexicon stats
```

应该显示：
- 成语: 31,858 条
- 总词语: 326,466 条

## 未来计划

- [ ] 持续监控并添加缺失的常用成语
- [ ] 考虑集成更多高质量数据源
- [ ] 建立社区反馈机制，收集缺失词语

## 更新日志

### 2026-02-01
- ✅ 集成 THUOCL 清华大学开放中文词库
- ✅ 添加手动补充的常见成语（扬名立万、走街串巷）
- ✅ 创建自动化合并脚本
- ✅ 成语数量增加 963 条 (30,895 → 31,858)
