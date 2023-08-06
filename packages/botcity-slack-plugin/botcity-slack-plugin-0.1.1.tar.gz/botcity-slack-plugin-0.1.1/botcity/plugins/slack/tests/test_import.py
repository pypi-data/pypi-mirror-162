def test_package_import():
    import botcity.plugins.slack as plugin
    assert plugin.__file__ != ""
