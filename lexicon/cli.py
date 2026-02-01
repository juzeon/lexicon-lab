"""Main CLI entry point using typer framework."""

import typer
import random as random_module
import logging
import click
import csv
import json
from typing import Optional, List
from pathlib import Path
from dataclasses import asdict
from lexicon.search import SearchEngine
from lexicon.models import Word

try:
    import orjson
except ImportError:
    orjson = None

app = typer.Typer(help="Lexicon-Lab: A flexible Chinese word search CLI tool")

_search_engine: Optional[SearchEngine] = None

# Set up logging for error tracking
logger = logging.getLogger(__name__)


def get_search_engine() -> SearchEngine:
    """Initialize or return cached SearchEngine instance.
    
    Returns:
        SearchEngine: The global search engine instance
        
    Raises:
        SystemExit: If initialization fails and no data files are found
    """
    global _search_engine
    if _search_engine is None:
        try:
            _search_engine = SearchEngine()
            if not _search_engine.words:
                typer.echo("❌ 错误：未找到任何词语数据", err=True)
                typer.echo("   请确保数据文件存在于 data/raw/ 目录", err=True)
                raise typer.Exit(code=1)
        except FileNotFoundError as e:
            typer.echo(f"❌ 错误：找不到数据文件", err=True)
            typer.echo(f"   {str(e)}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"❌ 错误：无法初始化搜索引擎", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception("Failed to initialize search engine")
            raise typer.Exit(code=1)
    return _search_engine


def _export_results(
    results: list[Word],
    format: str,
    output_file: Optional[Path] = None,
    no_pinyin: bool = False,
    no_definition: bool = False
) -> None:
    """Export search results in specified format.
    
    Supports exporting results to different formats (text, json, csv) and
    optionally writes to a file. If no output file is specified, writes to stdout.
    
    Args:
        results: List of Word objects to export
        format: Output format ('text', 'json', or 'csv')
        output_file: Path to output file, or None for stdout
        no_pinyin: Whether to omit pinyin (text format only)
        no_definition: Whether to omit definition (text format only)
        
    Raises:
        ValueError: If format is not one of the supported formats
        IOError: If file write fails (re-raised as info message to user)
    """
    if format not in ["text", "json", "csv"]:
        raise ValueError(f"不支持的输出格式: {format}。支持的格式: text, json, csv")
    
    if format == "text":
        _export_text(results, output_file, no_pinyin, no_definition)
    elif format == "json":
        _export_json(results, output_file)
    elif format == "csv":
        _export_csv(results, output_file)


def _export_text(
    results: list[Word],
    output_file: Optional[Path] = None,
    no_pinyin: bool = False,
    no_definition: bool = False
) -> None:
    """Export results in text format (same as console output).
    
    Args:
        results: List of Word objects to export
        output_file: Path to output file, or None for stdout
        no_pinyin: Whether to omit pinyin
        no_definition: Whether to omit definition
    """
    lines = []
    lines.append(f"找到 {len(results)} 条结果:\n")
    
    for i, word in enumerate(results, 1):
        line = f"{i}. {word.word}"
        
        if not no_pinyin and word.pinyin:
            line += f" [{word.pinyin}]"
        
        if not no_definition and word.definition:
            line += f" - {word.definition}"
        
        lines.append(line)
    
    output = "\n".join(lines)
    
    if output_file is None:
        typer.echo(output)
    else:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            typer.echo(f"✅ 结果已导出到: {output_file}")
        except IOError as e:
            typer.echo(f"❌ 错误：无法写入文件 {output_file}", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception(f"Failed to write text export to {output_file}")
            raise typer.Exit(code=1)


def _export_json(
    results: list[Word],
    output_file: Optional[Path] = None
) -> None:
    """Export results in JSON format.
    
    Converts Word dataclasses to dictionaries and outputs as JSON array.
    Uses orjson if available for better performance, falls back to json module.
    
    Args:
        results: List of Word objects to export
        output_file: Path to output file, or None for stdout
    """
    # Convert Word objects to dictionaries
    results_dicts = [asdict(word) for word in results]
    
    try:
        # Use orjson if available for better performance, otherwise use json
        if orjson is not None:
            json_output = orjson.dumps(results_dicts, option=orjson.OPT_INDENT_2).decode('utf-8')
        else:
            json_output = json.dumps(results_dicts, ensure_ascii=False, indent=2)
        
        if output_file is None:
            typer.echo(json_output)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            typer.echo(f"✅ 结果已导出到: {output_file}")
    except (IOError, OSError) as e:
        typer.echo(f"❌ 错误：无法写入文件 {output_file}", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception(f"Failed to write JSON export to {output_file}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ 错误：JSON序列化失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("JSON serialization failed")
        raise typer.Exit(code=1)


def _export_csv(
    results: list[Word],
    output_file: Optional[Path] = None
) -> None:
    """Export results in CSV format.
    
    Creates CSV with columns: word, pinyin, definition, category, length
    
    Args:
        results: List of Word objects to export
        output_file: Path to output file, or None for stdout
    """
    try:
        # CSV headers
        fieldnames = ["word", "pinyin", "definition", "category", "length"]
        
        if output_file is None:
            # Write to stdout
            writer = csv.DictWriter(
                click.get_text_stream('stdout'),
                fieldnames=fieldnames,
                quoting=csv.QUOTE_MINIMAL,
                escapechar='\\'
            )
            writer.writeheader()
            for word in results:
                writer.writerow({
                    "word": word.word,
                    "pinyin": word.pinyin or "",
                    "definition": word.definition or "",
                    "category": word.category or "",
                    "length": word.length
                })
        else:
            # Write to file
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    quoting=csv.QUOTE_MINIMAL,
                    escapechar='\\'
                )
                writer.writeheader()
                for word in results:
                    writer.writerow({
                        "word": word.word,
                        "pinyin": word.pinyin or "",
                        "definition": word.definition or "",
                        "category": word.category or "",
                        "length": word.length
                    })
            typer.echo(f"✅ 结果已导出到: {output_file}")
    except IOError as e:
        typer.echo(f"❌ 错误：无法写入文件 {output_file}", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception(f"Failed to write CSV export to {output_file}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ 错误：CSV导出失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("CSV export failed")
        raise typer.Exit(code=1)



@app.command()
def search(
    initials: Optional[str] = typer.Option(None, "-i", "--initials", help="拼音首字母 - Pinyin initials"),
    regex: Optional[str] = typer.Option(None, "-r", "--regex", help="正则表达式 - Regular expression pattern"),
    length: Optional[int] = typer.Option(None, "-l", "--length", help="词语长度 - Word length"),
    category: Optional[str] = typer.Option(None, "-t", "--category", help="类型 - Word category (成语/词语/歇后语)"),
    structure: Optional[str] = typer.Option(None, help="结构 - Structure (AABB/ABAC/etc)"),
    rhyme: Optional[str] = typer.Option(None, help="韵母 - Rhyme/final"),
    tone: Optional[str] = typer.Option(None, help="声调模式 - Tone sequence (1,2,3,4)"),
    enable_pinyin: bool = typer.Option(False, "-p", "--enable-pinyin", help="启用拼音搜索 - Enable pinyin to hanzi expansion (e.g., wan -> 万,玩,晚)"),
    enable_homophone: bool = typer.Option(False, "-h", "--enable-homophone", help="启用谐音搜索 - Enable homophone matching (e.g., wan -> wang)"),
    limit: int = typer.Option(20, "-L", "--limit", help="每页结果数量 (0=不限制) - Results per page (0=unlimited)"),
    page: int = typer.Option(1, "-P", "--page", help="页码 - Page number"),
    no_pinyin: bool = typer.Option(False, "--no-pinyin", help="不显示拼音 - Hide pinyin"),
    no_definition: bool = typer.Option(False, "--no-definition", help="不显示释义 - Hide definition"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径 - Output file path"),
    format: str = typer.Option("text", "--format", "-f", help="输出格式 - Output format (text/json/csv)"),
) -> None:
    try:
        engine = get_search_engine()
        
        # Validate page number
        if page < 1:
            typer.echo("❌ 错误：--page 必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        # limit=0 means unlimited, otherwise must be positive
        if limit < 0:
            typer.echo("❌ 错误：--limit 不能为负数 (使用 0 表示不限制)", err=True)
            raise typer.Exit(code=1)
        
        try:
            results = engine.search(
                pinyin=initials,
                regex=regex,
                length=length,
                category=category,
                structure=structure,
                rhyme=rhyme,
                tone=tone,
                enable_pinyin=enable_pinyin,
                enable_homophone=enable_homophone,
                limit=limit,
                page=page
            )
        except ValueError as e:
            typer.echo(f"❌ 错误：无效的搜索参数", err=True)
            typer.echo(f"   {str(e)}", err=True)
            raise typer.Exit(code=1)
        
        if not results:
            if not output:
                typer.echo("未找到匹配的词语")
            return
        
        _export_results(results, format, output, no_pinyin, no_definition)
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：搜索失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Search command failed")
        raise typer.Exit(code=1)


@app.command()
def chain(start_char: str = typer.Argument(..., help="起始字"), count: int = typer.Option(10, "-c", "--count", help="连接数量")) -> None:
    """成语接龙 - Idiom chain game (find idioms where first char matches last char of previous)."""
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
        
        idioms_with_start = engine.search(regex=f"^{start_char}", category="成语", limit=1)
        if not idioms_with_start:
            typer.echo(f"无法找到从 '{start_char}' 开始的成语")
            raise typer.Exit(code=0)
        
        result_chain = [start_char]
        current_char = start_char
        
        for i in range(count):
            try:
                idioms_with_start = engine.search(regex=f"^{current_char}", category="成语", limit=100)
                
                if not idioms_with_start:
                    typer.echo(f"\n⚠️  链断了！找不到以「{current_char}」开头的成语")
                    break
                
                best_idiom = None
                best_followers_count = 0
                
                for idiom in idioms_with_start:
                    try:
                        followers = engine.search(regex=f"^{idiom.last_char}", category="成语")
                        followers_count = len(followers)
                        
                        if followers_count > best_followers_count:
                            best_followers_count = followers_count
                            best_idiom = idiom
                    except Exception as e:
                        logger.warning(f"Error checking followers for {idiom.word}: {e}")
                        continue
                
                if best_idiom is None:
                    typer.echo(f"\n⚠️  链断了！没有可选的成语")
                    break
                
                result_chain.append(best_idiom.word)
                current_char = best_idiom.last_char
            
            except Exception as e:
                typer.echo(f"\n⚠️  在第 {i+1} 步出错：{str(e)}", err=True)
                logger.warning(f"Error during chain generation at step {i+1}: {e}")
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
            results = engine.search(regex=f"^{word}$")
        except Exception as e:
            typer.echo(f"❌ 错误：搜索失败 - {str(e)}", err=True)
            logger.warning(f"Search failed for word '{word}': {e}")
            raise typer.Exit(code=1)
        
        if not results:
            typer.echo(f"词语 '{word}' 不存在")
            return
        
        matched_word = results[0]
        
        typer.echo(f"\n📖 {matched_word.word}")
        typer.echo(f"   拼音: {matched_word.pinyin}")
        typer.echo(f"   类型: {matched_word.category}")
        
        if matched_word.definition:
            typer.echo(f"   释义: {matched_word.definition}")
        
        if matched_word.source:
            typer.echo(f"   出处: {matched_word.source}")
        
        if matched_word.example:
            typer.echo(f"   例句: {matched_word.example}")
        
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：定义查询失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Define command failed")
        raise typer.Exit(code=1)


@app.command()
def synonym() -> None:
    typer.echo("synonym command - Not implemented yet")


@app.command()
def antonym() -> None:
    typer.echo("antonym command - Not implemented yet")


@app.command()
def random_word(length: Optional[int] = typer.Option(None, "-l", "--length", help="词语长度"), category: Optional[str] = typer.Option(None, "-t", "--category", help="词语类型")) -> None:
    """随机词语 - Pick a random word optionally filtered by length and category."""
    try:
        if length is not None and length <= 0:
            typer.echo("❌ 错误：词语长度必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        candidates = list(range(len(engine.words)))
        
        if length is not None:
            candidates = [idx for idx in candidates if engine.words[idx].length == length]
        
        if category is not None:
            candidates = [idx for idx in candidates if engine.words[idx].category == category]
        
        if not candidates:
            typer.echo("未找到匹配的词语")
            if length is not None or category is not None:
                typer.echo(f"   提示：尝试调整搜索条件")
            return
        
        try:
            selected_idx = random_module.choice(candidates)
            word = engine.words[selected_idx]
        except Exception as e:
            typer.echo(f"❌ 错误：无法选择随机词语", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception("Failed to select random word")
            raise typer.Exit(code=1)
        
        typer.echo(f"\n🎲 {word.word}")
        typer.echo(f"   拼音: {word.pinyin}")
        typer.echo(f"   类型: {word.category}")
        
        if word.definition:
            typer.echo(f"   释义: {word.definition}")
        
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：随机词语失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Random word command failed")
        raise typer.Exit(code=1)


@app.command()
def stats() -> None:
    """显示统计信息 - Show statistics about the lexicon."""
    try:
        engine = get_search_engine()
        
        if not engine.words:
            typer.echo("❌ 错误：没有可用的词语数据", err=True)
            raise typer.Exit(code=1)
        
        index = engine.index
        if not index:
            typer.echo("❌ 错误：索引未正确初始化", err=True)
            raise typer.Exit(code=1)
        
        total_words = len(engine.words)
        
        by_category = {}
        for word in engine.words:
            category = word.category
            by_category[category] = by_category.get(category, 0) + 1
        
        if not by_category:
            typer.echo("❌ 错误：无法统计词语分类", err=True)
            raise typer.Exit(code=1)
        
        typer.echo("\n📊 词库统计：")
        typer.echo(f"   总词语数: {total_words}")
        
        typer.echo("\n   按类型分类:")
        for category, count in sorted(by_category.items()):
            typer.echo(f"      {category}: {count}")
        
        top_5_first = index.char_freq_start.most_common(5)
        if top_5_first:
            typer.echo("\n   最常见的首字 (Top 5):")
            for char, count in top_5_first:
                typer.echo(f"      {char}: {count}")
        
        top_5_last = index.char_freq_end.most_common(5)
        if top_5_last:
            typer.echo("\n   最常见的尾字 (Top 5):")
            for char, count in top_5_last:
                typer.echo(f"      {char}: {count}")
        
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：统计失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Stats command failed")
        raise typer.Exit(code=1)


@app.command()
def quiz(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="类型 (成语/词语/歇后语)"),
    length: Optional[int] = typer.Option(None, "--length", "-l", help="词语长度")
) -> None:
    """猜词游戏 - Word guessing game."""
    try:
        if length is not None and length <= 0:
            typer.echo("❌ 错误：词语长度必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        candidates = list(range(len(engine.words)))
        if length is not None:
            candidates = [idx for idx in candidates if engine.words[idx].length == length]
        if category is not None:
            candidates = [idx for idx in candidates if engine.words[idx].category == category]
        
        if not candidates:
            typer.echo("❌ 错误：未找到匹配的词语")
            if length is not None or category is not None:
                typer.echo("   提示：尝试调整搜索条件")
            raise typer.Exit(code=1)
        
        try:
            selected_idx = random_module.choice(candidates)
            word_obj = engine.words[selected_idx]
        except Exception as e:
            typer.echo(f"❌ 错误：无法选择随机词语", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception("Failed to select random word for quiz")
            raise typer.Exit(code=1)
        
        typer.echo("\n🎯 猜词游戏\n")
        
        answer = word_obj.word
        max_attempts = 3
        attempts = 0
        guessed_correctly = False
        
        if word_obj.definition:
            typer.echo(f"释义: {word_obj.definition}")
        if word_obj.example:
            typer.echo(f"例句: {word_obj.example}")
        typer.echo()
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                user_guess = typer.prompt(f"你的答案 (还有 {max_attempts - attempts + 1} 次机会)", default="")
            except (KeyboardInterrupt, EOFError):
                typer.echo("\n游戏结束")
                raise typer.Exit(code=0)
            
            if not user_guess or len(user_guess.strip()) == 0:
                typer.echo("❌ 答案不能为空，请重新输入\n")
                attempts -= 1
                continue
            
            user_guess = user_guess.strip()
            
            if user_guess == answer:
                guessed_correctly = True
                typer.echo(f"✅ 正确！你用了 {attempts} 次机会猜对了。\n")
                break
            else:
                if attempts < max_attempts:
                    typer.echo(f"❌ 不对！")
                    
                    if attempts == 1:
                        first_char = answer[0]
                        typer.echo(f"   提示: 首字是「{first_char}」")
                    elif attempts == 2:
                        word_length = len(answer)
                        typer.echo(f"   提示: 长度是 {word_length} 字")
                        
                        char_positions = {}
                        for i, char in enumerate(answer):
                            if char not in char_positions:
                                char_positions[char] = []
                            char_positions[char].append(i + 1)
                        
                        repeated_chars = {char: pos for char, pos in char_positions.items() if len(pos) > 1}
                        if repeated_chars:
                            hints = []
                            for char, positions in repeated_chars.items():
                                hints.append(f"「{char}」出现在第 {', '.join(map(str, positions))} 位")
                            typer.echo(f"   提示: {'; '.join(hints)}")
                    
                    typer.echo()
                else:
                    typer.echo(f"❌ 不对！")
                    typer.echo(f"   答案是: {answer}\n")
        
        if not guessed_correctly:
            typer.echo(f"游戏结束！答案是「{answer}」\n")
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：游戏出错", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Quiz command failed")
        raise typer.Exit(code=1)


@app.command()
def fill(
    pattern: str = typer.Argument(..., help="填字模式，使用 ? 表示待填字符 (如: 一?一?)"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="类型 (成语/词语/歇后语)"),
    limit: int = typer.Option(20, "--limit", help="最大结果数量 (0=不限制) - Maximum results (0=unlimited)")
) -> None:
    """填字游戏 - Fill-in-the-blank word game."""
    try:
        if not pattern or len(pattern.strip()) == 0:
            typer.echo("❌ 错误：模式不能为空", err=True)
            raise typer.Exit(code=1)
        
        pattern = pattern.strip()
        
        if "?" not in pattern:
            typer.echo("❌ 错误：模式必须包含至少一个 ? 字符", err=True)
            raise typer.Exit(code=1)
        
        if limit < 0:
            typer.echo("❌ 错误：--limit 不能为负数 (使用 0 表示不限制)", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("?", ".").replace("*", ".*")
        regex_pattern = f"^{regex_pattern}$"
        
        # Search for matching words
        try:
            results = engine.search(
                regex=regex_pattern,
                category=category,
                limit=limit
            )
        except ValueError as e:
            typer.echo(f"❌ 错误：无效的搜索参数", err=True)
            typer.echo(f"   {str(e)}", err=True)
            raise typer.Exit(code=1)
        
        result_count = len(results)
        
        # Case 1: No matches
        if result_count == 0:
            typer.echo("未找到匹配的词语")
            return
        
        # Case 2: Exactly one match
        if result_count == 1:
            word = results[0]
            typer.echo(f"\n✨ 找到答案：{word.word}")
            if word.pinyin:
                typer.echo(f"   拼音: {word.pinyin}")
            if word.definition:
                typer.echo(f"   释义: {word.definition}")
            typer.echo()
            return
        
        # Case 3: 2-10 matches - interactive game
        if 2 <= result_count <= 10:
            typer.echo("\n🎯 填字游戏\n")
            
            # Pick a random word from results
            try:
                selected_idx = random_module.choice(range(len(results)))
                answer_word = results[selected_idx]
            except Exception as e:
                typer.echo(f"❌ 错误：无法选择随机词语", err=True)
                typer.echo(f"   {str(e)}", err=True)
                logger.exception("Failed to select random word for fill game")
                raise typer.Exit(code=1)
            
            answer = answer_word.word
            max_attempts = 2
            attempts = 0
            guessed_correctly = False
            
            # Show pattern and definition
            typer.echo(f"模式: {pattern}")
            if answer_word.definition:
                typer.echo(f"释义: {answer_word.definition}")
            typer.echo()
            
            while attempts < max_attempts:
                attempts += 1
                
                try:
                    user_guess = typer.prompt(f"你的答案 (还有 {max_attempts - attempts + 1} 次机会)", default="")
                except (KeyboardInterrupt, EOFError):
                    typer.echo("\n游戏结束")
                    raise typer.Exit(code=0)
                
                if not user_guess or len(user_guess.strip()) == 0:
                    typer.echo("❌ 答案不能为空，请重新输入\n")
                    attempts -= 1
                    continue
                
                user_guess = user_guess.strip()
                
                if user_guess == answer:
                    guessed_correctly = True
                    typer.echo(f"✅ 正确！\n")
                    break
                else:
                    if attempts < max_attempts:
                        typer.echo(f"❌ 不对！")
                        
                        if attempts == 1:
                            # First hint: show first and last character
                            hint_parts = []
                            if len(answer) > 0:
                                hint_parts.append(f"首字是「{answer[0]}」")
                            if len(answer) > 1:
                                hint_parts.append(f"尾字是「{answer[-1]}」")
                            if hint_parts:
                                typer.echo(f"   提示: {'; '.join(hint_parts)}")
                        
                        typer.echo()
                    else:
                        typer.echo(f"❌ 不对！")
                        typer.echo(f"   答案是: {answer}\n")
            
            if not guessed_correctly:
                typer.echo(f"游戏结束！答案是「{answer}」\n")
            
            return
        
        # Case 4: More than 10 matches - just list them
        typer.echo(f"\n找到 {result_count} 条结果:\n")
        for i, word in enumerate(results, 1):
            line = f"{i}. {word.word}"
            if word.pinyin:
                line += f" [{word.pinyin}]"
            if word.definition:
                line += f" - {word.definition}"
            typer.echo(line)
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：填字游戏失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Fill command failed")
        raise typer.Exit(code=1)


@app.command()
def init() -> None:
    typer.echo("init command - Not implemented yet")


def _is_chinese_character(char: str) -> bool:
    """Check if character is valid Chinese character (CJK)."""
    code_point = ord(char)
    return (
        (0x4E00 <= code_point <= 0x9FFF) or
        (0x3400 <= code_point <= 0x4DBF) or
        (0x20000 <= code_point <= 0x2A6DF) or
        (0x2A700 <= code_point <= 0x2B73F) or
        (0x2B740 <= code_point <= 0x2B81F) or
        (0x2B820 <= code_point <= 0x2CEAF) or
        (0x2CEB0 <= code_point <= 0x2EBEF)
    )


@app.command()
def fly(
    char: str = typer.Argument(..., help="飞花令关键字 (单个汉字)"),
    position: Optional[str] = typer.Option(None, "--position", "-p", help="字符位置 (start/end/any)"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="类型 (成语/词语/歇后语)"),
    length: Optional[int] = typer.Option(None, "--length", "-l", help="词语长度"),
    limit: int = typer.Option(20, "--limit", help="最大结果数量 (0=不限制) - Maximum results (0=unlimited)")
) -> None:
    """飞花令 - Flying Flower word game."""
    try:
        if not char or len(char.strip()) == 0:
            typer.echo("❌ 错误：请输入单个汉字", err=True)
            raise typer.Exit(code=1)
        
        char = char.strip()
        
        if len(char) != 1:
            typer.echo("❌ 错误：请输入单个汉字", err=True)
            raise typer.Exit(code=1)
        
        if not _is_chinese_character(char):
            typer.echo(f"❌ 错误：'{char}' 不是有效的汉字", err=True)
            raise typer.Exit(code=1)
        
        if position is not None:
            position = position.lower()
            if position not in ["start", "end", "any"]:
                typer.echo("❌ 错误：位置参数必须是 start/end/any", err=True)
                raise typer.Exit(code=1)
        
        if limit < 0:
            typer.echo("❌ 错误：--limit 不能为负数 (使用 0 表示不限制)", err=True)
            raise typer.Exit(code=1)
        
        if length is not None and length <= 0:
            typer.echo("❌ 错误：词语长度必须大于 0", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        search_kwargs = {
            "limit": limit,
            "category": category,
            "length": length,
        }
        
        if position == "start":
            search_kwargs["start"] = char
        elif position == "end":
            search_kwargs["end"] = char
        else:
            search_kwargs["contains"] = [char]
        
        try:
            results = engine.search(**search_kwargs)
        except ValueError as e:
            typer.echo(f"❌ 错误：无效的搜索参数", err=True)
            typer.echo(f"   {str(e)}", err=True)
            raise typer.Exit(code=1)
        
        if not results:
            typer.echo("未找到匹配的词语")
            return
        
        result_count = len(results)
        
        if position == "start":
            header = f"找到 {result_count} 条以'{char}'开头的词语"
        elif position == "end":
            header = f"找到 {result_count} 条以'{char}'结尾的词语"
        else:
            header = f"找到 {result_count} 条包含'{char}'的词语"
        
        typer.echo(f"\n{header}:\n")
        
        for i, word in enumerate(results, 1):
            line = f"{i}. {word.word}"
            
            if word.pinyin:
                line += f" [{word.pinyin}]"
            
            if word.definition:
                line += f" - {word.definition}"
            
            typer.echo(line)
        
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：飞花令游戏失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Fly command failed")
        raise typer.Exit(code=1)




@app.command()
def batch(
    input_file: Path = typer.Argument(..., help="输入文件路径"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    format: str = typer.Option("text", "--format", "-f", help="输出格式 (text/json/csv)")
) -> None:
    """批量搜索 - Batch search from file."""
    try:
        # Validate input file
        if not input_file.exists():
            typer.echo("❌ 错误：输入文件不存在", err=True)
            raise typer.Exit(code=1)
        
        if format not in ["text", "json", "csv"]:
            typer.echo(f"❌ 错误：不支持的输出格式: {format}", err=True)
            typer.echo("   支持的格式: text, json, csv", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        
        # Read input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except IOError as e:
            typer.echo(f"❌ 错误：无法读取文件 {input_file}", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception(f"Failed to read input file {input_file}")
            raise typer.Exit(code=1)
        
        # Filter and clean lines
        queries = []
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                queries.append(line)
        
        if not queries:
            typer.echo("❌ 错误：输入文件为空", err=True)
            raise typer.Exit(code=1)
        
        # Process each query
        all_results: dict[str, Word] = {}  # Use dict to deduplicate by word text
        processed_count = 0
        
        for query in queries:
            try:
                results = engine.search(regex=f"^{query}$")
                for word in results:
                    # Deduplicate by word text
                    if word.word not in all_results:
                        all_results[word.word] = word
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                # Continue processing other queries even if one fails
                continue
            processed_count += 1
        
        # Convert dict to list for export
        results_list = list(all_results.values())
        
        # Export results
        try:
            _export_results(results_list, format, output)
            typer.echo(f"\n处理了 {processed_count} 行，找到 {len(results_list)} 条结果")
        except Exception as e:
            typer.echo(f"❌ 错误：导出结果失败", err=True)
            typer.echo(f"   {str(e)}", err=True)
            logger.exception("Failed to export batch results")
            raise typer.Exit(code=1)
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：批量搜索失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Batch command failed")
        raise typer.Exit(code=1)


@app.command()
def freq(
    position: str = typer.Option("all", help="Position: start/end/all"),
    limit: int = typer.Option(20, help="Number of results (0=unlimited)")
) -> None:
    """字频统计 - Show character frequency statistics."""
    try:
        if limit < 0:
            typer.echo("❌ 错误：--limit 不能为负数 (使用 0 表示不限制)", err=True)
            raise typer.Exit(code=1)
        
        engine = get_search_engine()
        index = engine.index
        
        if not index:
            typer.echo("❌ 错误：索引未正确初始化", err=True)
            raise typer.Exit(code=1)
        
        position = position.lower()
        if position not in ["start", "end", "all"]:
            typer.echo(f"❌ 错误：无效的位置参数: {position}", err=True)
            typer.echo("   有效选项: start, end, all", err=True)
            raise typer.Exit(code=1)
        
        if position == "start":
            char_freq = index.char_freq_start
            header = "📊 字频统计 (首字):"
        elif position == "end":
            char_freq = index.char_freq_end
            header = "📊 字频统计 (尾字):"
        else:
            char_freq = index.char_freq_all
            header = "📊 字频统计 (全部):"
        
        if not char_freq:
            typer.echo("❌ 错误：没有字频数据", err=True)
            raise typer.Exit(code=1)
        
        top_chars = char_freq.most_common(limit if limit > 0 else None)
        
        if not top_chars:
            typer.echo("未找到任何字频数据")
            return
        
        typer.echo(f"\n{header}")
        for char, count in top_chars:
            typer.echo(f"   {char}: {count}")
        
        typer.echo()
    
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 错误：字频统计失败", err=True)
        typer.echo(f"   {str(e)}", err=True)
        logger.exception("Freq command failed")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
