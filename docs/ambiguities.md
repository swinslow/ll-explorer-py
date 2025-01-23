# Ambiguities in SPDX Matching Guidelines

## Policy questions

* Purpose and ambiguity:
  - Should the SPDX Matching Guidelines have a single, unambiguous interpretation in order for all tools to apply them uniformly?
  - Or, are they intended as general guidelines, where each tool may implement them differently and reach differing results?

## Technical questions

The following _technical_ questions appear to be ambiguous under the SPDX Matching Guidelines, and may warrant further investigation:

* Regular expressions:
  - Should regular expressions in `<alt>` tags be matched with regards to applying the rest of the Matching Guidelines before evaluation?
  - For example: Should spaces in the regex be evaluated as if they were `\s+`? Should quote marks and dashes in the regex be evaluated as if they were any quotes and any hyphens or dashes?

* Punctuation:
  - Quotes:
    - Should successive quote marks be treated as a single quote? For example, should `''` be interpreted as equivalent to `"`, which would in turn be interpreted as equivalent to `'`?

* Separators:
  - The guideline refers to a "_non-letter_ character repeated 3 or more times to establish a visual separation". Should repeating numbers and periods (e.g. `...`) also be excluded from being ignored?
  - The purpose of "to establish a visual separation" is ambiguous. Would this include:
    - repeats only on their own line?
    - repeats separated from other characters by whitespace?
    - repeats occuring directly adjacent to alphanumeric characters?
  - Presumably should not include ignoring whitespace characters as "_non-letter_ characters"?
    - _Ignoring_ them would lead to treating them as non-existing, rather than the whitespace rule treating as a single white space
    - Perhaps can justify carving them out from the separators rule, because they don't "establish a visual separator"?

## Semantic questions

The following _semantic_ questions relate to issues that appear to be ambiguous, or not necessarily aligned, with actual practice in the SPDX License List:

* Replaceable text:
  - The description mostly refers only to using replaceable text for e.g. names and dates. (There is a reference to using it for "generic term[s]".) However, in the License List XML markups, we use `<alt>` tags for a variety of "not legally substantive" matches. Should the guideline's description be expanded to clarify this usage?
