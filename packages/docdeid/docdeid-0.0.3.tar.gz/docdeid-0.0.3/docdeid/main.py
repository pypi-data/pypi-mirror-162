from docdeid.datastructures.lookup import LookupList
from docdeid.document.document import Document
from docdeid.tokenizer.tokenizer import SpaceSplitTokenizer


def main1():

    l1 = LookupList()
    l1.add_items_from_iterable(items=["a", "b", "c"])

    l2 = LookupList()
    l2.add_items_from_iterable(items=["c", "d", "e"])

    l2 -= l1

    print(l1._items)


def main2():

    tokenizer = SpaceSplitTokenizer()

    doc = Document(text="dit is een test", tokenizer=tokenizer)

    text = doc.text
    text = text[:10]

    print(text)
    print(doc.text)


if __name__ == "__main__":
    main2()
