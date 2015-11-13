## ShapeOut
[![Build Win](https://img.shields.io/appveyor/ci/paulmueller/ShapeOut/master.svg?label=build_win)](https://ci.appveyor.com/project/paulmueller/ShapeOut)

This repository contains a graphical user interface for the analysis
and visualization of RT-DC data sets. For more informaion please visit
http://www.zellmechanik.com/.


### Information for developers

#### Running from source
The easiest way to run ShapeOut from source is to use
[Anaconda](http://continuum.io/downloads). 

- **Windows**: Sketchy installation instructions are 
  [here](https://github.com/ZellMechanik-Dresden/ShapeOut/tree/master/freeze_appveyor) and 
  [here](https://github.com/ZellMechanik-Dresden/ShapeOut/blob/master/appveyor.yml).

- **Debian**: Run [this script](https://github.com/ZellMechanik-Dresden/ShapeOut/blob/master/develop/activate_linux.sh)
  which will create a python virtual environment.

- **MacOS**: The above links should help.

#### Contributing
The main branch for developing ShapeOut is *develop*. Small changes that do not
break anything can be submitted to this branch.
If you want to do big changes, please (fork ShapeOut and) create a separate branch,
e.g. `my_new_feature_dev`, and create a pull-request to *develop* once you are done making
your changes.
**Please make sure to edit the 
[Changelog](https://github.com/ZellMechanik-Dresden/ShapeOut/blob/master/CHANGELOG)**. 

**Very important:** Please always try to use 

	git pull --rebase

instead of

	git pull
	
to prevent confusions in the commit history.

#### Tests
ShapeOut is tested using pytest. If you have the time, please write test
methods for your code and put them in the `tests` directory. You may
run the tests manually by issuing:

	python setup.py test
	

#### Test binaries
After each commit to the ShapeOut repository, a binary installer is created
by [Appveyor](https://ci.appveyor.com/project/paulmueller/ShapeOut). Click
on a build and navigate to `ARTIFACTS` (upper right corner right under
the running time of the build). From there you can download the executable
Windows installer.


#### Creating releases
Please **do not** create releases when you want to test if something you
did works in the final Windows binary. Use the method described above to
do so. Releases should be created when improvements were made,
bugs were resolved, or new features were introduced.

##### Procedure:
1. Make sure that the [changelog (develop)](https://github.com/ZellMechanik-Dresden/ShapeOut/blob/develop/CHANGELOG)
   is updated and that the [version (develop)](https://github.com/ZellMechanik-Dresden/ShapeOut/blob/develop/shapeout/_version.py)
   is incremented.

1. Create a pull request from develop into master using the web interface or simply run

    git checkout master  
    git pull origin develop  
    git push  
	
2. Create the release at https://github.com/ZellMechanik-Dresden/ShapeOut/releases.  
   Make sure that the tag of the release follows the version format of ShapeOut
   (e.g. `0.5.3`) and also name the release correctly (e.g. `ShapeOut 0.5.3`).
   Also, copy and paste the change log of the new version into the comments of the release.
   The first line of the release comments should contain the download counts shield like so:
   
       `![](https://img.shields.io/github/downloads/ZellMechanik-Dresden/ShapeOut/0.5.3/total.svg)`.
   
   The rest should contain the change log.  
   Make sure to check `This is a pre-release` box.
   
3. Once the release is created, [Appveyor](https://ci.appveyor.com/project/paulmueller/ShapeOut)
   will perform the build process and upload the installation files directly to the release. 
   If the binary works, edit the release and uncheck the `This is a pre-release` box.

4. Make sure that all the changes you might have performed on the `master` branch are brought back
   to `develop`.
   

    git checkout develop  
    git pull origin master  
    git push     

