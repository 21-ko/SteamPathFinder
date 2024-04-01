from setuptools import setup, find_packages

# README 파일을 읽어서 long_description으로 사용
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SteamPathFinder",  # 패키지 이름
    version="0.0.4",  # 패키지 버전
    author="21-ko",  # 패키지 저자
    author_email="dlwlghks8779@naver.com",  # 저자 이메일
    description="A utility module for finding Steam paths",  # 패키지 간단 설명
    long_description=long_description,  # 패키지 상세 설명
    long_description_content_type="text/markdown",  # 상세 설명의 형식
    url="https://github.com/21-ko/SteamPathFinder",  # 프로젝트 홈페이지 주소
    packages=find_packages(),  # 패키지 포함
    classifiers=[  # 패키지 분류 정보
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11"
    ],
    python_requires='>=3.6',  # 필요한 Python 버전
    install_requires=[  # 의존성 목록
        "vdf"
    ],
)
