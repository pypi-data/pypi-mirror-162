def test_package_import():
    import botcity.plugins.cloudvision as plugin
    assert plugin.__file__ != ""
