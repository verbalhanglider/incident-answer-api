
from attic.main import classify_request

tests = [
    ('I was charged twice for my order.', 'billing'),
    ('Where is my package? It never arrived.', 'shipping'),
    ('What are your business hours?', 'general'),
    ('I need a copy of my invoice.', 'billing'),
    ('Something is wrong with my order.', 'billing'),
    ('I need help.', 'general'),
    ('This isn\'t right.', 'general'),
    ('Can someone look into this?','general'),
    ('I have an issue with a recent purchase.', 'general'),
    ('My tracking number says delivered but I don\'t have the package.', 'shipping'),
]

for text, expected in tests:
    result = classify_request(text)
    actual = result.get("intent")
    print({
        "text": text,
        "expected": expected,
        "actual": actual,
        "pass": actual == expected
    })