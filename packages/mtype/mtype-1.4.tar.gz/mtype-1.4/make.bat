@echo off

choice -c YN -m Rebuild?
if "%ERRORLEVEL%"=="1" (
	rd /S /Q dist
	py -m build
)

py -m twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDk3ZWYwOGY4LWY2ZjYtNDU4ZC04YWI0LTQ4NjMxNWQxMjMzYQACNnsicGVybWlzc2lvbnMiOiB7InByb2plY3RzIjogWyJtdHlwZSJdfSwgInZlcnNpb24iOiAxfQACOXsicHJvamVjdF9pZHMiOiBbImU4ZTNiYmYwLTIxMDItNDJlNi05ZWRmLWI5ZDg1NmI1Njg1OSJdfQAABiCfcdq3Wi1xz-JQQh_sFJaYzmeW6g-YqxTVV_Bm5oKTzA
pip uninstall -y mtype
timeout 5 /NOBREAK >nul
pip install mtype
start https://pypi.org/project/mtype/