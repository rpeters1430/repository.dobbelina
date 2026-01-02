"""Additional tests for zfile behaviors."""

import io
import warnings
import zipfile

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
