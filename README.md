# Lexicon-Lab

> 一个灵活的中文词语搜索 CLI 工具

一个强大的命令行工具，用于搜索和探索中文词语、成语、歇后语。支持多种高级搜索功能，包括拼音、结构模式、押韵等。

*Orchestrated with [OpenCode](https://github.com/anomalyco/opencode) & [OhMyOpenCode](https://github.com/code-yeongyu/oh-my-opencode).*

## ✨ 特性

- 🔍 **灵活搜索**: 支持正则表达式、拼音首字母等多种搜索条件
- 🎯 **高级搜索**: 拼音扩展、谐音搜索、结构识别（AABB/ABAC等）、押韵、声调
- 📖 **词语释义**: 查看详细的词语解释、出处、例句
- 🔗 **成语接龙**: 自动生成成语接龙链
- 🎲 **随机词语**: 根据条件随机获取词语
- 📊 **统计分析**: 词库统计、字频分析
- ⚡ **快速响应**: 使用内存索引，搜索速度快

## 📦 数据集

包含 **326,466** 条词语数据：
- 成语：**31,858** 条
- 词语：280,576 条
- 歇后语：14,032 条

### 数据来源

本项目整合了多个高质量中文词汇数据集：

1. **[chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua)** - 中华新华字典数据库（主要数据源）
   - 提供成语、词语、歇后语的详细释义、出处、例句等
   
2. **[THUOCL](https://github.com/thunlp/THUOCL)** - 清华大学开放中文词库
   - 补充了 961 条高频成语
   - 提供词频统计数据
   
3. **手动补充** - 常见但缺失的成语词语
   - 如：扬名立万、走街串巷等

通过合并去重，相比原始数据集增加了 **963 条成语**，覆盖更全面。

## 🔧 安装

**要求**: Python >= 3.10

```bash
# 克隆项目
git clone https://github.com/yourusername/lexicon-lab.git
cd lexicon-lab

# 安装依赖
pip install -e .

# 验证安装
lexicon --help
```

## 📚 使用方法

### 基础搜索

```bash
# 搜索以"天"结尾的四字词语
lexicon search --regex ".*天$" -l 4 -L 5

# 搜索包含"心"的成语
lexicon search --regex ".*心.*" -t 成语

# 搜索拼音首字母为"xgcl"的词语
lexicon search -i xgcl

# 正则表达式搜索 - 搜索"不X不Y"格式的词语
lexicon search -r "^不.*不.*$"
```

### 拼音与谐音搜索 🆕

```bash
# 拼音转汉字搜索 - 搜索以"wan"发音开头的词语
lexicon search -r "^wan" -p -L 10
# 结果：万、玩、晚、完、弯 等开头的词语

# 拼音包含搜索 - 搜索包含"zhong"发音的词语
lexicon search -r ".*zhong.*" -p
# 结果：包含 中、重、种、终 等字的词语

# 拼音正则搜索 - 正则表达式 + 拼音扩展 🆕
lexicon search -r "^wan.*" -p -t 成语 -L 5
# 搜索以 wan 发音开头的成语
# 结果：弯弓饮羽、剜肉补疮 等

# 拼音正则 + 谐音搜索 🆕
lexicon search -r "^wan.*" -p -h -t 成语 -L 5
# 搜索以 wan 或相似发音(wang/wen/weng/yuan)开头的成语
# 结果：弯弓饮羽、剜肉补疮、网开一面、稳扎稳打 等

# @ 通配符搜索 - 用 @ 代替声母或韵母 🆕
lexicon search -r "^t@cai$" -p -L 10
# t@cai 会扩展为 tiancai, tencai, tacai, tucai 等
# 结果：大采、大菜、大蔡、破财 等

lexicon search -i "t@c" -L 10
# 搜索拼音首字母匹配 t+任意韵母+c 的词语
# 结果：天窗、天垂、天赐、天聪 等

lexicon search -r "^tianc@$" -p -L 10
# tianc@ 会扩展为 tiancai, tiancao, tiancang 等
# 搜索以 tianc 开头加任意韵母的词语

# 拼音模式下的 . 通配符 - 匹配一个拼音音节（一个汉字）🆕
lexicon search -r "^h@..$" -p -h -L 10
# h@ = 以h开头+任意韵母（1个字）
# .. = 任意2个字
# 总共匹配 3字词语
# 结果：合同异、合胃口、海棠果、海豚泳 等

lexicon search -r "^h@...$" -p -h -L 10
# h@ + ... = 4字词语
# 结果：海市蜃楼、海誓山盟、海水桑田 等

# 正则量词 - 使用 {n}, {m,n} 等量词指定字数 🆕
lexicon search -r "^zuoci.{2}$" -p -h
# .{2} = 恰好2个字
# 结果：坐吃山崩、坐吃山空

lexicon search -r "^tian.{1,3}$" -p -L 10
# .{1,3} = 1到3个字
# 结果：天戈、天各一方、天根 等

lexicon search -r "^xin.{2,}$" -p -L 10
# .{2,} = 2个或更多字
# 结果：心惊胆战、心惊肉跳、心照不宣 等

lexicon search -r "^yi.{,3}$" -p -L 10
# .{,3} = 0到3个字
# 结果：訑言、溢言虚美、溢于言表 等

# 谐音搜索 - 搜索声母相似的成语
lexicon search -i zgcd -h -L 10
# zgcd (中国成都) 会扩展到 cgcd, sgcd, zgsd 等相似发音
# 结果：枕戈尝胆(zgcd), 称功颂德(cgsd), 知高识低(zgsd) 等

# 组合使用
lexicon search -r "^wan" -p -h -t 成语
# 搜索以wan或类似发音开头的成语
```

### 分页搜索 🆕

```bash
# 获取第2页结果，每页显示10条
lexicon search -r ".*天.*" -L 10 -P 2

# 获取所有结果（不限制数量）
lexicon search -r ".*天.*" -L 0

# 第一页（默认）
lexicon search -r ".*天.*"
# 等同于: lexicon search -r ".*天.*" -P 1 -L 20
```

### 高级搜索

```bash
# 通配符搜索 (? = 任意字, . = 单个字符, .* = 任意字符)
lexicon search -r "^一.一.$"

# 结构搜索
lexicon search --structure AABB

# 押韵搜索
lexicon search --rhyme ang -l 4

# 声调搜索
lexicon search --tone "1,2,3,4"
```

### 词语释义

```bash
# 查看词语详细信息
lexicon define 天长地久
```

输出：
```
📖 天长地久
   拼音: tiān cháng dì jiǔ
   类型: 成语
   释义: 跟天和地存在的时间那样长。形容时间悠久...
   出处: 《老子》第七章...
```

### 成语接龙

```bash
# 从"天"开始接龙5个成语
lexicon chain 天 --count 5
```

输出：
```
🔗 成语接龙：
天 → 天宝当年 → 年富力强 → 强本弱枝 → 枝布叶分 → 分崩离析
```

### 随机词语

```bash
# 随机获取一个四字成语
lexicon random-word --category 成语 --length 4
```

### 统计信息

```bash
# 查看词库统计
lexicon stats

# 字频统计
lexicon freq --position start --limit 10  # 首字频率
lexicon freq --position end --limit 10    # 尾字频率
lexicon freq --position all --limit 20    # 全部字频
```

## 🎮 命令列表

| 命令 | 说明 |
|------|------|
| `search` | 搜索词语（支持多种过滤条件） |
| `define` | 查看词语释义 |
| `chain` | 成语接龙游戏 |
| `random-word` | 随机获取词语 |
| `stats` | 词库统计信息 |
| `freq` | 字频统计 |

## 🔍 搜索选项

```
search 命令支持的选项:

  -i, --initials TEXT     拼音首字母
  -r, --regex TEXT        正则表达式
  -l, --length INT        词语长度
  -t, --category TEXT     类型 (成语/词语/歇后语)
  --structure TEXT        结构 (AABB/ABAC/ABAB/ABCC/AABC/ABCB)
  --rhyme TEXT            韵母
  --tone TEXT             声调模式
  -p, --enable-pinyin     启用拼音搜索 (将拼音转为汉字)
  -h, --enable-homophone  启用谐音搜索 (扩展相似发音)
  -L, --limit INT         每页结果数量 (0=不限制) [default: 20]
  -P, --page INT          页码 [default: 1]
  --no-pinyin             不显示拼音
  --no-definition         不显示释义
  -o, --output PATH       输出文件路径
  -f, --format TEXT       输出格式 (text/json/csv)
```

## 📖 示例场景

### 文字游戏
```bash
# 找所有"一X一Y"格式的成语
lexicon search -r "^一.一.$" -t 成语

# 成语接龙比赛
lexicon chain 天 --count 20
```

### 诗词写作
```bash
# 找押"ang"韵的四字词
lexicon search --rhyme ang -l 4

# 找以"春"结尾的词语
lexicon search -r ".*春$"
```

### 起名字
```bash
# 找拼音首字母是"zxy"的词语
lexicon search -i zxy

# 找AABB结构的叠词
lexicon search --structure AABB
```

### 汉语学习
```bash
# 查看成语释义和出处
lexicon define 画蛇添足

# 统计最常见的字
lexicon freq --position all --limit 50
```

## 🏗️ 项目结构

```
lexicon-lab/
├── lexicon/              # 主程序代码
│   ├── cli.py           # CLI 入口
│   ├── search.py        # 搜索引擎
│   ├── index.py         # 内存索引
│   ├── models.py        # 数据模型
│   ├── pinyin_utils.py  # 拼音处理
│   └── structure.py     # 结构识别
├── data/raw/            # 原始数据
├── pyproject.toml       # 项目配置
└── README.md
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 数据来源：
  - [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) - 中华新华字典数据库
  - [THUOCL](https://github.com/thunlp/THUOCL) - 清华大学开放中文词库
- 拼音处理：[pypinyin](https://github.com/mozillazg/python-pinyin)
