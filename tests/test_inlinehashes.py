import pytest


from inlinehashes import __version__, parse
from inlinehashes.lib import Inline, _EVENT_HANDLER_ATTRS


class TestInline:
    def test_cant_be_changed(self):
        pass

    @pytest.mark.parametrize(
        "content,short_version",
        (
            ("", ""),
            ("var a = 1", "var a = 1"),
            ("a" * 60, "a" * 50),
            ("a " * 100, "a " * 25),
        ),
    )
    def test_short_content_property(self, content, short_version):
        inline = Inline(content=content)
        assert inline.short_content == short_version

    @pytest.mark.parametrize(
        "content,hash",
        (
            (
                "// some random text just for the test",
                "sha256-vzu2ZpqtqjZiOP3l+j6HQsHp+riIi8i0xVa6on8mlRo=",
            ),
            (
                "var someVar = { name: 'some object' };",
                "sha256-v/WJgrg+M5LxuU0IK/Y1dT3tksK9AiJzm1dKDBVW+iw=",
            ),
            (
                "color:blue;font-size:46px;",
                "sha256-DFhv4zzzY7i3fh6qPPRuAiglNEX0GP7ZxllkMYPUF90=",
            ),
            ("var i = 1;", "sha256-1QhCpB/IFWw8Pb/g/IBzIBgErHWG5wrytauZib+UF+g="),
            (" var i = 1; ", "sha256-JXsq/1KEtrnrlGozP1V228Z4rNL2pB7MlgpEBBbVnLA="),
        ),
    )
    def test_sha256_property(self, content, hash):
        inline = Inline(content=content)
        assert inline.sha256 == hash

    @pytest.mark.parametrize(
        "content,hash",
        (
            (
                "// some random text just for the test",
                "sha384-A5EAhuefnNnRpbU0i6b6GBGk/fhBeEbvVVnYrzVFcbxgiuNmk5K59nFbJQZiagi2",
            ),
            (
                "var someVar = { name: 'some object' };",
                "sha384-tml8/Wx/TZ8FTfazxR54HN61zqUyzX4KuiBPxa/ot0X/oyEC19LmI+BqaeiDrzcE",
            ),
            (
                "color:blue;font-size:46px;",
                "sha384-BLIqhqw5pbfWaCOlp8/xES7A5UVD7u8imzLvpHJ1sJW2gsIWoj+rLoPKH2OBMZUi",
            ),
            (
                "var i = 1;",
                "sha384-exw+zZA219Su/XnwiE7j7V4yLVNpXk08+H71sGIABcOj8Nq+OiXLWOkPTUajb3tv",
            ),
            (
                " var i = 1; ",
                "sha384-nZsnOT4KuSVu0hzbDrLEc3Qvy3ATghmXDEZ9Mof5QDMEsu40TtlH3KSMqTCNHNyu",
            ),
        ),
    )
    def test_sha384_property(self, content, hash):
        inline = Inline(content=content)
        assert inline.sha384 == hash

    @pytest.mark.parametrize(
        "content,hash",
        (
            (
                "// some random text just for the test",
                "sha512-8Ig5oR6kSaFkAeZ2DQXCxTb9Q0E4roYZfFBaHhXZaB1xOTdFphjm72MkfDLp7SMoDGSIYBbXxtve5s2nXLhhtA==",
            ),
            (
                "var someVar = { name: 'some object' };",
                "sha512-We1wStKIQ/9t0u/jKh5rNlYMMYlQtPrp5yfe7FQRqCkClsLKfRSDWfQ+eFKvJk/ciSIWdph3+dJ6sobCct9l2Q==",
            ),
            (
                "color:blue;font-size:46px;",
                "sha512-D79kfJyq3IsfBLSk/JJmZtIHI1NnOyP2EnYG8DUjsfTQZLVgKXJd3oUXy0lsIskqUAdQ1XxS2nNtwBa7eYg+pA==",
            ),
            (
                "var i = 1;",
                "sha512-9jfUbPKIo4icp7gZFa9Wvl3S9ofp2zdzxqqvOL1oLSV49b3I6MkVtyjM1ydPefCjLreZBlKa+iZwF1DLhUdgSQ==",
            ),
            (
                " var i = 1; ",
                "sha512-KG0P+4FVrx4nU8/XARtZiktTanUC8ENoTN4/oyQG/O9n9NpdHiVIVpW8JWwrixq/7u9OWtDog6BJAcG199eqFA==",
            ),
        ),
    )
    def test_sha512_property(self, content, hash):
        inline = Inline(content=content)
        assert inline.sha512 == hash


class TestParse:
    def test_parse_detects_script_tags(self):
        doc = """
        <html>
        <head><title>Some title</title></head>
        <body>Some body
        <script>alert("hash this");</script>
        </body>
        </html>
        """
        inlines = parse(doc)
        assert len(inlines) == 1
        assert inlines[0].content == 'alert("hash this");'

    def test_parse_detects_style_tags(self):
        doc = """
        <html>
        <head>
          <title>Some title</title>
          <style>.someclass { background:#142a3f; }</style>
        </head>
        <body>Some body</body>
        </html>
        """
        inlines = parse(doc)
        assert len(inlines) == 1
        assert inlines[0].content == ".someclass { background:#142a3f; }"

    def test_parse_detects_style_attributes(self):
        doc = """
        <html>
        <head>
          <title>Some title</title>
        </head>
        <body style="text-color: #000;">Some body</body>
        </html>
        """
        inlines = parse(doc)
        assert len(inlines) == 1
        assert inlines[0].content == "text-color: #000;"

    @pytest.mark.parametrize("attr", _EVENT_HANDLER_ATTRS)
    def test_parse_detect_attributes_with_js(self, attr):
        # Just to test they are detected even though some of them are
        # not valid for all elements
        doc = f"""
        <html>
        <head>
          <title>Some title</title>
        </head>
        <body {attr}="alert(1);">Some body</body>
        </html>
        """
        inlines = parse(doc)
        assert len(inlines) == 1
        assert inlines[0].content == "alert(1);"


def test_version():
    assert __version__ == "0.0.2"
