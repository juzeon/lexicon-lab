#!/usr/bin/env python3
"""
数据集合并脚本
将多个中文成语数据源合并为一个统一的数据集
"""

import json
from pathlib import Path
from typing import Dict, List, Set
import re

def load_original_idioms() -> List[Dict]:
    """加载原始 idiom.json 数据"""
    idiom_path = Path(__file__).parent.parent / 'data' / 'raw' / 'idiom.json'
    with open(idiom_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_crazywhale_idioms() -> List[Dict]:
    """加载 crazywhalecc/idiom-database 数据"""
    source_path = Path(__file__).parent.parent / 'data' / 'sources' / 'crazywhale_idioms.json'
    with open(source_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_thuocl_idioms() -> List[Dict]:
    """加载 THUOCL 成语库数据"""
    source_path = Path(__file__).parent.parent / 'data' / 'sources' / 'thuocl_chengyu.txt'
    idioms = []
    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts:
                word = parts[0].strip()
                if word:
                    idioms.append({
                        'word': word,
                        'frequency': int(parts[1]) if len(parts) > 1 else 0
                    })
    return idioms

def load_chengyujielong_idioms() -> List[Dict]:
    """加载成语接龙数据集 (43,165条成语)"""
    source_path = Path(__file__).parent.parent / 'data' / 'sources' / 'chengyujielong_idioms.json'
    with open(source_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_manual_idioms() -> List[Dict]:
    """手动添加缺失的常见成语"""
    return [
        {
            'word': '扬名立万',
            'pinyin': 'yáng míng lì wàn',
            'explanation': '意指传播名声并确立形象。多用于形容事业有成，在社会上有名气，在行业里也有威望的个人或团体。',
            'derivation': '现代词汇',
            'example': '他凭借这部作品扬名立万，成为业界翘楚。',
            'abbreviation': 'ymlw',
            'source': 'manual'
        },
        {
            'word': '走街串巷',
            'pinyin': 'zǒu jiē chuàn xiàng',
            'explanation': '走大街串小巷，指走遍居民聚集地的各个角落。',
            'derivation': '老舍《四世同堂》：虽说为了生活他得走街串巷，跟各种各样的人打交道，可他从来没跟人动过手。',
            'example': '小贩们走街串巷，到处叫卖。',
            'abbreviation': 'zjcx',
            'source': 'manual'
        }
    ]

def normalize_idiom(idiom: Dict, source: str) -> Dict:
    """标准化成语数据格式"""
    normalized = {
        'word': idiom.get('word', ''),
        'pinyin': idiom.get('pinyin', ''),
        'explanation': idiom.get('explanation', ''),
        'derivation': idiom.get('derivation', ''),
        'example': idiom.get('example', ''),
        'abbreviation': idiom.get('abbreviation', ''),
        'source': source
    }
    return normalized

def merge_idioms() -> List[Dict]:
    """合并所有数据源"""
    print("🔄 开始合并数据集...")
    
    # 1. 加载所有数据源
    print("\n📥 加载数据源...")
    original = load_original_idioms()
    print(f"  ✓ 原始数据集 (chinese-xinhua): {len(original)} 条")
    
    crazywhale = load_crazywhale_idioms()
    print(f"  ✓ crazywhalecc数据集: {len(crazywhale)} 条")
    
    thuocl = load_thuocl_idioms()
    print(f"  ✓ THUOCL数据集: {len(thuocl)} 条")
    
    chengyujielong = load_chengyujielong_idioms()
    print(f"  ✓ 成语接龙数据集: {len(chengyujielong)} 条")
    
    manual = add_manual_idioms()
    print(f"  ✓ 手动添加: {len(manual)} 条")
    
    # 2. 使用字典去重（以 word 为键）
    print("\n🔨 合并并去重...")
    merged_dict: Dict[str, Dict] = {}
    
    # 优先级：原始数据 > crazywhale > 成语接龙 > THUOCL > 手动
    # 但手动添加的一定会加入
    
    # 先加载原始数据
    for item in original:
        word = item.get('word')
        if word:
            merged_dict[word] = normalize_idiom(item, 'chinese-xinhua')
    
    # 添加 crazywhale 中不存在的
    added_from_crazywhale = 0
    for item in crazywhale:
        word = item.get('word')
        if word and word not in merged_dict:
            merged_dict[word] = normalize_idiom(item, 'crazywhalecc')
            added_from_crazywhale += 1
    print(f"  ✓ 从 crazywhalecc 新增: {added_from_crazywhale} 条")
    
    # 添加成语接龙数据集中不存在的
    added_from_chengyujielong = 0
    for item in chengyujielong:
        word = item.get('word')
        if word and word not in merged_dict:
            merged_dict[word] = normalize_idiom(item, 'chengyujielong')
            added_from_chengyujielong += 1
    print(f"  ✓ 从成语接龙 新增: {added_from_chengyujielong} 条")
    
    # 添加 THUOCL 中不存在的（简化版）
    added_from_thuocl = 0
    for item in thuocl:
        word = item.get('word')
        if word and word not in merged_dict:
            # THUOCL 只有词语和频率，创建简化条目
            import pypinyin
            pinyin_list = pypinyin.lazy_pinyin(word)
            pinyin_str = ' '.join(pinyin_list)
            abbr = ''.join([p[0] for p in pinyin_list])
            
            merged_dict[word] = {
                'word': word,
                'pinyin': pinyin_str,
                'explanation': '',
                'derivation': '',
                'example': '',
                'abbreviation': abbr,
                'source': 'THUOCL',
                'frequency': item.get('frequency', 0)
            }
            added_from_thuocl += 1
    print(f"  ✓ 从 THUOCL 新增: {added_from_thuocl} 条")
    
    # 强制添加手动条目
    added_manual = 0
    for item in manual:
        word = item.get('word')
        if word:
            if word in merged_dict:
                # 更新现有条目，保留更详细的信息
                merged_dict[word].update({k: v for k, v in item.items() if v})
            else:
                merged_dict[word] = item
                added_manual += 1
    print(f"  ✓ 手动添加新条目: {added_manual} 条")
    
    # 3. 转换为列表
    merged_list = list(merged_dict.values())
    
    print(f"\n📊 合并结果:")
    print(f"  总计: {len(merged_list)} 条成语")
    print(f"  相比原数据集增加: {len(merged_list) - len(original)} 条")
    
    return merged_list

def verify_critical_idioms(merged: List[Dict]) -> bool:
    """验证关键成语是否存在"""
    print("\n✅ 验证关键成语...")
    critical_words = ['扬名立万', '走街串巷']
    
    word_set = {item['word'] for item in merged}
    all_found = True
    
    for word in critical_words:
        if word in word_set:
            print(f"  ✓ 找到: {word}")
        else:
            print(f"  ✗ 缺失: {word}")
            all_found = False
    
    return all_found

def save_merged_data(merged: List[Dict]):
    """保存合并后的数据"""
    output_path = Path(__file__).parent.parent / 'data' / 'raw' / 'idiom_merged.json'
    
    # 排序（按拼音或词语）
    merged_sorted = sorted(merged, key=lambda x: x.get('word', ''))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_sorted, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存合并数据到: {output_path}")
    print(f"   文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

def main():
    print("=" * 60)
    print("中文成语数据集合并工具")
    print("=" * 60)
    
    try:
        # 合并数据
        merged = merge_idioms()
        
        # 验证关键词
        verification_passed = verify_critical_idioms(merged)
        
        if not verification_passed:
            print("\n⚠️  警告：部分关键成语验证失败！")
        
        # 保存数据
        save_merged_data(merged)
        
        print("\n" + "=" * 60)
        print("✨ 合并完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
