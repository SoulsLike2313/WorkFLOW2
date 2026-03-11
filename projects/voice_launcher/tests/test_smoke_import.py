def test_package_import_smoke():
    import voice_launcher_app  # noqa: F401
    from voice_launcher_app.app.main import main  # noqa: F401
