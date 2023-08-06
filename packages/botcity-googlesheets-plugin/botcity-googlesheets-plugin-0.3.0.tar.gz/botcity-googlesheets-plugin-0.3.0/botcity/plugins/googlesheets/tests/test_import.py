def test_package_import():
    import botcity.plugins.googlesheets as plugin
    assert plugin.__file__ != ""
