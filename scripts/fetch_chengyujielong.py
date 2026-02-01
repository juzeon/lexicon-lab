#!/usr/bin/env python3
"""
成语接龙数据爬取脚本
从 https://cy.hwxnet.com/ 爬取4万多条成语数据
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
    print("开始爬取成语接龙数据集")
    print("=" * 60)
    print()
    
    # Step 1: Get all chengyu URLs and basic info
    print("📥 第一步：获取所有成语列表...")
    print("   (这将爬取按拼音分类的所有成语)")
    print()
    spider.get_all_chengyu3()
    
    print()
    print("=" * 60)
    
    # Step 2: Parse detail information for each chengyu
    print("📝 第二步：获取每个成语的详细信息...")
    print("   (这可能需要较长时间，因为要爬取每个成语的详情页)")
    print("   ⚠️  预计需要爬取 40000+ 个页面，可能需要数小时")
    print()
    
    user_input = input("是否继续？(y/n): ")
    if user_input.lower() == 'y':
        spider.parse_url3_detail()
        print()
        print("=" * 60)
        print("✨ 爬取完成！")
        print("=" * 60)
        print()
        print("生成的文件：")
        print(f"  - {spider_dir}/data/cym3.csv (成语列表)")
        print(f"  - {spider_dir}/data/cycd.csv (成语详细信息)")
    else:
        print("已取消爬取详细信息")
        print("你可以稍后手动运行 parse_url3_detail()")
    
finally:
    # Restore original directory
    os.chdir(original_dir)
