# Process Notes

## Text preprocessing end goal

Want to have:

* **orig**: original string
* **origrc**: list of tuples [(row1, col1), (row2, col2), ...] for each char in orig
* **proc**: processed string ready for matching
* **procmap**: list of corresponding indices in orig for each char in proc
  - will include preceding character's index for e.g. newly inserted chars

FIXME eventually, may want to track start + end values in procmap

The **procmap** pointers to the index in the **orig** string are tracked for several reasons:

1. using the corresponding portion of the **orig** string when processing regular expressions in `<alt>` tags;
2. on errors, being able to communicate back to the user or caller the original position of the match failure; and
3. being able to show (via UI or otherwise) which row/column corresponds to a location in the match, via procmap => origrc

Preprocessing for **proc** should involve accounting for:

* _comments_: remove all comment indicators _at the start of a line_
* _capitalization_: change all characters to lowercase
* _separators_: remove all repeating (3+ times) non-letter characters
* _whitespace_: collapse all consecutive whitespace to a single blank space
* _hyphens_: change all dashes, etc. to a single hyphen (`-`)
* _quotes_: change all double quote marks, etc. to a single quote (`'`)
* _copyright symbol_: replace all `©` symbols with `(c)`
* _http protocol_: replace all `http://` with `https://`
* _varietal words_: replace all equivalent words with the first option for each

FIXME things not fully handled above:

* _comment indicators_: consider whether we should be removing _trailing_ indicators as well, e.g. `*/` for C
* _copyright symbol_: guidelines says to treat `©`, `(c)` and `Copyright` as equivalent, but simple substitution likely doesn't work here. `(c)` can be a list bullet and `Copyright` appears for lots of other non-copyright-notice reasons.

## Text preprocessing steps

### Step 1: Create original chars mapping index

For each character in the line-split full text string, create a list of length equal to the length of the text string.
Each item in the list is a tuple, mapping the corresponding character in the original text string to (line, column) of its location.
Walk through the list of lines from 1(a), adding these mappings.
Remember to include a newline at the end of each line _other than_ the last one.

Result from step 1: **origrc** contains tuples with orig row and orig col

### Step 2: Replace comment characters

In a copy of the **orig** string (**proc**), replace comment characters at the start of any line with an equivalent number of blank space characters.

No adjustment to **procmap** should be required.

FIXME consider whether to attempt comment removal at all, or whether to require user / caller to clean comment markers themselves.

FIXME note language in guideline referring to a comment indicator "which occurs at the beginning of _each_ line in a matchable section".

### Step 3: Convert to lowercase

Convert all letter characters in the **proc** string to lowercase.

This conversion _MAY_ result in changing the length of the string!
See, e.g., [Unicode Standard Annex #21: Case Mappings](https://www.unicode.org/reports/tr21/tr21-5.html):

> "For example, the German character U+00DF "ß" _small letter sharp s_ expands when uppercased to the sequence of two characters "SS". This also occurs where there is no precomposed character corresponding to a case mapping, such as with U+0149 "ŉ" _latin small letter n preceded by apostrophe_."

Note that the example above occurs when going from _lowercase_ to _uppercase_.
In the other direction, there is at least one example where converting from _uppercase_ to _lowercase_ results in a longer string: "İ", see https://stackoverflow.com/questions/28683805/is-there-a-unicode-string-which-gets-longer-when-converted-to-lowercase.
Testing in Python confirms that `"İ".lower()` increases the string size from 1 character to 2.

Based on https://stackoverflow.com/questions/28695245/can-a-string-ever-get-shorter-when-converted-to-upper-lowercase, it appears that calling `str.lower()` on a string in CPython should never result in it getting _shorter_, so I'm not handling or testing for that case at the moment.

So, this conversion should go character-by-character, and adjust the character location mapping in **procmap** as needed.

### Step 4: Convert repeating characters

For each conversion step, the string length may change; so the conversion should adjust the character location mapping in **procmap** as needed.

#### Step 4(a): Remove separators

Remove all repeating (3+ times) non-letter characters.

Note that this step needs to occur before converting whitespace, because it may often lead to multiple preceding and subsequent space characters becoming adjacent.

For now, remove only those that are on their own line (with optional non-`\n` whitespace before or after).
Removing separators mid-lines with other content causes conflicts with step 4(c) below (converting hyphen-like characters).

FIXME consider whether this should be limited to repeating non-letter characters that are, e.g., on their own line; or surrounded on both sides by whitespace; etc. If removing only those on their own line, may want to process this step earlier, e.g. in Step 2 along with removing comment indicators.

FIXME assume that "non-letter character" does _not_ include numbers, or periods (since "..." should not get removed). Will not remove repeating letters, numbers, or periods.

FIXME also consider whether this rule should apply to whitespace characters themselves?

#### Step 4(b): Convert whitespace

Change all consecutive whitespace characters, including newlines, to a single blank space.

#### Step 4(c): Convert hyphen-like characters

Change all hyphens, dashes, en dashes, em dashes, and other variants to a single hyphen-minus (`-`, U+002D).

Use cfg.combineHyphens to determine whether multiple adjacent hyphen-like objects should be combined into a single hyphen (if True), or remain as multiple separate hyphens (if False).

FIXME determine what other variants this may include.

Reference: https://jkorpela.fi/dashes.html

#### Step 4(d): Convert quotes

Change all variation of quotations (single, double, curly, etc.), including a series of multiple quotes, to a single non-smart quote character (`'`).

FIXME determine whether multiple quote marks should be kept as separate instead of merged.

FIXME determine what other variants this may include.

Reference: https://hexdocs.pm/ex_unicode/Unicode.Category.QuoteMarks.html

### Step 5: Convert word and character alternative options

For each conversion step, the string length may change; so the conversion should adjust the character location mapping in **procmap** as needed.

#### Step 5(a): Convert copyright symbols

Change all instances of `©` to `(c)`.

Note that this does _not_ currently handle equivalence of `(c)` and the word `Copyright`.
I am hesitant to merge `(c)` and `Copyright`, since `(c)` may signal a list item bullet and `Copyright` will appear as a word in lots of places other than copyright notices.
In any case, this should rarely be an issue for matching purposes outside of `<copyrightText>` tags, which are allowed to match to any content anyway.

#### Step 5(b): Convert http protocol

Change all instances of `http://` to `https://`.

#### Step 5(c): Convert varietal words

First, convert the [equivalent words file](https://spdx.org/licenses/equivalentwords.txt) to a list of tuples `[(found1, replace1), (found2, replace2), ...]`.
Note the special handling for "sublicense" variants; all should be converted to "sublicense".

For each successive non-whitespace portion of the string, check for the presence of any of the `foundN` words.
If found, replace them with the equivalent `replaceN` alternative, adjusting the character location mapping as needed.

Needs to match words on boundaries; put differently, since "fulfill" contains its variant "fulfil", this should NOT be converted or else it would end up as "fulfilll".
Equivalent words should only be replaced where the preceding and following characters are non-letter characters.

FIXME consider how to handle changes to the equivalent words file over time.
Note that the equivalentwords.txt file has been modified to handle the "sublicense" variants.

## Helpers

### proc text replacement helper

Call with:
  - old text start index
  - old text length (number of chars) to replace
  - new text to insert

Performs the following steps:
  - removes old text portion from proc
  - replaces it with new text
  - updates procmap for these and all subsequent entries
  - returns index of next character _not_ replaced

### proc text replace-all helper

Call with:
  - regex for what to find
  - function (which takes an re.Match object) for what to replace it with

Performs the following steps:
  - re.search() for regex in proc string
  - if None, done
  - if not None:
    - call arg function with Match to get replacement text
    - call `_helperReplace` to replace matched text
    - loop back to beginning for new re.search() beginning from next non-replaced character, as returned by `_helperReplace`
