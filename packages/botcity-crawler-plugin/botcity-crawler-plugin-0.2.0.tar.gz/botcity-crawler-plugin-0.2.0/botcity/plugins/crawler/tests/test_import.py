def test_package_import():
    import botcity.plugins.crawler as crawler
    assert crawler.__file__ != ""
