@ECHO ON

set scriptdir=%~dp0
set builddir=%scriptdir%\build

IF not exist %builddir% (mkdir %builddir%)

python -m PyInstaller --name bin2hpm --onefile --workpath %builddir% --distpath %builddir%\dist %scriptdir%\bin2hpm\__main__.py
