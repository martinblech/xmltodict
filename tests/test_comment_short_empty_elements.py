import pytest

from xmltodict import parse, unparse


@pytest.mark.parametrize("short_empty_elements", [False, True])
@pytest.mark.parametrize("pretty", [False, True])
@pytest.mark.parametrize(
    "obj",
    [
        {"root": {"#comment": "note"}},
        {"root": {"@id": "7", "#comment": ["first", "second"]}},
        {"root": {"child": {"#comment": "nested"}}},
        {"root": {"#comment": "before child", "child": None}},
        {"#comment": "before root", "root": None},
    ],
)
def test_comments_roundtrip_with_short_empty_elements(
    obj, pretty, short_empty_elements
):
    xml = unparse(
        obj, pretty=pretty, short_empty_elements=short_empty_elements
    )

    assert parse(xml, process_comments=True) == obj


@pytest.mark.parametrize("short_empty_elements", [False, True])
@pytest.mark.parametrize("comment", [None, ""])
def test_skipped_comments_leave_empty_elements_empty(
    comment, short_empty_elements
):
    xml = unparse(
        {"root": {"#comment": comment}},
        full_document=False,
        short_empty_elements=short_empty_elements,
    )

    expected = "<root/>" if short_empty_elements else "<root></root>"
    assert xml == expected


@pytest.mark.parametrize("short_empty_elements", [False, True])
@pytest.mark.parametrize("comment", ["invalid--comment", "invalid-"])
def test_invalid_comments_are_rejected_with_short_empty_elements(
    comment, short_empty_elements
):
    with pytest.raises(ValueError, match="Comment text"):
        unparse(
            {"root": {"#comment": comment}},
            short_empty_elements=short_empty_elements,
        )
