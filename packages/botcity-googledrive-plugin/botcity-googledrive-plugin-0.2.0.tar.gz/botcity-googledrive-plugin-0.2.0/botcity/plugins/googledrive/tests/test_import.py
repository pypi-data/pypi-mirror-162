def test_package_import():
    import botcity.plugins.googledrive as plugin
    assert plugin.__file__ != ""
