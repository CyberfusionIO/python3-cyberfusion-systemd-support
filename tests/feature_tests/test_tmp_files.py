from cyberfusion.SystemdSupport.tmp_files import TmpFileConfigurationLine

type_ = "d"
path = "/tmp/example"
mode = "0755"
user = "example"
group = "example"


def test_tmp_file_configuration_line_string_base() -> None:
    tmp_file_configuration_line = str(
        TmpFileConfigurationLine(
            type_=type_, path=path, mode=mode, user=user, group=group
        )
    ).split()

    assert tmp_file_configuration_line[0] == type_
    assert tmp_file_configuration_line[1] == path
    assert tmp_file_configuration_line[2] == mode
    assert tmp_file_configuration_line[3] == user
    assert tmp_file_configuration_line[4] == group


def test_tmp_file_configuration_line_string_without_age() -> None:
    tmp_file_configuration_line = str(
        TmpFileConfigurationLine(
            type_=type_, path=path, mode=mode, user=user, group=group, age=None
        )
    ).split()

    assert tmp_file_configuration_line[5] == "-"


def test_tmp_file_configuration_line_string_with_age() -> None:
    age = "1d"

    tmp_file_configuration_line = str(
        TmpFileConfigurationLine(
            type_=type_, path=path, mode=mode, user=user, group=group, age=age
        )
    ).split()

    assert tmp_file_configuration_line[5] == age
