"""Additional tests for zfile behaviors."""

import io
import warnings
import zipfile

import pytest

from resources.lib import zfile


def _build_zip(path):
    with zipfile.ZipFile(str(path), "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("alpha.txt", b"alpha")
        zf.writestr("dir/beta.txt", b"beta")
        zf.comment = b"comment"
    return path


def test_is_zipfile_with_file_object(tmp_path):
    zip_path = _build_zip(tmp_path / "sample.zip")
    with open(zip_path, "rb") as handle:
        assert zfile.is_zipfile(handle) is True


def test_endrecdata_reads_comment(tmp_path):
    zip_path = _build_zip(tmp_path / "sample.zip")
    with open(zip_path, "rb") as handle:
        endrec = zfile._EndRecData(handle)
    assert endrec[zfile._ECD_COMMENT] == b"comment"


def test_zipfile_read_open_and_namelist(tmp_path, capsys):
    zip_path = _build_zip(tmp_path / "sample.zip")
    with zfile.ZipFile(str(zip_path), "r") as zf:
        assert sorted(zf.namelist()) == ["alpha.txt", "dir/beta.txt"]
        assert zf.read("alpha.txt") == b"alpha"
        with zf.open("dir/beta.txt") as handle:
            assert handle.read() == b"beta"
        assert zf.getinfo("alpha.txt").file_size == 5
        zf.printdir()
        zf.testzip()
    captured = capsys.readouterr()
    assert "alpha.txt" in captured.out


def test_zipfile_extract_and_extractall(tmp_path):
    zip_path = _build_zip(tmp_path / "sample.zip")
    extract_root = tmp_path / "extract"
    with zfile.ZipFile(str(zip_path), "r") as zf:
        zf.extract("alpha.txt", path=str(extract_root))
        zf.extractall(path=str(extract_root))
    assert (extract_root / "alpha.txt").read_bytes() == b"alpha"
    assert (extract_root / "dir" / "beta.txt").read_bytes() == b"beta"


def test_comment_truncates_with_warning(tmp_path):
    zip_path = _build_zip(tmp_path / "sample.zip")
    long_comment = b"x" * (zfile.ZIP_MAX_COMMENT + 10)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with zfile.ZipFile(str(zip_path), "r") as zf:
            zf.comment = long_comment
            assert len(zf.comment) == zfile.ZIP_MAX_COMMENT
    assert caught


def test_check_zipfile_rejects_invalid_bytes():
    buffer = io.BytesIO(b"not-a-zip")
    assert zfile._check_zipfile(buffer) is False


def test_write_and_writestr_roundtrip(tmp_path):
    zip_path = tmp_path / "out.zip"
    payload_path = tmp_path / "payload.txt"
    payload_path.write_text("hello", encoding="utf-8")

    with zfile.ZipFile(str(zip_path), "w") as zf:
        zf.write(str(payload_path), arcname="payload.txt")
        zf.writestr("dir/", b"")
        zf.writestr("dir/inner.txt", b"inner")

    with zfile.ZipFile(str(zip_path), "r") as zf:
        names = sorted(zf.namelist())
        assert names == ["dir/", "dir/inner.txt", "payload.txt"]
        assert zf.read("payload.txt") == b"hello"
        assert zf.read("dir/inner.txt") == b"inner"


def test_writestr_warns_on_duplicate_name(tmp_path):
    zip_path = tmp_path / "dup.zip"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with zfile.ZipFile(str(zip_path), "w") as zf:
            zf.writestr("dup.txt", b"first")
            zf.writestr("dup.txt", b"second")
    assert any("Duplicate name" in str(warning.message) for warning in caught)


def test_open_rejects_invalid_mode(tmp_path):
    zip_path = tmp_path / "mode.zip"
    with zfile.ZipFile(str(zip_path), "w") as zf:
        zf.writestr("sample.txt", b"data")

    with zfile.ZipFile(str(zip_path), "r") as zf:
        with pytest.raises(RuntimeError, match="open\\(\\) requires mode"):
            zf.open("sample.txt", "w")


def test_write_after_close_raises(tmp_path):
    zip_path = tmp_path / "closed.zip"
    zf = zfile.ZipFile(str(zip_path), "w")
    zf.close()
    with pytest.raises(RuntimeError, match="closed"):
        zf.writestr("later.txt", b"data")


def test_getinfo_missing_raises(tmp_path):
    zip_path = tmp_path / "missing.zip"
    with zfile.ZipFile(str(zip_path), "w") as zf:
        zf.writestr("sample.txt", b"data")

    with zfile.ZipFile(str(zip_path), "r") as zf:
        with pytest.raises(KeyError):
            zf.getinfo("missing.txt")


def test_pyzipfile_writepy_adds_compiled_file(tmp_path):
    source = tmp_path / "module.py"
    source.write_text("value = 1\n", encoding="utf-8")
    zip_path = tmp_path / "pyzip.zip"

    with zfile.PyZipFile(str(zip_path), "w") as zf:
        zf.writepy(str(source))

    with zfile.ZipFile(str(zip_path), "r") as zf:
        names = zf.namelist()
        assert any(
            name.endswith("module.pyc") or name.endswith("module.pyo")
            for name in names
        )


def test_zipextfile_readline_and_peek(tmp_path):
    zip_path = tmp_path / "lines.zip"
    payload = b"alpha\r\nbeta\n"
    with zfile.ZipFile(str(zip_path), "w", compression=zfile.ZIP_DEFLATED) as zf:
        zf.writestr("lines.txt", payload)

    with zfile.ZipFile(str(zip_path), "r") as zf:
        with zf.open("lines.txt", "r") as fh:
            chunk = fh.read1(3)
            assert chunk == b"alp"
            assert fh.peek(4).startswith(b"ha")
            line = fh.readline()
            assert line == b"ha\r\n"
            second = fh.readline()
            assert second == b"beta\n"
            assert fh.read() == b""
