def test_package_import():
    import botcity.plugins.discord as plugin
    assert plugin.__file__ != ""
