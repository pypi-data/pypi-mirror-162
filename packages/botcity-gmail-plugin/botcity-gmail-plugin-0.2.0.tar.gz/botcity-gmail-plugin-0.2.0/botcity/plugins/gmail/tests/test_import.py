def test_package_import():
    import botcity.plugins.gmail as plugin
    assert plugin.__file__ != ""
