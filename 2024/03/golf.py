import re

print(
    sum(
        int(a) * int(b)
        for a, b in (
            match.groups()
            for match in re.finditer(
                r'mul\((\d{1,3}),(\d{1,3})\)',
                open('input').read(),
            )
        )
    )
)
