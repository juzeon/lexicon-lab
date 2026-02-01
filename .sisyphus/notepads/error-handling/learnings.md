# Error Handling Implementation - Learnings

## Overview
Comprehensive error handling was added to all CLI commands in `lexicon/cli.py` to make the tool more robust and user-friendly.

## Key Changes Made

### 1. Global Error Handling Initialization
- Added `get_search_engine()` function with proper error handling for data loading
- Catches `FileNotFoundError` when data files are missing
- Provides clear error messages when no words are loaded
- Handles initialization exceptions gracefully

### 2. Search Command Enhancements
- Validates `--limit` parameter (must be > 0)
- Catches `ValueError` for invalid search parameters
- Shows "未找到匹配的词语" (No matching words found) instead of empty output
- Added safety check for `word.pinyin` before using it
- Wrapped entire command in try-except block

### 3. Chain Command Improvements
- Validates start character is not empty and is single character only
- Validates count parameter is > 0
- Checks if starting character has any idioms before proceeding
- Handles errors during follower lookup without breaking the chain
- Shows step-specific error information if chain breaks mid-process
- Uses exit code 0 for "no idioms found" (not an error, expected behavior)
- Provides different messages for:
  - "无法找到从 '{start}' 开始的成语" - No idioms with starting character
  - "链断了！找不到以「{char}」开头的成语" - Chain breaks during generation
  - "链断了！没有可选的成语" - No suitable successor idioms

### 4. Define Command Improvements
- Validates word input is not empty
- Trims whitespace from input
- Shows "词语 '{word}' 不存在" instead of "❌ 没有找到词语"
- Catches exceptions during search operation
- Proper error logging for debugging

### 5. Random Word Command Improvements
- Validates length parameter if provided (must be > 0)
- Shows "未找到匹配的词语" with helpful tip to adjust search conditions
- Better error handling for random selection
- Graceful exit when no candidates match criteria

### 6. Stats Command Improvements
- Validates engine and index are properly initialized
- Checks if words list is non-empty
- Validates by_category data
- Only shows frequency data if available
- Handles empty frequency lists gracefully

### 7. Freq Command Improvements
- Validates limit parameter (must be > 0)
- Validates position parameter is one of "start", "end", "all"
- Checks if index is initialized
- Validates char_freq object exists before using
- Shows "未找到任何字频数据" if no frequency data available

## Error Message Patterns

### Chinese Error Messages (User-Friendly)
All error messages follow these patterns:

**Data Loading Errors:**
- "❌ 错误：未找到任何词语数据"
- "❌ 错误：找不到数据文件"

**Validation Errors:**
- "❌ 错误：--limit 必须大于 0"
- "❌ 错误：词语不能为空"
- "❌ 错误：无效的位置参数: {value}"

**Not Found (No Error):**
- "未找到匹配的词语"
- "词语 '{word}' 不存在"
- "无法找到从 '{char}' 开始的成语"

**Warnings (Chain Breaking):**
- "⚠️  链断了！找不到以「{char}」开头的成语"
- "⚠️  链断了！没有可选的成语"

## Error Handling Patterns Used

### 1. Input Validation
```python
if limit <= 0:
    typer.echo("❌ 错误：--limit 必须大于 0", err=True)
    raise typer.Exit(code=1)
```

### 2. Exception Wrapping
```python
try:
    engine = get_search_engine()
    # ... command logic
except typer.Exit:
    raise  # Re-raise typer exits
except Exception as e:
    typer.echo(f"❌ 错误：...", err=True)
    logger.exception("...")
    raise typer.Exit(code=1)
```

### 3. Graceful No-Results Handling
```python
if not results:
    typer.echo("未找到匹配的词语")
    return  # Exit cleanly, exit code 0
```

### 4. Optional Data Handling
```python
if top_5_first:
    typer.echo("\n   最常见的首字 (Top 5):")
    for char, count in top_5_first:
        typer.echo(f"      {char}: {count}")
```

## Testing Results

All commands tested successfully:

✅ **search** - Valid input works, empty results handled, invalid limit caught
✅ **chain** - Valid chains work, invalid chars caught, no idioms message shown
✅ **define** - Valid words shown, non-existent words reported, empty input rejected
✅ **random-word** - Valid results returned, no matches message shown with hint
✅ **stats** - Statistics displayed correctly
✅ **freq** - Valid positions work, invalid positions rejected, invalid limits caught

## Best Practices Implemented

1. **User-Friendly Messages**: All errors and results shown in Chinese
2. **Consistent Error Format**: "❌ 错误：..." for critical errors
3. **Helpful Tips**: Suggestions when no results found (e.g., "提示：尝试调整搜索条件")
4. **Exit Code Conventions**: 
   - Exit code 1 for errors
   - Exit code 0 for clean exits (including "not found" cases)
5. **Logging**: All exceptions logged for debugging
6. **stderr for Errors**: Error messages sent to stderr using `err=True`
7. **No Crashes**: Program never crashes, always shows helpful message
8. **Data Validation**: All user inputs validated before use

## Future Improvements

1. Could add regex validation for complex patterns before search
2. Could provide suggestions for typos in word lookups
3. Could cache chain generation results for performance
4. Could add command-line help with error examples
