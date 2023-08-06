def test_package_import():
    import botcity.plugins.aws.sqs as plugin
    assert plugin.__file__ != ""
