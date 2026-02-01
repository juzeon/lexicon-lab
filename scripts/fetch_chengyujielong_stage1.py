#!/usr/bin/env python3
"""
成语接龙数据爬取脚本 - 第一阶段
快速获取所有成语列表（约10-15分钟）
"""

import os
import sys
from pathlib import Path

# Add the spider directory to the path
spider_dir = Path(__file__).parent.parent / 'data' / 'sources' / 'chinese_chengyujielong'
sys.path.insert(0, str(spider_dir))

# Change to spider directory so the script's relative paths work
original_dir = os.getcwd()
os.chdir(spider_dir)

try:
    # Import the spider module
    import spider
    
    print("=" * 60)
    print("成语接龙数据集 - 第一阶段爬取")
    print("=" * 60)
    print()
    print("📥 正在获取所有成语列表...")
    print("   来源: https://cy.hwxnet.com/")
    print("   预计时间: 10-15分钟")
    print("   数据量: 约40,000条成语")
    print()
    
    # Step 1: Get all chengyu URLs and basic info
    spider.get_all_chengyu3()
    
    print()
    print("=" * 60)
    print("✨ 第一阶段完成！")
    print("=" * 60)
    print()
    
    # Check if the output file was created
    output_file = Path("data/cym3.csv")
    if output_file.exists():
        import pandas as pd
        df = pd.read_csv(output_file)
        print(f"✓ 成功爬取 {len(df)} 条成语")
        print(f"✓ 文件保存至: {output_file.absolute()}")
        print()
        print("示例数据:")
        print(df.head())
    else:
        print("⚠️  未找到输出文件 data/cym3.csv")
    
    print()
    print("=" * 60)
    print("📝 说明:")
    print("  - 当前已获取成语名称和链接")
    print("  - 如需获取详细信息（拼音、解释、出处等），需运行第二阶段")
    print("  - 第二阶段将爬取每个成语的详情页，需要数小时")
    print("  - 可通过运行 parse_url3_detail() 启动第二阶段")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore original directory
    os.chdir(original_dir)
