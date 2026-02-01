# Before & After Comparison

## Command: `define`

### BEFORE
```python
@app.command()
def define(word: str = typer.Argument(..., help="要查询的词语")) -> None:
    """查询词语定义 - Show word definition."""
    engine = get_search_engine()
    
    results = engine.search(pattern=f"^{word}$")
    
    if not results:
        typer.echo(f"❌ 没有找到词语: {word}")
        return
    
    # ... rest of display
```

**Issues:**
- ❌ Shows inconsistent error message
- ❌ Doesn't validate empty input
- ❌ No exception handling
- ❌ Search engine initialization can crash

### AFTER
```python
@app.command()
def define(word: str = typer.Argument(..., help="要查询的词语")) -> None:
    """查询词语定义 - Show word definition."""
    try:
        if not word or len(word.strip()) == 0:
            typer.echo("❌ 错误：词语不能为空", err=True)
            raise typer.Exit(code=1)
        
        word = word.strip()
        
        engine = get_search_engine()
        
        try:
            results = engine.search(pattern=f"^{word}$")
        except Exception as e:
            typer.echo(f"❌ 错误：搜索失败 - {str(e)}", err=True)
            logger.warning(f"Search failed for word '{word}': {e}")
            raise typer.Exit(code=1)
        
        if not results:
            typer.echo(f"词语 '{word}' 不存在")
            return
        
        # ... rest of display
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：定义查询失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Define command failed")
        raise typer.Exit(code=1)
```

**Improvements:**
- ✅ Validates empty input
- ✅ Uses spec-compliant message: "词语 '{word}' 不存在"
- ✅ Handles search exceptions
- ✅ Catches all unexpected errors
- ✅ Logs errors for debugging
- ✅ Never crashes

---

## Command: `chain`

### BEFORE
```python
@app.command()
def chain(start_char: str = typer.Argument(..., help="起始字"), 
          count: int = typer.Option(10, "-c", "--count", help="连接数量")) -> None:
    """成语接龙 - Idiom chain game."""
    engine = get_search_engine()
    
    result_chain = [start_char]
    current_char = start_char
    
    for _ in range(count):
        idioms_with_start = engine.search(start=current_char, category="成语", limit=100)
        
        if not idioms_with_start:
            typer.echo(f"链断了！找不到以「{current_char}」开头的成语")
            break
        
        best_idiom = None
        best_followers_count = 0
        
        for idiom in idioms_with_start:
            followers = engine.search(start=idiom.last_char, category="成语")
            followers_count = len(followers)
            
            if followers_count > best_followers_count:
                best_followers_count = followers_count
                best_idiom = idiom
        
        if best_idiom is None:
            typer.echo(f"链断了！没有可选的成语")
            break
        
        result_chain.append(best_idiom.word)
        current_char = best_idiom.last_char
    
    typer.echo("\n🔗 成语接龙：")
    typer.echo(" → ".join(result_chain))
```

**Issues:**
- ❌ No input validation for start_char
- ❌ No validation for count parameter
- ❌ Doesn't check if starting character has any idioms
- ❌ No error handling for unexpected exceptions
- ❌ Can crash if anything goes wrong

### AFTER
```python
@app.command()
def chain(start_char: str = typer.Argument(..., help="起始字"), 
          count: int = typer.Option(10, "-c", "--count", help="连接数量")) -> None:
    """成语接龙 - Idiom chain game."""
    try:
        if not start_char or len(start_char) == 0:
            typer.echo("❌ 错误：起始字不能为空", err=True)
            raise typer.Exit(code=1)
        
        if len(start_char) > 1:
            typer.echo("❌ 错误：起始字必须是单个字符", err=True)
            raise typer.Exit(code=1)
        
        if count <= 0:
            typer.echo("❌ 错误：连接数量必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        idioms_with_start = engine.search(start=start_char, category="成语", limit=1)
        if not idioms_with_start:
            typer.echo(f"无法找到从 '{start_char}' 开始的成语")
            raise typer.Exit(code=0)
        
        result_chain = [start_char]
        current_char = start_char
        
        for i in range(count):
            try:
                # ... chain generation with error handling
            except Exception as e:
                typer.echo(f"\n⚠️  在第 {i+1} 步出错：{str(e)}", err=True)
                logger.warning(f"Error during chain generation: {e}")
                break
        
        typer.echo("\n🔗 成语接龙：")
        typer.echo(" → ".join(result_chain))
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：成语接龙失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Chain command failed")
        raise typer.Exit(code=1)
```

**Improvements:**
- ✅ Validates start_char is not empty
- ✅ Validates start_char is single character only
- ✅ Validates count > 0
- ✅ Pre-checks if starting character has idioms
- ✅ Uses spec-compliant message: "无法找到从 '{start}' 开始的成语"
- ✅ Handles errors during chain generation
- ✅ Shows step-specific error information
- ✅ Never crashes

---

## Command: `search`

### BEFORE
```python
@app.command()
def search(
    start: Optional[str] = typer.Option(...),
    # ... many options ...
    limit: int = typer.Option(20, "--limit", ...),
    # ... more options ...
) -> None:
    engine = get_search_engine()
    
    results = engine.search(
        # ... all parameters ...
    )
    
    result_count = len(results)
    typer.echo(f"找到 {result_count} 条结果:\n")
    
    for i, word in enumerate(results, 1):
        line = f"{i}. {word.word}"
        
        if not no_pinyin:
            line += f" [{word.pinyin}]"
        
        if not no_definition and word.definition:
            line += f" - {word.definition}"
        
        typer.echo(line)
```

**Issues:**
- ❌ Shows "找到 0 条结果" instead of "未找到匹配的词语"
- ❌ No validation for negative limit
- ❌ Can crash if search engine fails
- ❌ Accesses word.pinyin without checking if it exists

### AFTER
```python
@app.command()
def search(
    # ... same options ...
) -> None:
    try:
        engine = get_search_engine()
        
        if limit <= 0:
            typer.echo("❌ 错误：--limit 必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        try:
            results = engine.search(...)
        except ValueError as e:
            typer.echo(f"❌ 错误：无效的搜索参数", err=True)
            typer.echo(f"   {str(e)}", err=True)
            raise typer.Exit(code=1)
        
        if not results:
            typer.echo("未找到匹配的词语")
            return
        
        result_count = len(results)
        typer.echo(f"找到 {result_count} 条结果:\n")
        
        for i, word in enumerate(results, 1):
            line = f"{i}. {word.word}"
            
            if not no_pinyin and word.pinyin:
                line += f" [{word.pinyin}]"
            
            if not no_definition and word.definition:
                line += f" - {word.definition}"
            
            typer.echo(line)
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：搜索失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Search command failed")
        raise typer.Exit(code=1)
```

**Improvements:**
- ✅ Validates limit > 0
- ✅ Uses spec-compliant message: "未找到匹配的词语"
- ✅ Catches search parameter errors
- ✅ Safely checks word.pinyin before use
- ✅ Comprehensive exception handling
- ✅ Never crashes

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Input Validation | ❌ None | ✅ Comprehensive |
| Error Messages | ❌ Inconsistent | ✅ Spec-compliant & consistent |
| Exception Handling | ❌ Minimal | ✅ Comprehensive try-except |
| Edge Cases | ❌ Many uncovered | ✅ All covered |
| User Experience | ❌ Can crash | ✅ Always shows helpful message |
| Logging | ❌ None | ✅ All errors logged |
| Code Safety | ❌ Unsafe attribute access | ✅ Safe with checks |
| Exit Codes | ❌ Inconsistent | ✅ Proper Unix conventions |
| stderr Usage | ❌ Not used | ✅ All errors to stderr |

