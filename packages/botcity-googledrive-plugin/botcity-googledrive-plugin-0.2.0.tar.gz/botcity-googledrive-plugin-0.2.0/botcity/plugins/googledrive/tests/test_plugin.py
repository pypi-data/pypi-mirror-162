from botcity.plugins.googledrive import BotGoogleDrivePlugin

credentials_path = "C:\\BotCity\\workspace\\Plugins\\credenciais\\credentials.json"

googledrive = BotGoogleDrivePlugin(credentials_path)


def test_return_correct_file_id():
    file_id = googledrive.search_file_by_name("planilha_nomes")
    assert file_id == "1xrRycTf8Onl1gEfvDc0jEY7uS9QFq3fGMX8aXCr3e4A"


def test_return_none_for_non_existent_file():
    file_id = googledrive.search_file_by_name("file.txt")
    assert file_id is None


def test_create_folder():
    created_folder_id = googledrive.create_folder("My folder")
    assert type(created_folder_id) == str


def test_return_correct_folder_id():
    folder_id = googledrive.search_folder_by_name("Pasta - Testes")
    assert folder_id == "105vy-S6JNLc4qCGHAVGaxgZ4-WutZi-U"


def test_return_none_for_non_existent_folder():
    folder_id = googledrive.search_folder_by_name("Pasta 2 - Testes")
    assert folder_id is None


def test_return_all_files_from_parent_folder():
    subfiles = googledrive.get_files_from_parent_folder("105vy-S6JNLc4qCGHAVGaxgZ4-WutZi-U")
    assert len(subfiles) == 5


def test_do_not_return_any_files_for_empty_folders():
    subfiles = googledrive.get_files_from_parent_folder("1NwOMjAKod9yx7A7S8rnn8hMgeWuoH_9G")
    assert len(subfiles) == 0
