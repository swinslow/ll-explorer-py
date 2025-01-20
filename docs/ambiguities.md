# Ambiguities in SPDX Matching Guidelines

## Technical questions

The following _technical_ questions appear to be ambiguous under the SPDX Matching Guidelines, and may warrant further investigation:

* Regular expressions:
  - Should regular expressions in `<alt>` tags be matched with regards to applying the rest of the Matching Guidelines before evaluation?
  - For example: Should spaces in the regex be evaluated as if they were `\s+`? Should quote marks and dashes in the regex be evaluated as if they were any quotes and any hyphens or dashes?
* Punctuation:
  - Quotes:
    - Should successive quote marks be treated as a single quote? For example, should `''` be interpreted as equivalent to `"`, which would in turn be interpreted as equivalent to `'`?

## Semantic questions

The following _semantic_ questions relate to issues that appear to be ambiguous, or not necessarily aligned, with actual practice in the SPDX License List:

* Replaceable text:
  - The description mostly refers only to using replaceable text for e.g. names and dates. (There is a reference to using it for "generic term[s]".) However, in the License List XML markups, we use `<alt>` tags for a variety of "not legally substantive" matches. Should the guideline's description be expanded to clarify this usage?
