import re
listhtml = """
    <div class="pagination">
        <a href="#">9</a> <a class='next' data-block-id="block1" data-parameters="from:2">Next</a>
    </div>
"""
# Test part by part
print("1:", bool(re.search(r'>(\d+)</a>', listhtml)))
print("2:", bool(re.search(r'>(\d+)</a>\s+<a class=\'next\'', listhtml)))
print("3:", bool(re.search(r'>(\d+)</a>\s+<a class=\'next\' .+?data-block-id="([^"]+)"', listhtml)))
print("4:", bool(re.search(r'>(\d+)</a>\s+<a class=\'next\' .+?data-block-id="([^"]+)"\s+data-parameters="([^"]+)">', listhtml)))
