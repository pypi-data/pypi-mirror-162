# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opencv_camcalib',
 'opencv_camcalib.gui',
 'opencv_camcalib.gui.ui',
 'opencv_camcalib.utils']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'func-timeout>=4.3.5,<5.0.0',
 'opencv-python<=4.5.5.64',
 'pyside6>=6.3.1,<7.0.0',
 'qt-material>=2.12,<3.0',
 'rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['opencv-camcalib = opencv_camcalib.cli:main']}

setup_kwargs = {
    'name': 'opencv-camcalib',
    'version': '0.1.0',
    'description': '',
    'long_description': '<p align="center">\n    <a href="https://pixelied.com/editor/design/62d95249afecc1406f2037a9"><img alt="logo" src="https://raw.githubusercontent.com/XavierJiezou/OpenCV-CamCalib/main/images/favicon_256x256.svg" /></a>\n<h1 align="center">相机标定器</h1>\n<p align="center">一个基于OpenCV的自动化相机数据采集和标定程序。\n</p>\n</p>\n<p align="center">\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/actions?query=workflow:Release">\n        <img src="https://github.com/XavierJiezou/OpenCV-CamCalib/workflows/Release/badge.svg"\n            alt="GitHub Workflow Release Status" />\n    </a>\n    <a href=\'https://opencv-camera-calibration.readthedocs.io/zh/latest/?badge=latest\'>\n        <img src=\'https://readthedocs.org/projects/opencv-camera-calibration/badge/?version=latest\' alt=\'Documentation Status\' />\n    </a>\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/actions?query=workflow:Lint">\n        <img src="https://github.com/XavierJiezou/LitMNIST/workflows/Lint/badge.svg"\n            alt="GitHub Workflow Lint Status" />\n    <a\n        href="https://www.codacy.com/gh/XavierJiezou/OpenCV-CamCalib/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=XavierJiezou/OpenCV-CamCalib&amp;utm_campaign=Badge_Grade">\n        <img src="https://app.codacy.com/project/badge/Grade/c2f85c8d6b8a4892b40059703f087eab" alt="Codacy Badge">\n    </a>\n    <a href="https://codecov.io/gh/XavierJiezou/OpenCV-CamCalib">\n        <img src="https://codecov.io/gh/XavierJiezou/OpenCV-CamCalib/branch/main/graph/badge.svg?token=QpCLcUGoYx" alt="codecov">\n    </a>\n    <a href="https://pypi.org/project/OpenCV-CamCalib/">\n        <img src="https://img.shields.io/pypi/pyversions/OpenCV-CamCalib" alt="PyPI - Python Version">\n    </a>\n    <a href="https://pypistats.org/packages/OpenCV-CamCalib">\n        <img src="https://img.shields.io/pypi/dm/OpenCV-CamCalib" alt="PyPI - Downloads">\n    </a>\n    <a href="https://pypi.org/project/OpenCV-CamCalib/">\n        <img src="https://img.shields.io/pypi/v/OpenCV-CamCalib" alt="PyPI">\n    </a>\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/stargazers">\n        <img src="https://img.shields.io/github/stars/XavierJiezou/OpenCV-CamCalib" alt="GitHub stars">\n    </a>\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/network">\n        <img src="https://img.shields.io/github/forks/XavierJiezou/OpenCV-CamCalib" alt="GitHub forks">\n    </a>\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/issues">\n        <img src="https://img.shields.io/github/issues/XavierJiezou/OpenCV-CamCalib" alt="GitHub issues">\n    </a>\n    <a href="https://github.com/XavierJiezou/OpenCV-CamCalib/blob/main/LICENSE">\n        <img src="https://img.shields.io/github/license/XavierJiezou/OpenCV-CamCalib" alt="GitHub license">\n    </a>\n    <br />\n    <br />\n    <a href="https://www.python.org/">\n        <img src="http://ForTheBadge.com/images/badges/made-with-python.svg" alt="forthebadge made-with-python">\n    </a>\n    <a href="https://github.com/XavierJiezou">\n        <img src="http://ForTheBadge.com/images/badges/built-with-love.svg" alt="ForTheBadge built-with-love">\n    </a>\n</p>\n<p align="center">\n    <a href="#演示">观看演示</a>\n    •\n    <a href="https://github.com/xavierjiezou/OpenCV-CamCalib/issues/new">报告错误</a>\n    •\n    <a href="https://github.com/xavierjiezou/OpenCV-CamCalib/issues/new">功能需求</a>\n  </p>\n  <p align="center">\n    <a href="/docs/README.en.md">English </a>\n    •\n    <a href="/docs/README.cn.md">简体中文</a>\n</p>\n<p align="center">喜欢这个项目吗？请考虑捐赠<a href="https://paypal.me/xavierjiezou?country.x=C2&locale.x=zh_XC">（<a\n            href="https://raw.githubusercontent.com/XavierJiezou/OpenCV-CamCalib/main/images/wechat.jpg">微信</a> | <a\n            href="https://raw.githubusercontent.com/XavierJiezou/OpenCV-CamCalib/main/images/alipay.jpg">支付宝</a>）</a>，以帮助它改善！</p>\n\n## 演示\n\n> 测试相机 RTSP 地址：[rtsp://admin:a12345678@y52t229909.zicp.vip](rtsp://admin:a12345678@y52t229909.zicp.vip)\n\n![demo](https://raw.githubusercontent.com/XavierJiezou/OpenCV-CamCalib/main/images/demo.png)\n\n## 功能\n\n- [x] 数据采集\n- [x] 棋盘标定\n- [x] 畸变矫正\n- [ ] 圆孔标定\n\n## 安装\n\n### 命令界面\n\n```bash\npip install opencv-camcalib\n```\n\n### 图像界面\n\n```bash\npip install opencv-camcalib\n```\n\n## 用法\n\n### 命令界面\n\n`$ opencv-camcalib`\n\n- 数据采集\n\n```bash\nopencv-camcalib capture rtsp://admin:a12345678@y52t229909.zicp.vip\n```\n\n- 棋盘标定\n\n```bash\nopencv-camcalib calibrate --data_dir="/path/to/data" --rows=9 --cols=6\n```\n\n- 畸变纠正\n\n```bash\nopencv-camcalib undistort --data_dir="/path/to/data"\n```\n\n### 图形界面\n\n![1](/images/gui/1_main_window.png)\n![2](/images/gui/2_chessboard_calibration.png)\n![3](/images/gui/3_distortion_correction.png)\n![4](/images/gui/4_screenshot_setting.png)\n![5](/images/gui/5_data_collection.png)\n![6](/images/gui/6_about_us.png)\n\n## 构建\n\n- 命令界面\n\n```bash\npoetry build\n```\n\n- 图像界面\n\n```bash\npyinstaller -w -F opencv_camcalib/app.py -i images/favicon_256x256.ico -n opencv-camcalib-0.1.0\n```\n\n## 文档\n\n- 安装\n\n```bash\ngit clone https://github.com/XavierJiezou/OpenCV-CamCalib.git\ncd OpenCV-CamCalib/\npip install -r docs/requirements.txt\n```\n\n- 构建\n\n```bash\nmkdocs build\n```\n\n- 部署\n\n```bash\nmkdocs serve\n```\n\n## 贡献\n\n```bash\ngit clone https://github.com/XavierJiezou/OpenCV-CamCalib.git\ncd OpenCV-CamCalib/\npip install poetry\npoetry install\n```\n\n## 日志\n\n见 [CHANGELOG.md](/CHANGELOG.md)\n\n## 证书\n\n[MIT License](/LICENSE)\n\n## 依赖\n\n### 生产依赖\n\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=psf&repo=requests)](https://github.com/psf/requests)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=Textualize&repo=rich)](https://github.com/Textualize/rich)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=google&repo=python-fire)](https://github.com/google/python-fire)\n\n### 开发依赖\n\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=python-poetry&repo=poetry)](https://github.com/python-poetry/poetry)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pytest-dev&repo=pytest)](https://github.com/pytest-dev/pytest)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pytest-dev&repo=pytest-cov)](https://github.com/pytest-dev/pytest-cov)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pre-commit&repo=pre-commit)](https://github.com/pre-commit/pre-commit)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=PyCQA&repo=flake8)](https://github.com/PyCQA/flake8)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=PyCQA&repo=pylint)](https://github.com/PyCQA/pylint)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=psf&repo=black)](https://github.com/psf/black)\n[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=uiri&repo=toml)](https://github.com/uiri/toml)\n\n## 参考\n\n- [Displaying webcam feed using OpenCV and Python+PySide.](https://gist.github.com/bsdnoobz/8464000)\n- [OpenCV Face Detection Example](https://doc.qt.io/qtforpython/examples/example_external__opencv.html)\n',
    'author': 'XavierJiezou',
    'author_email': '878972272@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/XavierJiezou/OpenCV-CamCalib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<3.11',
}


setup(**setup_kwargs)
