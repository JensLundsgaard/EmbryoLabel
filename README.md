# EmbryoLabel
Embryo labeling project

# Instructions
* Make sure you have [the data](https://zenodo.org/records/7912264) downloaded here and unzipped, the directory should be called `embryo_dataset` and be in the `EmbryoLabel` repo folder.
* Install python 3 and then run `pip install Flask Werkzeug` in a terminal.
* Now run `python label_app.py` (you may have to mess around with path settings if the above command doesn't work, feel free to contact me should it not work).
* Now you should be able to enter `localhost:5000` into a browser and see the website. 
* Be careful with `true_images.txt` as it contains all the important stuff (that will earn you wine). Definitely back it up and stuff.
* Discerning whether there is an embryo should be relatively easy. Any clump of stuff that looks "biological" or like cells is an embryo and anything that's just uninterpretable background noise or dust/ debris is not. Now do be careful as some of the images contain a lot of sperm, but those do not count if there's no embryo in sight.  Some embryos will be partially outside of the lens circle, if that's the case it's still an embryo.
* Most of the images are gonna have an embryo so it's important that you focus and make sure you get all of the empty ones. If you mislabel an empty one I care less but try to be accurate. There is an undo button that will take you back one, and you can edit `true_images.txt` but of course excercise caution. There is a backup but the balance must be respected. 
* I am giving you access to push to the repo. Definitely push often to save your progress and I would urge each of you to make a branch, and then merge the files together onto one later. Be careful with merge conflicts if working on the same branch.
* If you can believe it this marvel of computer science technology was not coded by me but rather by Claude so if there are any bugs let me know, but it should be relatively straightforward.
* Remember this work is mysterious and important and don't forget you are the matrix. Everything comes from you. Have fun!
