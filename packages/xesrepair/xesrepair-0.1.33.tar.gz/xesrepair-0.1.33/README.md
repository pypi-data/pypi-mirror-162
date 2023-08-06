# 每次发版注意事项
1. 修改setup.py中的版本信息
2. 运行python setup.py sdist bdist_wheel进行打包
3. 上传pypi
   1. 运行twine upload dist/*
   2. username:zhushaodong123
   3. password:R4E3W2Q1zxc