# PyPI Package Publishing Guide for LazzyORM

This guide explains how to publish LazzyORM to PyPI (Python Package Index).

## Prerequisites

1. **Create PyPI Account**
   - Register at https://pypi.org/account/register/
   - Register at https://test.pypi.org/account/register/ (for testing)

2. **Install Publishing Tools**
   ```bash
   pip install twine build wheel setuptools
   ```

3. **Configure PyPI Credentials**
   
   Create `~/.pypirc` file:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN-HERE

   [testpypi]
   username = __token__
   password = pypi-YOUR-TEST-API-TOKEN-HERE
   ```

## Publishing Process

### 1. Prepare the Package

Ensure all files are up to date:
- ✅ `setup.py` - Package configuration
- ✅ `pyproject.toml` - Modern build configuration
- ✅ `README.md` - Complete documentation
- ✅ `CHANGELOG.md` - Version history
- ✅ `LICENSE` - MIT License
- ✅ `MANIFEST.in` - Files to include

### 2. Update Version Number

Update version in three places:
1. `setup.py` - `VERSION = "0.3.0"`
2. `pyproject.toml` - `version = "0.3.0"`
3. `lazzy_orm/__init__.py` - `__version__ = "0.3.0"`

### 3. Build the Distribution

```bash
# Clean previous builds
make clean
# or manually:
rm -rf build/ dist/ *.egg-info

# Build distribution packages
python setup.py sdist bdist_wheel
# or using build:
python -m build
```

This creates:
- `dist/LazzyORM-0.3.0.tar.gz` - Source distribution
- `dist/LazzyORM-0.3.0-py3-none-any.whl` - Wheel distribution

### 4. Test the Package Locally

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Test import
python -c "from lazzy_orm import Connector, LazyQuery; print('OK')"
```

### 5. Upload to Test PyPI (Optional but Recommended)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ LazzyORM

# Test the installed package
python -c "import lazzy_orm; print(lazzy_orm.__version__)"
```

### 6. Upload to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Or using Makefile
make upload
```

### 7. Verify on PyPI

Visit: https://pypi.org/project/LazzyORM/

Check:
- ✅ README displays correctly
- ✅ All metadata is correct
- ✅ Installation instructions work
- ✅ Links are functional

### 8. Test Installation

```bash
# Create new virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from PyPI
pip install LazzyORM

# Test import and basic functionality
python -c "
from lazzy_orm import Connector, LazyQuery, LazyUpdate, LazyDelete
print('✓ LazzyORM installed successfully!')
print(f'Version: {lazzy_orm.__version__}')
"
```

## Using Makefile Commands

The project includes convenient Makefile commands:

```bash
# Build distribution
make build

# Upload to Test PyPI
make upload-test

# Upload to Production PyPI
make upload

# Complete workflow: clean, build, upload
make clean build upload
```

## GitHub Release (Optional)

After publishing to PyPI, create a GitHub release:

1. Go to: https://github.com/Dipendra-creator/LazzyORM/releases
2. Click "Create a new release"
3. Tag version: `v0.3.0`
4. Release title: `LazzyORM v0.3.0`
5. Description: Copy from CHANGELOG.md
6. Attach the distribution files from `dist/`

## Troubleshooting

### Issue: README not displaying on PyPI

**Solution**: Ensure `long_description_content_type="text/markdown"` in setup.py

### Issue: Missing dependencies

**Solution**: Check all dependencies are listed in `install_requires`

### Issue: Import errors after installation

**Solution**: Verify `__init__.py` has proper exports

### Issue: File not found errors

**Solution**: Check `MANIFEST.in` includes all necessary files

## Post-Publication Checklist

- [ ] Package appears on PyPI
- [ ] README displays correctly
- [ ] Installation works: `pip install LazzyORM`
- [ ] All imports work correctly
- [ ] Documentation links are functional
- [ ] Version number is correct
- [ ] Update project status (if moving from Alpha to Beta)
- [ ] Announce release (Twitter, Reddit, etc.)
- [ ] Create GitHub release
- [ ] Update project website (if applicable)

## Updating an Existing Package

When releasing a new version:

1. Update version numbers (3 files)
2. Update CHANGELOG.md
3. Commit changes: `git commit -am "Release v0.3.1"`
4. Create tag: `git tag v0.3.1`
5. Push: `git push && git push --tags`
6. Build and upload: `make clean build upload`

## Monitoring

After publication:

- Monitor PyPI downloads: https://pypistats.org/packages/lazzyorm
- Check for issues: https://github.com/Dipendra-creator/LazzyORM/issues
- Review user feedback
- Update documentation based on common questions

## Security

**Important**: Never commit:
- PyPI tokens
- Database passwords
- `.pypirc` file
- API keys

Add to `.gitignore`:
```
.pypirc
*.env
.env.*
```

## Resources

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Setuptools Documentation**: https://setuptools.pypa.io/

## Support

For issues with publishing:
- PyPI support: https://pypi.org/help/
- Python Packaging Discourse: https://discuss.python.org/c/packaging/

---

**Last Updated**: February 13, 2026
**Package Version**: 0.3.0
