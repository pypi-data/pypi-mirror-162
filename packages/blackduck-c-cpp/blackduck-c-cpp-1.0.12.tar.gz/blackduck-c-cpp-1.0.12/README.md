# blackduck-c-cpp

This code is responsible for running a c/cpp build wrapped by Coverity - capturing the source and binary files involved
and then using the available tools to deliver BDIO and signatures to Black Duck using a variety of tools and
methodologies.

## Overview

C and CPP projects don't have a standard package manager or method for managing dependencies. It is therefore more
difficult to create an accurate BOM for these projects. This leaves Software Composition Analysis tools fewer options
than with other languages. The primary options which are available in this context are: file system signatures. Black
Duck has a variety of old and new signatures which can be used to build a BOM. In order to effectively use signatures,
the tool first needs to know which files to take signatures from. In the past SCA tools have pointed a scanner at a
build directory, getting signatures from a subset of files within the directory sub-tree. The problem with this approach
is that there are many environmental variables, parameters and switches provided to the build tools, which make
reference to files outside of the build directory to include as part of the build. Further, there are, commonly, files
within the build directory, which are not part of the build and can lead to false positives within the BOM.

The new Black Duck C/CPP tool avoids the pitfalls described above by using a feature of Coverity called Build Capture.
Coverity Build Capture, wraps your build, observing all invocations of compilers and linkers and storing the paths of
all compiled source code, included header files and linked object files. These files are then matched using a variety of
methods described in the section of this document called "The BOM".

## Supported Platforms

Debian, Redhat, Ubuntu, openSUSE, Fedora, CentOS, macOS, and Windows are supported.

The signature scan and binary scan will be completed on all supported platforms as permitted by your Black Duck license. 
On Unix-like operating systems, a package manager scan will also be run. Since Windows doesn't have a supported package 
manager, blackduck-c-cpp scans run on Windows won't include the package manager scan and won't produce a BDIO file.
Any scan cli parameters can be used and passed to blackduck-c-cpp tool through additional_sig_scan_args parameter.

## Installation

Minimum version of Black Duck required is 2020.10.0

To install from pypi:

```
pip install blackduck-c-cpp
```

To install a specific version:

```
pip install blackduck-c-cpp==0.1.18b0
```

## Configuration

Prior to running your build, run any build specific configuration needed. Then the blackduck-c-cpp tool can either be
configured using a .yaml file or with command line arguments.

Here is a sample fully functional .yaml configuration: ardour-config.yaml

```
build_cmd: ../waf build
build_dir: /Users/theUser/myProject/ardour/build/
skip_build: False
verbose: True
project_name: ardour_mac
project_version: may-4-2021
bd_url: https://...
api_token: <token>
insecure: False
```

### API Token

Black Duck API tokens are generated on a per-user basis. To scan to a new project and view the results, the user who
generates the API token for blackduck-c-cpp must at minimum have the **Global Code Scanner**, **Global Project
Viewer**, and **Project Creator** roles assigned. To scan to an existing project and view the results, the user must at minimum have the project
assigned to their user, and have the **Project Code Scanner** role assigned. See Administration > Managing Black Duck
user accounts > Understanding roles in the Black Duck Help documentation for more details on user roles. The Black Duck
Help documentation is accessible through the Black Duck UI.

To generate an API token:

1. Go to the Black Duck UI and log in.
2. From the user menu located on the top navigation bar, select My Access Tokens.
3. Click Create New Token. The Create New Token dialog box appears.
4. Enter a name, description (optional), and select the scope for this token (to use with blackduck-c-cpp, must be **
   read and write access**).
5. Click Create. The Access Token Name dialog box appears with the access token.
6. Copy the access token shown in the dialog box. This token can only be viewed here at this time. Once you close the
   dialog box, you cannot view the value of this token.

### Details

usage: blackduck-c-cpp [-h] [-c CONFIG] [-bc build_cmd] -d BUILD_DIR [-Cov coverity_root] [-Cd cov_output_dir]
[-od output_dir] [-s [SKIP_BUILD]] [-v [verbose]] -proj PROJECT_NAME -vers PROJECT_VERSION [-Cl CODELOCATION_NAME]
-bd bd_url -a api_token [-as additional_sig_scan_args] [-i [insecure]] [-f [force]] [-djs [DISABLE_JSON_SPLITTER]] 
[-si SCAN_INTERVAL] [-jsl json_splitter_limit] [-dg [debug]] [-st [SKIP_TRANSITIVES]] [-sh [SKIP_INCLUDES]] 
[-sd [SKIP_DYNAMIC]] [-off [OFFLINE]] [-md modes] [-uo [USE_OFFLINE_FILES]] [-sc scan_cli_dir] [-Cc cov_configure_args] 
[-ac additional_coverity_params] [-es [EXPAND_SIG_FILES]] [-po PORT]

arguments:

```
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file path.
  -bc build_cmd, --build_cmd build_cmd
                        Command used to execute the build
  -d BUILD_DIR, --build_dir BUILD_DIR
                        Directory from which to run build. Absolute path (not relative) information is required
  -Cov coverity_root, --coverity_root coverity_root
                        Base directory for coverity. If not specified, blackduck-c-cpp downloads latest mini coverity 
                        package from GCP for authorized Black Duck customers for Black Duck versions >= 2021.10. 
                        Absolute path (not relative) information is required. For downloading coverity package using 
                        GCP, you need to open connection toward *.googleapis.com:443. If you don't have coverity package 
                        and your Black Duck version is < 2021.10, please contact sales team to get latest version of 
                        coverity package.
  -Cd cov_output_dir, --cov_output_dir cov_output_dir
                        Target directory for coverity output files.If not specified, defaults to 
                        user_home/.synopsys/blackduck-c-cpp/output/project_name. Absolute path (not relative) 
                        information is required
  -od output_dir, --output_dir output_dir
                        Target directory for blackduck-c-cpp output files.If not specified, defaults to 
                        user_home/.synopsys/blackduck-c-cpp/output/project_name. Absolute path (not relative) 
                        information is required
  -s [SKIP_BUILD], --skip_build [SKIP_BUILD]
                        Skip build and use previously generated build data.
  -v [verbose], --verbose [verbose]
                        Verbose mode selection
  -proj PROJECT_NAME, --project_name PROJECT_NAME
                        Black Duck project name
  -vers PROJECT_VERSION, --project_version PROJECT_VERSION
                        Black Duck project version
  -Cl CODELOCATION_NAME, --codelocation_name CODELOCATION_NAME
                        This controls the Black Duck's codelocation.  The codelocation_name will overwrite any scans 
                        sent to the same codelocation_name, indicating that this is a new scan of a previous code 
                        location.  Use with care.
  -bd bd_url, --bd_url bd_url
                        Black Duck URL
  -a api_token, --api_token api_token
                        Black Duck API token
  -as additional_sig_scan_args, --additional_sig_scan_args additional_sig_scan_args
                        Any additional args to pass to the signature scanner
  -i [insecure], --insecure [insecure]
                        Disable SSL verification so self-signed Black Duck certs will be trusted
  -f [force], --force [force]
                        In case of GCP failure, force use of older version of Coverity (if present)
  -djs [DISABLE_JSON_SPLITTER], --disable_json_splitter [DISABLE_JSON_SPLITTER]
                        Disable the json splitter and always upload as a single scan
  -si SCAN_INTERVAL, --scan_interval SCAN_INTERVAL
                        Set the number of seconds to wait between scan uploads in case of multiple scans
  -jsl json_splitter_limit, --json_splitter_limit json_splitter_limit
                        Set the limit for a scan size in bytes
  -dg [debug], --debug [debug]
                        Debug mode selection. Setting debug: True sends all the files we found to all matching types. 
                        By default, it will only send files not detected by package manager to BDBA and Signature 
                        matching.
  -st [SKIP_TRANSITIVES], --skip_transitives [SKIP_TRANSITIVES]
                        Skipping all transitive dependencies
  -sh [SKIP_INCLUDES], --skip_includes [SKIP_INCLUDES]
                        Skipping all .h & .hpp files from all types of scan
  -sd [SKIP_DYNAMIC], --skip_dynamic [SKIP_DYNAMIC]
                        Skipping all dynamic (.so/.dll) files from all types of scan
  -off [OFFLINE], --offline [OFFLINE]
                        Store bdba and sig tar files, sig scan json, and raw_bdio.csv to disk if offline mode is true
  -md modes, --modes modes
                        Comma separated list of modes to run - 'all'(default),'bdba','sig','pkg_mgr'
  -uo [USE_OFFLINE_FILES], --use_offline_files [USE_OFFLINE_FILES]
                        Use offline generated files for upload in online mode
  -sc scan_cli_dir, --scan_cli_dir scan_cli_dir
                        Scan cli directory. Absolute path (not relative) information is required
  -Cc cov_configure_args, --cov_configure_args cov_configure_args
                        Additional configuration commands to cov-configure for different compilers. Inputs taken are of 
                        format {"compiler":"compiler-type"}. There is a way to use coverity template configuration to 
                        reduce number of template compiler configurations with wildcards: 
                        example: "--compiler *g++ --comptype gcc" for adding x86_64-pc-linux-gnu-g++
  -ac additional_coverity_params, --additional_coverity_params additional_coverity_params
                        Any additional args to pass to coverity build command. example: "--record-with-source"
  -es [EXPAND_SIG_FILES], --expand_sig_files [EXPAND_SIG_FILES]
                        Use expand_sig_files for creating exploded directory instead of tar in sig scanner mode
  -po PORT, --port PORT
                        Set a custom Black Duck port
```

#### Running

Once your blackduck-c-cpp tool is installed and configured as explained above, simply run the command:

blackduck-c-cpp --config /Users/theUser/myProject/ardour-config.yaml

To use snippet scanning, pass the snippet scanning parameters to the signature scanner using
--additional_sig_scan_args <snippet scanning parameter(s)>. Synopsys recommends using --snippet-matching. See Scanning 
Components > Using the Signature Scanner > Running a component scan using the Signature Scanner command line in the 
Black Duck Help Guide for more details.

To access the Black Duck server via a proxy, you must set a SCAN_CLI_OPTS environment variable prior to running the 
scan. See Scanning Components > Using the Signature Scanner > Accessing the Black Duck server via a proxy in the Black 
Duck Help Guide for details.

#### The Bom

Direct Dependencies - These are files which are being linked in to the built executable directly or header files
included by source code as identified by Coverity Build Capture.  
Package Manager - The Package Manager of the Linux system is queried about the source of the files - if recognized,
these are added to the BOM as "Direct Dependencies". Transitive Dependencies - These are files which are needed by the
Direct Dependencies. LDD - LDD is used to List the files (Dynamic Dependencies) of the Direct Dependencies. These files
are then used to query the package manager and results are added to the BOM as "Transitive Dependencies". Binary Matches
BDBA - Any linked object files not identified by the package manager are sent to BDBA (Binary) for matching. Signature
Matches - Any linked object and header files not identified by the package manager as well as all source code identified
by Coverity Build Capture are then sent to the Knowledge Base for signature matching.

## CI Builds

This projects CI build is run through GitLab-CI Pipelines, within this repository. When changes are made on
the `master` (default) branch, the version will be appended with `b` and the pipeline number as metadata. For `release/`
branches, `-rc` will be appended to the version with the pipeline number as metadata, and this will be published to
Artifactory. When changes are made to another branch (`dev/` or `bugfix/` for example), `dev` will be appended to the
version with the pipeline number, and the commit hash will be appended as metadata.

For example:

* default branch: 1.0.0b3821+abcd1234
* release branch: 1.0.0rc4820+abcd1234
* dev branch: 1.0.0dev5293+abcd1234
* release: 1.0.0

Release jobs are also run through GitLab-CI Pipelines, when tagged as per below. The version will be uploaded to
Artifactory at the end of the pipeline.

# Releasing

To release this library, simply tag this repo with a tag of the format: `vMM.mm.ff` like `v1.0.1`. This version should
match the version (minus the `v` in `setup.py`)

Be sure to increment the version in `setup.py` to the next fix version, or minor/major version as necessary. Do not add
any metadata or additional version information to the version, here.

The specific set of steps is:

- Ensure a full `python setup install` completes
- Commit changes
- Tag with `v##.##.##`, matching the version number in `setup.py`
- Push the change log changes, and tag, to GitLab
- Update the version number in `setup.py`
- Commit version change and push to GitLab

## FAQ's

1. If BOM isn't capturing all expected components, what to do?

Make sure you did a clean build. Run all clean commands and configure commands before running the blackduck-c-cpp tool with build command.
Also, if you are using custom compilers, you have to configure it as follows:
--cov_configure_args: {"gcc.cx.a.b-ac.mips64-linux":"gcc"} where "gcc.cx.a.b-ac.mips64-linux" is compiler and "gcc" is compiler type.
you can also set matchConfidenceThreshold to 0 in additional_sig_scan_args.

2. How to run snippet scanning?

Pass below command in your yaml file
`additional_sig_scan_args: '--snippet-matching' `
To run it from command line, example:
`blackduck-c-cpp -bc "make" -d "/apps/cpuminer-2.5.1/" -s False -v True -proj "cpuminer-cmd" -vers 1.0 -bd "https:<bd_url>" -a "<api_token" -as ="--snippet-matching --copyright-search" -i False`

3. Where can blackduck-c-cpp.log be found on the system?

All output files will be in
`user_home/.synopsys/blackduck-c-cpp/output/project_name`
by default if --output_dir is not given. Else, All output files will be in output_dir.

4. How to run blackduck-c-cpp?

Run with config file where are arugments are set or through command line. 
Example:
`blackduck-c-cpp -c /apps/../../cpuminer-config.yaml`
or
To run it from command line,:
`blackduck-c-cpp -bc "make" -d "/apps/cpuminer-2.5.1/" -s False -proj "cpuminer-cmd" -vers 1.0 -bd "https:<bd_url>" -a "<api_token" -i False`
Give all absolute paths in yaml file or command line instead of relative paths.
Below command will give you an error - where -od (output dir) is relative path
`blackduck-c-cpp -bc make -d . -Cov ~/bd-capture/ -od bd-build -proj test-ptj -vers test -bd https:<bd_url> -a <api_token> -md pkg_mgr`

5. blackduck-c-cpp invokes BDBA. Do we need to be licensed for it? What happens if I don't have BDBA?

It throws `BDBA is not licensed for use with the current Black Duck instance -- will not be used` and goes to next matching type

6. Running blackduck-c-cpp throwing import errors

Check if you installed blackduck-c-cpp from testpypi. If so, please uninstall and install from pypi for dependencies to be automatically installed.
If you still see import errors, There may be some issues with multiple installations.
Try to create a virtual environment with python >= 3.6 version. Uninstall blackduck-c-cpp outside virtual environment and install blackduck-c-cpp inside virtual env. Otherwise, it may be looking at wrong installation path (Can be seen in stacktrace)
In linux environment:
```
python3 -m venv venv
source venv/bin/activate
pip3 install blackduck-c-cpp
```

7. Where to download coverity mini package?

If coverity_root is not specified, blackduck-c-cpp automatically downloads latest mini coverity package from GCP for authorized Black Duck users for Black Duck versions >= 2021.10.
For downloading coverity package using GCP, you need to open connection toward *.googleapis.com:443.
If you don't have coverity package and your Black Duck version is < 2021.10, please contact sales team to get latest version of coverity package.

8. BDBA upload throws an error as follows:

```
    raise RemoteDisconnected("Remote end closed connection without"
http.client.RemoteDisconnected: Remote end closed connection without response
.......
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
```
Check your requests-toolbelt library version - `pip show requests-toolbelt`. If you have older version than 0.9.1, install 0.9.1 version and try again.

9. Windows build - The blackduck-c-cpp process is stuck during a phase

Try giving a keyboard input by pressing enter/any other key if you still have the command prompt open where stuck. We noticed in Windows that programs sometimes get stuck  when we click into the console and enter the "selection" mode to highlight/copy text from it.

10. Error:

```
headers.pop('Accept')
KeyError: 'Accept'
```
Do `pip show blackduck`. If you have version < 1.0.4, install 1.0.4 version and try again.

11. Windows error - `MemoryError`

Make sure you have the correct installation of python (64bit vs 32 bit) for your operating system.

12. Spaces in the paths to Coverity analysis 

` /apps/.../cov\ 2021\ <vers>/bin/cov-build`
Coverity needs to be located in a directory that doesn't have a space in it. 

13. Signature scan is performed on tar.gz. Adding other sig scan arguments are not working. What to do?

Set `expand_sig_files: True`

14. How to uninstall blackduck-c-cpp?

pip uninstall blackduck-c-cpp

15. I already have a coverity build for my project. Can I use the tool?

Yes, you can set --cov_output_dir to the path where your coverity output files reside. (build-log.txt and emit directory), then set `skip_build: True`.

16. How to see more logging information for troubleshooting? 

You can see the blackduck-c-cpp.log file in output_dir  (OR) set verbose: True to see if it reveals any issues in stdout.

17. I have custom compilers. What to do?

If you are using custom compilers, you have to configure it as follows:
cov_configure_args: {"gcc.cx.a.b-ac.mips64-linux":"gcc"} where "gcc.cx.a.b-ac.mips64-linux" is compiler and "gcc" is compiler type.

18. What is debug mode?

Setting `debug: True` sends all the files we found to all matching types. By default, it will only send files not detected by package manager to BDBA and Signature matching.

19. How to run a specific matching type? 

You can select modes: sig, bdba, pkg_mgr in config file to run specific ones.  

20. I already have run blackduck-c-cpp once. I ran in offline mode. I want to run in online mode. Do I need to do the full build again?

No, you can set `use_offline_files: True` and `skip_build: True` to use already stored files and just upload it to Black Duck.

21. I already have run blackduck-c-cpp once. I got a few errors after build is finished which are fixed now. I want to run again. Do I need to do the full build again?

No, you can set `skip_build: True` to skip build process.

