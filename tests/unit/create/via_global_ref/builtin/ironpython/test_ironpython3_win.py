import pytest
from testing.helpers import contains_exe, contains_ref
from testing.path import join as path

from virtualenv.create.via_global_ref.builtin.ironpython.ipy3 import IronPython3Windows

IRONPYTHON3_PATH = (
    "virtualenv.create.via_global_ref.builtin.ironpython.common.Path",
    "virtualenv.create.via_global_ref.builtin.ironpython.ipy3.Path",
)


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_2_exe_on_default_py_host(py_info, mock_files):
    mock_files(IRONPYTHON3_PATH, [py_info.system_executable])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    # Default Python exe.
    assert contains_exe(sources, py_info.system_executable)
    # Should always exist.
    assert contains_exe(sources, path(py_info.prefix, "ipy3.exe"))


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_3_exe_on_not_default_py_host(py_info, mock_files):
    # Not default python host.
    py_info.system_executable = path(py_info.prefix, "ipy555.exe")
    mock_files(IRONPYTHON3_PATH, [py_info.system_executable])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    # Not default Python exe linked to both the default name and origin.
    assert contains_exe(sources, py_info.system_executable, "ipy.exe")
    assert contains_exe(sources, py_info.system_executable, "ipy555.exe")
    # Should always exist.
    assert contains_exe(sources, path(py_info.prefix, "ipyw.exe"))


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_only_shim(py_info, mock_files):
    shim = path(py_info.system_stdlib, "venv\\scripts\\nt\\ipy.exe")
    py_files = (
        path(py_info.prefix, "IronPython.SQLite.dll"),
        path(py_info.prefix, "IronPython.Wpf.dll"),
        path(py_info.prefix, "_asyncio.pyd"),
        path(py_info.prefix, "_bz2.pyd"),
    )
    mock_files(IRONPYTHON3_PATH, [shim, *py_files])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    assert IronPython3Windows.has_shim(interpreter=py_info)
    assert contains_exe(sources, shim)
    assert not contains_exe(sources, py_info.system_executable)
    for file in py_files:
        assert not contains_ref(sources, file)


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_exe_dll_pyd_without_shim(py_info, mock_files):
    py_files = (
        path(py_info.prefix, "libcrypto-1_1.dll"),
        path(py_info.prefix, "libffi-7.dll"),
        path(py_info.prefix, "_asyncio.pyd"),
        path(py_info.prefix, "_bz2.pyd"),
    )
    mock_files(IRONPYTHON3_PATH, py_files)
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    assert not IronPython3Windows.has_shim(interpreter=py_info)
    assert contains_exe(sources, py_info.system_executable)
    for file in py_files:
        assert contains_ref(sources, file)


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_python_zip_if_exists_and_set_in_path(py_info, mock_files):
    python_zip_name = f"python{py_info.version_nodot}.zip"
    python_zip = path(py_info.prefix, python_zip_name)
    mock_files(IRONPYTHON3_PATH, [python_zip])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    assert python_zip in py_info.path
    assert contains_ref(sources, python_zip)


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_no_python_zip_if_exists_and_not_set_in_path(py_info, mock_files):
    python_zip_name = f"python{py_info.version_nodot}.zip"
    python_zip = path(py_info.prefix, python_zip_name)
    py_info.path.remove(python_zip)
    mock_files(IRONPYTHON3_PATH, [python_zip])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    assert python_zip not in py_info.path
    assert not contains_ref(sources, python_zip)


@pytest.mark.parametrize("py_info_name", ["ironpython3_win_embed"])
def test_no_python_zip_if_not_exists(py_info, mock_files):
    python_zip_name = f"python{py_info.version_nodot}.zip"
    python_zip = path(py_info.prefix, python_zip_name)
    # No `python_zip`, just python.exe file.
    mock_files(IRONPYTHON3_PATH, [py_info.system_executable])
    sources = tuple(IronPython3Windows.sources(interpreter=py_info))
    assert python_zip in py_info.path
    assert not contains_ref(sources, python_zip)
