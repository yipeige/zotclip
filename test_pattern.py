"""Test script to verify Zotero pattern matching."""

import re

# Test data from user's example
test_cases = [
    # Original example with quotes
    '"loss-free balance routing" ([Team et al., 2025, p. 2](zotero://select/library/items/UVG6GBGT)) ([pdf](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L))',

    # With curly quotes
    '"loss-free balance routing" ([Team et al., 2025, p. 2](zotero://select/library/items/UVG6GBGT)) ([pdf](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L))',

    # Variations with different spacing
    '"loss-free balance routing"([Team et al., 2025, p. 2](zotero://select/library/items/UVG6GBGT))([pdf](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L))',

    # Without quotes
    'loss-free balance routing ([Team et al., 2025, p. 2](zotero://select/library/items/UVG6GBGT)) ([pdf](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L))',

    # Non-Zotero content (should not match)
    'This is just plain text',
    'Another [link](https://example.com)',
]

# Current pattern
ZOTERO_PATTERN = re.compile(
    r'^"?([^"\n]+?)"?\s*\(\[.*?\]\(.*?\)\)\s*\(\[.*?\]\((.+?)\)\)$',
    re.DOTALL
)

# Pattern to strip surrounding quotes
QUOTES_PATTERN = re.compile(r'^["""''](.+?)["""'']$')

def strip_quotes(title):
    """Strip surrounding quotes from title."""
    match = QUOTES_PATTERN.match(title)
    if match:
        return match.group(1)
    return title

print("Testing Zotero pattern matching:\n")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    match = ZOTERO_PATTERN.match(test)
    print(f"\nTest Case {i}:")
    print(f"Input: {test[:80]}...")
    print(f"Match: {bool(match)}")

    if match:
        title = match.group(1).strip()
        pdf_link = match.group(2).strip()
        print(f"  Raw Title: {title}")

        # Strip quotes
        clean_title = strip_quotes(title)
        if clean_title != title:
            print(f"  Clean Title: {clean_title} (quotes removed)")

        print(f"  PDF Link: {pdf_link}")

        # Show output in both modes
        print(f"  Plain Text Mode: {clean_title}")
        print(f"  Markdown Mode: [{clean_title}]({pdf_link})")

print("\n" + "=" * 80)
