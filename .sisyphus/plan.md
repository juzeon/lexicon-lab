# Lexicon-Lab 项目规划

> 一个灵活的中文词语搜索 CLI 工具

## 技术选型

- **语言**: Python
- **数据存储**: JSON 文件 + 内存索引
- **CLI 框架**: typer
- **拼音处理**: pypinyin
- **JSON 解析**: orjson

## 项目结构

```
lexicon-lab/
├── lexicon/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口
│   ├── search.py           # 搜索引擎核心
│   ├── index.py            # 内存索引构建
│   ├── pinyin_utils.py     # 拼音处理
│   ├── models.py           # 数据模型
│   ├── games.py            # 游戏功能 (接龙/猜词等)
│   └── stats.py            # 统计功能
├── data/
│   ├── raw/                # 原始数据
│   │   ├── idiom.json      # 成语库
│   │   └── words.json      # 词语库
│   └── processed/          # 预处理后的索引
│       └── index.pkl       # pickle 序列化索引
├── scripts/
│   └── build_index.py      # 数据预处理脚本
├── tests/
├── pyproject.toml
└── README.md
```

## 数据模型

```python
@dataclass
class Word:
    word: str                    # 词语
    pinyin: str                  # 完整拼音 (带声调)
    pinyin_no_tone: str          # 拼音 (无声调)
    pinyin_initials: str         # 首字母 "xgcl"
    tones: str                   # 声调序列 "1,2,3,4"
    rhyme: str                   # 尾字韵母
    first_char: str              # 首字
    last_char: str               # 尾字
    chars: list[str]             # 所有字
    length: int                  # 字数
    definition: str              # 释义
    source: str | None           # 出处
    example: str | None          # 例句
    category: str                # 成语/词语/歇后语
    structure: str | None        # AABB/ABAC
    synonyms: list[str] | None   # 近义词
    antonyms: list[str] | None   # 反义词
    frequency: int | None        # 词频
```

## 索引结构

```python
class LexiconIndex:
    words: list[Word]
    
    # 快速查找索引
    by_first_char: dict[str, list[int]]
    by_last_char: dict[str, list[int]]
    by_char: dict[str, list[int]]
    by_pinyin_initials: dict[str, list[int]]
    by_pinyin_no_tone: dict[str, list[int]]
    by_rhyme: dict[str, list[int]]
    by_length: dict[int, list[int]]
    by_category: dict[str, list[int]]
    by_structure: dict[str, list[int]]
    
    # 统计数据
    char_freq_start: Counter
    char_freq_end: Counter
    char_freq_all: Counter
```

## 核心功能

### 1. 基础搜索

| 功能 | 选项 | 说明 |
|------|------|------|
| 首字搜索 | `--start 天` | 以"天"开头 |
| 尾字搜索 | `--end 天` | 以"天"结尾 |
| 包含搜索 | `--contains 心` | 包含"心"字 |
| 拼音首字母 | `--pinyin xgcl` | 匹配拼音首字母 |
| 全拼搜索 | `--full-pinyin "tian kong"` | 完整拼音匹配 |
| 正则搜索 | `--regex "不.*不.*"` | 正则表达式 |
| 长度筛选 | `--length 4` | 指定字数 |
| 类型筛选 | `--category 成语` | 成语/词语/歇后语 |

### 2. 结构搜索

| 功能 | 选项 | 示例结果 |
|------|------|---------|
| AABB | `--structure AABB` | 高高兴兴 |
| ABAB | `--structure ABAB` | 研究研究 |
| ABAC | `--structure ABAC` | 一心一意 |
| ABCC | `--structure ABCC` | 喜气洋洋 |
| AABC | `--structure AABC` | 津津有味 |
| ABCB | `--structure ABCB` | 心服口服 |
| 通配符 | `--pattern 一?一?` | 一心一意 |

### 3. 拼音相关

| 功能 | 选项 | 说明 |
|------|------|------|
| 押韵搜索 | `--rhyme ang` | 韵母是 ang |
| 声调搜索 | `--tone 2,4,2,4` | 匹配声调 |
| 同音词 | `--homophone 意义` | 同音词 |

### 4. 语义/关联

| 命令 | 说明 |
|------|------|
| `lexicon synonym 高兴` | 近义词 |
| `lexicon antonym 高兴` | 反义词 |
| `lexicon related 春天` | 相关词 |
| `lexicon define 别有洞天` | 查释义 |

### 5. 游戏/工具

| 命令 | 说明 |
|------|------|
| `lexicon chain 天` | 成语接龙 |
| `lexicon fly 春` | 飞花令 |
| `lexicon random -l 4` | 随机词语 |
| `lexicon quiz` | 猜词游戏 |
| `lexicon fill "一?一?"` | 填字游戏 |

### 6. 统计/导出

| 命令 | 说明 |
|------|------|
| `lexicon stats` | 词库统计 |
| `lexicon freq --position end` | 字频统计 |
| `lexicon batch input.txt` | 批量搜索 |

## CLI 命令

```bash
lexicon <command> [options]

Commands:
  search      搜索词语
  chain       成语接龙
  define      查看释义
  synonym     查近义词
  antonym     查反义词
  related     相关词语
  random      随机词语
  quiz        猜词游戏
  fill        填字游戏
  fly         飞花令
  freq        字频统计
  stats       词库统计
  batch       批量搜索
  init        初始化词库
  update      更新词库

Search Options:
  -s, --start TEXT        首字
  -e, --end TEXT          尾字
  -c, --contains TEXT     包含字符 (可多个)
  -p, --pinyin TEXT       拼音首字母
  -P, --full-pinyin TEXT  完整拼音
  -r, --regex TEXT        正则表达式
  -l, --length INT        词语长度
  -t, --category TEXT     类型
  --structure TEXT        结构
  --pattern TEXT          通配符模式
  --rhyme TEXT            韵母
  --tone TEXT             声调模式
  --homophone TEXT        同音词
  --limit INT             结果数量 [default: 20]
  --offset INT            跳过前N条
  -o, --output FILE       输出到文件
  --format TEXT           格式 (text/json/csv)
  --no-pinyin             不显示拼音
  --no-definition         不显示释义
```

## CLI 输出示例

```bash
$ lexicon search --end 天 --length 4 --limit 5

找到 156 条结果:

1. 别有洞天 [bié yǒu dòng tiān] - 比喻另有一番境界
2. 坐井观天 [zuò jǐng guān tiān] - 比喻眼界狭小
3. 开天辟地 [kāi tiān pì dì] - 比喻前所未有
4. 海阔天空 [hǎi kuò tiān kōng] - 形容心胸开阔
5. 异想天开 [yì xiǎng tiān kāi] - 形容想法离奇

使用 --limit 增加显示数量
```

```bash
$ lexicon chain 天 --count 5

天长地久 → 久负盛名 → 名不虚传 → 传为佳话 → 话不投机
```

```bash
$ lexicon stats

词库统计:
  成语: 30,895 条
  词语: 125,432 条
  歇后语: 5,123 条
  总计: 161,450 条

常见尾字 TOP5: 人(2341) 天(1892) 心(1654) 地(1432) 日(1205)
```

## 数据来源

| 数据源 | 地址 | 内容 |
|-------|------|------|
| chinese-xinhua | github.com/pwxcoo/chinese-xinhua | 成语、词语、歇后语 |
| jieba dict.txt | github.com/fxsjy/jieba | 词频数据 |
| pypinyin | 内置 | 拼音转换 |

## 算法要点

### 多音字处理

存储所有可能的拼音组合:
```python
"朝阳": {
    "pinyin_variants": ["zhāo yáng", "cháo yáng"],
    "initials_variants": ["zy", "cy"]
}
```

### 结构识别

```python
STRUCTURE_PATTERNS = {
    "AABB": r'^(.)\1(.)\2$',
    "ABAB": r'^(.)(.)\\1\\2$',
    "ABAC": r'^(.)(.)(.)\\2$',
    "ABCC": r'^(.)(.)(.)\\3$',
    "AABC": r'^(.)\1(.)(.)$',
    "ABCB": r'^(.)(.)(.)\\2$',
}
```

### 成语接龙

BFS 实现，优先选择"后续可选成语最多"的路径。

## 性能预估

| 数据规模 | 内存占用 | 加载时间 |
|---------|---------|---------|
| ~30,000 成语 | ~15MB | <0.5s |
| +100,000 词语 | ~50MB | ~1s |
| 总计带索引 | ~80MB | ~1.5s |

首次运行构建索引并缓存到 `~/.cache/lexicon/`，后续使用 pickle 快速加载。

---

## 执行任务清单

### P0: 项目初始化

- [x] 创建 pyproject.toml 配置
- [x] 创建项目目录结构
- [x] 下载 chinese-xinhua 数据集
- [x] 实现基础 CLI 框架

### P1: 核心搜索功能
- [x] 实现数据模型 (Word dataclass)
- [x] 实现索引构建 (LexiconIndex)
- [x] 实现拼音处理 (多音字)
- [x] 实现 search 命令 (首字/尾字/包含/拼音首字母/正则/长度/类型)

### P2: 高级搜索功能
- [x] 实现结构识别 (AABB/ABAC等)
- [x] 实现通配符模式搜索 (--pattern)
- [x] 实现押韵搜索 (--rhyme)
- [x] 实现声调搜索 (--tone)
- [x] 实现同音词搜索 (--homophone)

### P3: 语义与游戏功能
- [x] 实现 define 命令 (查释义)
- [-] 实现 synonym/antonym 命令 (近义词/反义词) - **BLOCKED: 数据集缺失** (见 .sisyphus/notepads/plan/blockers.md)
- [x] 实现 chain 命令 (成语接龙)
- [x] 实现 random 命令 (随机词语)
- [x] 实现 quiz 命令 (猜词游戏)
- [x] 实现 fill 命令 (填字游戏)
- [x] 实现 fly 命令 (飞花令)

### P4: 统计与导出
- [x] 实现 stats 命令 (词库统计)
- [x] 实现 freq 命令 (字频统计)
- [x] 实现 batch 命令 (批量搜索)
- [x] 实现结果导出 (text/json/csv)
- [-] 实现 init/update 命令 (词库管理) - **OUT OF SCOPE** (见 .sisyphus/notepads/plan/blockers.md)

### P5: 优化完善
- [x] 索引缓存优化 (pickle)
- [x] 错误处理与友好提示
- [x] 编写测试用例
- [x] 编写 README 文档
