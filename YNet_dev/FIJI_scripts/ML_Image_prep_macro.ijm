DIR = getDirectory("select the input folder");
targetFolder = getDirectory("select the output folder");
files = getFileList(DIR);
count = 0;

setBatchMode(true);

for (i=0; i<files.length; i++) {
	if (endsWith(files[i], ".tif")) { 
	run("Bio-Formats Importer", "open=["+ DIR + files[i] + "] color_mode=Default view=Hyperstack stack_order=XYCZT");
	getDimensions(width, height, channels, slices, frames);
	origTitle = getTitle();
	run("Split Channels");

	selectImage("C1-" + origTitle);
	close();
	selectImage("C3-" + origTitle);
	close();
	selectImage("C4-" + origTitle);
	close();
	
	selectImage("C5-" + origTitle);
	run("Make Substack...","slices=14");
	
	selectImage("C2-" + origTitle);
	run("Z Project...", "start=1 stop="+slices+" projection=[Max Intensity]");


	selectImage("C5-" + origTitle);
	close();
	selectImage("C2-" + origTitle);
	close();

	run ("Images to Stack", "name=[Stack]");
	save(targetFolder + "/" + origTitle + "stack.tif");
	
	while (nImages>0) {
		selectImage(nImages);
		close();
	}
	
	}
	
	
}
setBatchMode("exit & display");
