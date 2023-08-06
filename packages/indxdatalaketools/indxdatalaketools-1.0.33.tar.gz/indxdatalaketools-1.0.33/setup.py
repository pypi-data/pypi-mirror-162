import os
import setuptools
import site
import sys

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

dist = os.environ.get("INDX_DATALAKE_TOOLS_INSTALL", None)
print(dist)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


if dist == 'admin':
    setuptools.setup(
        
        name="indxdatalaketools",
        
        setuptools_git_versioning={
            "enabled": True,
        },
        license = "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0",
        license_files = ('LICEN[CS]E*', 'COPYING*', 'NOTICE*', 'AUTHORS*'),
        setup_requires=["setuptools-git-versioning"],
        data_files = [('man/man1', ['man/DataLakeTools.1']),],
        author="Ryan McDermott",
        author_email="rmcdermott@intelligentdx.com",
        description="Package that allows creation and manipulation of data lakes",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/IntelligentDX-LLC/data-lake-tools",
        project_urls={
            "Bug Tracker": "https://github.com/IntelligentDX-LLC/data-lake-tools/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        entry_points={'console_scripts': [
            'IndxAdminDataLakeTools = indxdatalaketools.AdminCommands.DataLakeToolsAdmin:main'
        ]},
        install_requires=[
        'google-cloud-datastore==2.5.1',
        'google-cloud-storage==2.3.0',
        'google-cloud-bigquery==3.1.0',
        'google-cloud-bigquery-storage==2.13.1',
        'google-auth==1.35.0',
        'google-cloud-pubsub==2.12.1',
        'google-cloud-scheduler==2.6.3',
        'google-cloud-secret-manager==2.10.0',
        'google-cloud-compute==0.7.0',
        'importlib-metadata==4.11.3',
        'protobuf==3.20.1',
        'click==8.1.3',
        'opencv-python==4.5.5.64',
        'google-api-python-client==1.9.3',
        'google-cloud-tasks==2.7.1',
        'requests==2.27.1',
        'numpy==1.22.3',
        'google-crc32c==1.3.0'
        ],
        packages=setuptools.find_packages(exclude=['**test**', 
        '*GoogleCloudResources*',]),
        python_requires=">=3.8",
        include_package_data=True,
        package_data={'': ['*ComputeEngineScripts/*']},
    )
else:
    setuptools.setup(
            
        name="indxdatalaketools",
        
        setuptools_git_versioning={
            "enabled": True,
            "template": "{tag}",
        },
        setup_requires=["setuptools-git-versioning"],
        license = "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0",
        license_files = ('LICEN[CS]E*', 'COPYING*', 'NOTICE*', 'AUTHORS*'),
        data_files = [('man/man1', ['man/DataLakeTools.1']),],
        author="Ryan McDermott",
        author_email="rmcdermott@intelligentdx.com",
        description="Package that allows the upload of files to a datalake",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/IntelligentDX-LLC/data-lake-tools",
        project_urls={
            "Bug Tracker": "https://github.com/IntelligentDX-LLC/data-lake-tools/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        entry_points={'console_scripts': [
            'IndxClientDataLakeTools = indxdatalaketools.ClientCommands.DataLakeToolsClient:main'
        ]},
        install_requires=[
        'google-cloud-datastore==2.5.1',
        'google-cloud-storage==2.3.0',
        'google-cloud-bigquery==3.1.0',
        'google-cloud-bigquery-storage==2.13.1',
        'google-auth==1.35.0',
        'google-cloud-pubsub==2.12.1',
        'google-cloud-scheduler==2.6.3',
        'google-cloud-secret-manager==2.10.0',
        'google-cloud-compute==0.7.0',
        'importlib-metadata==4.11.3',
        'protobuf==3.20.1',
        'click==8.1.3',
        'opencv-python==4.5.5.64',
        'google-api-python-client==1.9.3',
        'google-cloud-tasks==2.7.1',
        'requests==2.27.1',
        'numpy==1.22.3',
        'google-crc32c==1.3.0',
        ],
        packages=setuptools.find_packages(
            include=['*ArgumentValidation*', 
            '*DataStandardizer*', 
            '*GoogleClientWrappers*', 
            '*ClientTools*',
            '*ClientCommands*',
            'indxdatalaketools',
            '*data*'], 
            exclude=['**test**', '**pycache**',
            '*GoogleCloudResources*',
            '*ComputeEngineCreator*',
            '*ComputeEngineScripts*',
            '*DataLakeFileOperations*',
            '*DataLakeOperations*',
            '*AdminTools*',]),
        python_requires=">=3.8",
        include_package_data=True,
        package_data={'': []},
    )
