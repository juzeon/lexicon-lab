#!/bin/bash

echo "=== Testing Regex Quantifiers in Pinyin Mode ==="
echo ""

echo "1. Testing .{2} (exactly 2 characters):"
python lexicon/cli.py search --regex "^zuoci.{2}$" -p -h -L 3
echo ""

echo "2. Testing .{3} (exactly 3 characters):"
python lexicon/cli.py search --regex "^yi.{3}$" -p -L 3
echo ""

echo "3. Testing .{1,3} (1 to 3 characters):"
python lexicon/cli.py search --regex "^tian.{1,3}$" -p -L 5
echo ""

echo "4. Testing .{2,} (2 or more characters):"
python lexicon/cli.py search --regex "^xin.{2,}$" -p -L 5
echo ""

echo "5. Testing .{,2} (0 to 2 characters):"
python lexicon/cli.py search --regex "^xin.{,2}$" -p -L 5
echo ""

echo "6. Testing .{0,1} (optional 0 or 1 character):"
python lexicon/cli.py search --regex "^shu.{0,1}$" -p -L 5
echo ""

echo "7. Comparing .. vs .{2}:"
echo "   Using .. :"
python lexicon/cli.py search --regex "^zuoci..$" -p -h -L 2
echo "   Using .{2}:"
python lexicon/cli.py search --regex "^zuoci.{2}$" -p -h -L 2
echo ""

echo "=== All tests completed ==="
