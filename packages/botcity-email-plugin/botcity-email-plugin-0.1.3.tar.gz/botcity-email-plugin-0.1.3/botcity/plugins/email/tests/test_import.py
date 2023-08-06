def test_package_import():
    import botcity.plugins.email as plugin
    assert plugin.__file__ != ""
