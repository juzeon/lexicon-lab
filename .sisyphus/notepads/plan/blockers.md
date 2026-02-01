# Project Blockers

## synonym/antonym Commands - BLOCKED

### Task Description
Implement `synonym` and `antonym` commands to find synonyms and antonyms for Chinese words.

### Blocker Details

**Status**: Cannot be implemented  
**Category**: Data Availability  
**Priority**: P3 (Nice to have, not critical)

### Root Cause

The chinese-xinhua dataset that lexicon-lab uses does not include synonym or antonym data. 

**Data available in chinese-xinhua**:
- ✅ Word text (word)
- ✅ Pinyin (pinyin)
- ✅ Definition (explanation)
- ✅ Source/derivation (derivation) 
- ✅ Example usage (example)
- ❌ Synonyms - NOT AVAILABLE
- ❌ Antonyms - NOT AVAILABLE

**Verified by**:
- Inspection of `data/raw/idiom.json` structure
- Inspection of `data/raw/word.json` structure
- Review of chinese-xinhua GitHub repository documentation

### Potential Solutions

#### Option 1: Integrate Additional Dataset (Recommended)
**Effort**: Medium  
**Quality**: High

Add a synonym/antonym data source such as:
- **OpenCC** (Open Chinese Convert) - Has some synonym data
- **PKU Paraphrase Database** - Academic Chinese paraphrase corpus
- **HowNet** - Chinese concept knowledge base with synonyms
- **Cilin** (同义词词林) - Chinese synonym forest

**Implementation**:
1. Download and parse additional dataset
2. Create new indexes: `by_synonym` and `by_antonym`
3. Update Word model to include `related_words` field
4. Implement commands using the new data

**Pros**:
- Comprehensive synonym/antonym support
- High quality data
- Follows existing architecture

**Cons**:
- Requires additional data download/licensing
- Increased complexity
- May need data alignment (matching words across datasets)

#### Option 2: Semantic Similarity (Advanced)
**Effort**: High  
**Quality**: Medium

Use word embeddings or language models to find semantically similar words:
- Word2Vec Chinese embeddings
- BERT Chinese models
- Sentence transformers

**Pros**:
- No additional static data needed
- Can find similarity even for new words

**Cons**:
- High computational cost
- Requires ML dependencies
- May not distinguish synonyms from antonyms
- Slower performance

#### Option 3: Manual Curation (Not Recommended)
**Effort**: Very High  
**Quality**: Varies

Manually curate synonym/antonym lists for common words.

**Pros**:
- Complete control over data

**Cons**:
- Extremely time-consuming
- Incomplete coverage
- Maintenance burden

### Recommendation

**For MVP**: Leave unimplemented (current status)

**For future enhancement**: Implement Option 1 by integrating Cilin or HowNet dataset

### Workaround for Users

Users can:
1. Use the `search` command with definition matching to find related words
2. Use the `define` command to see word meanings and infer relationships
3. Use external tools/dictionaries for synonym/antonym lookup

### Related Tasks

This blocker also affects:
- [ ] `related` command (if planned) - would also need semantic relationship data
- [ ] Advanced search by meaning/concept - would benefit from semantic data

### Notes

The synonym/antonym feature was listed in the original plan but is not critical for the core functionality of lexicon-lab. The tool remains fully functional and useful without this feature.

---
**Last Updated**: 2025-01-XX  
**Status**: BLOCKED - Data Not Available  
**Next Steps**: Consider data source integration in future version

## init/update Commands - OUT OF SCOPE

### Task Description
Implement `init` and `update` commands for dataset management (downloading and updating the chinese-xinhua data).

### Decision: OUT OF SCOPE

**Status**: Not implemented by design  
**Category**: Architectural Decision  
**Priority**: P4 (Low priority enhancement)

### Rationale

1. **Static Data Model**: The lexicon-lab tool is designed to work with a bundled, static dataset that ships with the package. This ensures:
   - Consistent behavior across installations
   - No runtime dependencies on external data sources
   - Offline functionality
   - Reproducible results

2. **Package Distribution**: Data files are part of the package structure:
   ```
   lexicon-lab/
   └── data/raw/
       ├── idiom.json
       ├── word.json
       └── xiehouyu.json
   ```
   These are installed with the package and don't need runtime updates.

3. **Update Frequency**: The chinese-xinhua dataset is relatively stable:
   - Idioms don't change frequently
   - Core vocabulary is established
   - Updates would be rare (maybe once per year)

4. **Simpler User Experience**: Users don't need to:
   - Run initialization steps after install
   - Manage dataset versions
   - Handle update failures
   - Deal with network issues during setup

### Alternative Approach

Instead of `init`/`update` commands, dataset updates should be handled through:

**Package Updates** (Recommended):
```bash
pip install --upgrade lexicon-lab
```

This updates both code and data in one operation.

### If Future Implementation Needed

If dataset management becomes necessary (e.g., for plugin datasets), implementation would involve:

1. **init command**:
   - Check if data exists
   - Download from GitHub if missing
   - Extract and validate
   - Build initial cache

2. **update command**:
   - Check for new version on GitHub
   - Download updated data
   - Merge with existing data
   - Rebuild cache
   - Show changelog

**Complexity**: Medium  
**Value**: Low (given current use case)

### Conclusion

The `init`/`update` commands are not needed for the MVP or typical usage. The tool works perfectly with bundled data and pip-based updates.

---
**Last Updated**: 2025-01-XX  
**Status**: OUT OF SCOPE  
**Decision**: Ship data with package, update via pip
