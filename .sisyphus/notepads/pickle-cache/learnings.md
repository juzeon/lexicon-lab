# Pickle Caching Implementation - Learnings

## Implementation Summary

Successfully implemented pickle caching in `lexicon/search.py` to dramatically improve startup times.

## Performance Results

- **First load (JSON → cache)**: ~2.6s
- **Subsequent loads (cache hit)**: ~0.2s
- **Speedup**: ~13x faster on cache hits
- **Cache size**: ~24MB (for 61,069 words)

## Key Implementation Details

### 1. Imports Added
- `import hashlib` - for MD5 hash calculation
- `import pickle` - for serialization/deserialization

### 2. Class Constants
```python
CACHE_DIR = Path.home() / ".cache" / "lexicon-lab"
CACHE_FILE = CACHE_DIR / "index.pkl"
```
- Uses XDG Base Directory standard (`~/.cache/`)
- Single cache file stores both words and index

### 3. Cache Invalidation Strategy
- **MD5 hash** of all 3 data files (idiom.json, word.json, xiehouyu.json)
- Hash recalculated on each init and compared to cached hash
- Auto-invalidates when ANY data file changes
- Stored alongside words/index in cache dict

### 4. Three Helper Methods

#### `_calculate_data_hash()`
- Reads all 3 data files in binary mode
- Concatenates them into single MD5 hash
- Handles missing files gracefully

#### `_load_from_cache()`
- Checks cache file existence first (fast fail)
- Loads pickle data with exception handling
- Validates hash matches before accepting cache
- Returns boolean indicating success
- Falls back to JSON on any error (corrupted pickle, hash mismatch, etc.)

#### `_save_to_cache()`
- Creates cache directory with `mkdir(parents=True, exist_ok=True)`
- Stores dict with: `data_hash`, `words`, `index`
- Gracefully handles failures (doesn't crash if cache write fails)
- Uses `logger.warning()` for non-critical errors

### 5. New __init__ Flow
1. Check if cache exists and is valid
   - If YES: load and return (~0.2s)
   - If NO: continue to step 2
2. Load data from JSON files (~1.5s)
3. Build index (~0.9s)
4. Save to cache for next time (~0.2s)

## Error Handling

Tested and verified:
- ✅ Missing cache file → Falls back to JSON
- ✅ Corrupted pickle file → Falls back to JSON  
- ✅ Cache directory doesn't exist → Creates automatically
- ✅ Cache save fails → Logs warning, continues normally
- ✅ Data file changes → Cache invalidates automatically

## Logging Messages

Cache hits/misses are logged with INFO level:
- Cache hit: `"Cache hit: loaded 61069 words from cache"`
- Cache miss (no file): DEBUG level
- Cache invalidated: INFO level
- Cache load failures: WARNING level

## Design Decisions

1. **Pickle vs other formats**: Pickle chosen because it preserves Python objects exactly (Word objects, LexiconIndex)
2. **MD5 hash vs modification time**: MD5 is more reliable (handles file system quirks)
3. **Combined words + index**: Simpler than separate caches, one file to invalidate
4. **~/.cache/ location**: Follows XDG standards, user-specific, easy to clear
5. **Graceful degradation**: Cache failures never crash - always fallback to JSON

## Testing Results

All scenarios verified working:
1. First init with cache creation: ✅
2. Second init loading from cache: ✅
3. Cache hit logging: ✅
4. Data file modification triggers invalidation: ✅
5. Corrupted cache file fallback: ✅
6. Same data loaded both ways: ✅

## Notes for Future

- Cache is currently ~24MB (reasonable size)
- Could add cache clear command via CLI
- Could add cache statistics command
- Consider version field in cache dict for forward compatibility
