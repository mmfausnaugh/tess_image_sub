Roughly speaking, I am using directories to organize things instead of databases. This is working reasonably well on our server. I have textfiles that list image names and dates in each directory, and I use grep to check if files are in a given directory based on the text file. I think the differencing part is not yet I/O bound. There was also some tuning of our file system (which is ZFS) that was being done to improve things. We have a TB of memory and I think some of this was set up to exploit ZFS caching.

The directories also handle multiprocessing.  In TESS EM2, they look like this:

```
-sector??
--cam?_ccd?
---o1a
---o1b
---o2a
---oba
```

Each o{1a,1b,2a,2b} directory has a number of subdirectories like this
```
-o1a
--slice000
--slice001
--slice002
```

up to some number near 192. This is because I have 192 cores, and the way I multiprocess is using a bash script to loop over slice directories 

```
for slice in $(ls -d slice*); do
  cd $slice
   ~/isis/image_subtrach.csh &
  cd ..
done
wait
```

So, ISIS executables are not in this repo, I'm hoping the Hawaii team has these on their own.

Roughly speaking, `setup` configures directories; it has scripts that set up the dir structure, adds config files to make isis, runs, and links to everything we need (e.g., PSF models, interp_ images, etc.) The `control` directory has the main scripts to make things go.

In normal operations, I usually log in and run something like
```
cd /data/tess/image_sub/sector73
~/tess_image_sub/setup/dates_parallel_smooth.sh o1b
~/tess_image_sub/control/image_sub_em2 o1b
```
This assumes you have made a reference image. I do this in o1a these days, because the point is to run photometry every week on new transients. (Though I am behind on this.)  I can talk about making a reference at some point.

photometry is a little more complicated, either we are running *en masse* from an existing catalog, or running a hand-made list. There is another package to translate RA/Dec into TESS coordinates and make a `phot.data` file. A peak at how this works is in the directory `phot_scripts`. When doing things by hand, I use functions in `do_phot_em2.sh` and similar, which are in the top level directory. I believe the photometry is I/O bound, and I'm hoping at some point to rewrite this to be faster (needs major changes to the original C code).

Hopefully enough to get started.

Things have been stable, but I shouldn't have hardcoded paths. There are not too many variables, but sometimes these are also hardcoded and it is a problem.

There are other aspects that are embarassing about this code; some is very convoluted, some is very poor style. C'est la vie.
