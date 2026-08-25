"""Patch online-judge-tools for AtCoder's binary memory units."""

from pathlib import Path

import onlinejudge.service.atcoder


atcoder_path = Path(onlinejudge.service.atcoder.__file__)
source = atcoder_path.read_text()

replacements = {
    "tds[3].text.endswith(' KB')": "tds[3].text.endswith(' KiB')",
    "utils.remove_suffix(tds[3].text, ' KB')) * 1000)":
        "utils.remove_suffix(tds[3].text, ' KiB')) * 1024)",
    "tds[3].text.endswith(' MB')": "tds[3].text.endswith(' MiB')",
    "utils.remove_suffix(tds[3].text, ' MB')) * 1000 * 1000)  # TODO: confirm this is MB truly, not MiB":
        "utils.remove_suffix(tds[3].text, ' MiB')) * 1024 * 1024)",
    "r'^(メモリ制限|Memory Limit): ([0-9.]+) (KB|MB)'":
        "r'^(メモリ制限|Memory Limit): ([0-9.]+) (KiB|MiB)'",
    "memory_limit_unit == 'KB'": "memory_limit_unit == 'KiB'",
    "float(memory_limit_value) * 1000)": "float(memory_limit_value) * 1024)",
    "memory_limit_unit == 'MB'": "memory_limit_unit == 'MiB'",
    "float(memory_limit_value) * 1000 * 1000)":
        "float(memory_limit_value) * 1024 * 1024)",
    "utils.remove_suffix(tds[8].text, ' KB')) * 1000":
        "utils.remove_suffix(tds[8].text, ' KiB')) * 1024",
}

for old, new in replacements.items():
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"expected exactly one occurrence in {atcoder_path}: {old!r}; found {count}"
        )
    source = source.replace(old, new)

atcoder_path.write_text(source)
