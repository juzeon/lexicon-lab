#!/usr/bin/env python3
"""
处理成语接龙数据集
将爬取的 CSV 数据转换为 JSON 格式，与现有数据集兼容
"""

import json
from pathlib import Path
import pandas as pd
import pypinyin

def process_chengyujielong_data():
    """处理成语接龙数据集"""
    print("=" * 60)
    print("处理成语接龙数据集")
    print("=" * 60)
    print()
    
    # 读取爬取的数据
    csv_path = Path(__file__).parent.parent / 'data' / 'sources' / 'chinese_chengyujielong' / 'data' / 'cym3.csv'
    print(f"📥 读取数据: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"  ✓ 读取 {len(df)} 条成语")
    print()
    
    # 转换为统一格式
    print("🔨 转换数据格式...")
    idioms = []
    
    for idx, row in df.iterrows():
        chengyu = row['成语']
        
        # 使用 pypinyin 生成拼音
        pinyin_list = pypinyin.lazy_pinyin(chengyu)
        pinyin_str = ' '.join(pinyin_list)
        abbr = ''.join([p[0] for p in pinyin_list])
        
        # 创建数据条目
        idiom_entry = {
            'word': chengyu,
            'pinyin': pinyin_str,
            'abbreviation': abbr,
            'explanation': '',  # 第一阶段没有详细信息
            'derivation': '',
            'example': '',
            'source': 'chengyujielong'
        }
        
        idioms.append(idiom_entry)
        
        # 显示进度
        if (idx + 1) % 5000 == 0:
            print(f"  处理进度: {idx + 1}/{len(df)}")
    
    print(f"  ✓ 完成转换 {len(idioms)} 条成语")
    print()
    
    # 保存为 JSON
    output_path = Path(__file__).parent.parent / 'data' / 'sources' / 'chengyujielong_idioms.json'
    print(f"💾 保存数据: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(idioms, f, ensure_ascii=False, indent=2)
    
    file_size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"  ✓ 文件大小: {file_size_mb:.2f} MB")
    print()
    
    # 显示示例数据
    print("📊 示例数据:")
    for i in range(min(5, len(idioms))):
        print(f"  {i+1}. {idioms[i]['word']} ({idioms[i]['pinyin']}) - {idioms[i]['abbreviation']}")
    print()
    
    # 统计信息
    print("📈 数据统计:")
    lengths = {}
    for idiom in idioms:
        length = len(idiom['word'])
        lengths[length] = lengths.get(length, 0) + 1
    
    for length in sorted(lengths.keys()):
        print(f"  {length}字成语: {lengths[length]} 条")
    print()
    
    print("=" * 60)
    print("✨ 处理完成！")
    print("=" * 60)
    
    return idioms

if __name__ == '__main__':
    try:
        process_chengyujielong_data()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
