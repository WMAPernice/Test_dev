DIR = getDirectory("select the input folder");
targetFolder = getDirectory("select the output folder");
files = getFileList(DIR);
count = 0;
IMSIZE = 512;

setBatchMode(true);

for (i=0; i<files.length; i++) {
	if (endsWith(files[i], ".nd2")) { 
	// ensure images are opened with color_mode=Grayscale!
	run("Bio-Formats Importer", "open=["+ DIR + files[i] + "] color_mode=Grayscale view=Hyperstack stack_order=XYCZT");
	getDimensions(width, height, channels, slices, frames);
	origTitle = getTitle();
	split_Title = split(origTitle, ".");
	Im_id = split_Title[0];
	run("Split Channels");

	selectImage("C5-" + origTitle);
	close();
	
	//8-bit conversion:
	//Experimented with 8-bit conversion on stack vs conversion before stacking... 
	//8-bit conversion prior to stacking appears to preserve brightness differences in individual images,
	//and hence likely preserves more information.
	selectImage("C1-" + origTitle);
	run("Z Project...", "start=1 stop="+slices+" projection=[Max Intensity]");
	run("8-bit");
	
	selectImage("C2-" + origTitle);
	run("Z Project...", "start=1 stop="+slices+" projection=[Max Intensity]");
	run("8-bit");
	
	selectImage("C3-" + origTitle);
	run("Z Project...", "start=1 stop="+slices+" projection=[Max Intensity]");
	run("8-bit");
	
	selectImage("C4-" + origTitle);
	run("Z Project...", "start=1 stop="+slices+" projection=[Max Intensity]");
	run("8-bit");
	
	selectImage("C1-" + origTitle);
	close();
	selectImage("C2-" + origTitle);
	close();
	selectImage("C3-" + origTitle);
	close();
	selectImage("C4-" + origTitle);
	close();

	run ("Images to Stack", "name=[Stack]");
	run("Size...", "width=&IMSIZE height=&IMSIZE constrain average interpolation=Bicubic");
	// If input image is not square, size outputs non-square image (constrain!), hence need crop. 
	run("Specify...", "width=&IMSIZE height=&IMSIZE x=0 y=0 slice=1"); 
	run("Crop");
	//run("8-bit") <-- deactivated in favor of per-image 8-bit conversion prior to stacking...

	 
	

	save(targetFolder + "/" + Im_id + ".tif");
	
	while (nImages>0) {
		selectImage(nImages);
		close();
	}
	
	}
	
	
}
setBatchMode("exit & display");
