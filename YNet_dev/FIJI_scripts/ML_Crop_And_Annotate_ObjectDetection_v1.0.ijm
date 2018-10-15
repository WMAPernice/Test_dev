// Crop_And_Annotate.ijm
// ImageJ/Fiji macro
// Wolfgang Pernice, wp2181@cumc.columbia.edu; credit to Theresa Swayne, tcs6@cumc.columbia.edu, 2017

// Allows user to crop and annotate age of manually selected cells in an image, 
// and produce cropped versions with unique filenames containing annotation
//
// Input: A stack (or single plane) image. 
// 		User clicks on desired cells, and provides annotation data.
// Output: 
//		1) A stack (or single plane) of 200x200 pixels centered on each point.
//		2) An ROIset of the points chosen.
// 		Output images are saved in the same folder as the source image.
//		and named following the scheme: 
// 		genotype, initials, _E_xperiment, _S_tain, _F_ixed/live, _C_ell ID, _A_ge
// 		e.g. WT_WP_E1_S1_F1_C8_A13 
//		wild-type cell, prepared by Wolfgang P., from the first dataset submitted (E1), 
//		Fixed (F1), Cell number 8 (C8), age 13 (A13)
//
//	TODO: A CSV file will also be produced containing:
// 		0 cropped filename, 1 original filename, 2-3 center of crop box (XY), 4 genotype, 5 initials,
//		6 expt, 7 stain, 8 fixed/live, 9 cell ID, 10 age
// 		
// Usage: Open an image. You should already know the age of each cell in the image, or be
// 		looking at it simultaneously in another program. 
//		Then run the macro. 
//
// Limitations: If the point is < 200 pixels from an edge the output image is not 200x200,  
// 		but only goes to the edge of the image.




// ------------- SETUP

// maximum width and height of the final cropped image, in pixels
CROPSIZE = 200;


//Input Ouput
//inputdir=getDirectory("")
outputdir=getDirectory("Output")


// get file info 
selectWindow(getTitle())
id = getImageID();
title = getTitle();
dotIndex = indexOf(title, ".");
basename = substring(title, 0, dotIndex);
roiName = basename + "_roiset.zip";

roiManager("reset");


// get the parameters that are constant for all cells in the image
genotype = "";
initials = "";
experiment = 0;
stain = "";
MitoNum = 0;
stainNum = 5;
fixed = "";
fixedNum = 2;
MitoChoices = newArray("Cit1-mCherry", "Tom70-mCherry");
stainChoices = newArray("WGA 647", "Calcofluor","WGA 488");
fixedChoices = newArray("fixed","live");
nextCellNum = 0;
imageInfo = "";

Dialog.create("Enter experiment info");

Dialog.addString("Genotype:", "WT");
Dialog.addString("Experimenter Initials:", "WP");
Dialog.addNumber("Your Unique Experiment Number:", 3); // e.g. 3 = YNet_Data_[03]
Dialog.addChoice("Mito:", MitoChoices);
Dialog.addChoice("Stain:", stainChoices);
Dialog.addChoice("Fixed/Live:",fixedChoices);
Dialog.addNumber("Image number in series:", 1);
Dialog.addNumber("Next Cell Number in Experiment:",1); // allows continuing expt on a different image
Dialog.show();

genotype = Dialog.getString();
initials = Dialog.getString();
experiment = Dialog.getNumber();
Mito = Dialog.getChoice();
stain = Dialog.getChoice();
fixed = Dialog.getChoice();
ImageNum = Dialog.getNumber();
nextCellNum = Dialog.getNumber(); 

// TODO: raise errors if wrong type of input or no input

// turn choices into codes

if (Mito == "Cit1-mCherry") {
	MitoNum = 0; }
else if (stain == "Tom70-mCherry") {
	MitoNum = 1; }


if (stain == "Calcofluor") {
	stainNum = 0; }
else if (stain == "WGA 488") {
	stainNum = 1; }
else  { // 647
	stainNum = 2; }

if (fixed == "fixed") {
	fixedNum = 1; }
else { // live
	fixedNum = 0; }

// constant image info for all cells
imageInfo = genotype+"_"+initials+"_E"+experiment+"_Mito"+MitoNum+"_S"+stainNum+"_F"+fixedNum+"_I"+ImageNum;
DatasetInfo = genotype+"_"+initials+"_E"+experiment+"_Mito"+MitoNum+"_S"+stainNum+"_F"+fixedNum;

print("You entered:");
print(imageInfo);
print("and your next cell will be",nextCellNum);

// TODO: create CSV file

moreCells = 1;
cellCount = 0;
//setTool("point"); //legacy
setTool("polyline");
//run("Line Tool...", "type=Hybrid color=Yellow size=Medium add label");
//
age = 0;

// INTERACTIVE LOOP: MARKING AND ANNOTATING CELLS

while (moreCells == 1) 
	{
	cellNum = nextCellNum + cellCount;
	waitForUser("Mark cell", "Click on a bud neck, then click OK");
	
	age = "0";
	
	roiManager("add");

	// store annotations in ROI name
	numROIs = roiManager("count");
	roiManager("Select",numROIs-1); // select the most recent ROI
	roiManager("rename", imageInfo+"_C"+cellNum+"_A"+age);
	roiManager("Show All");
	
	//Error catching and editability

	// ask if they have another cell
	moreCells = getBoolean("Continue?");
	cellCount ++;
	}
		
// --------------- CROP AND SAVE

// make sure nothing is selected to begin with
selectImage(id);
roiManager("Deselect");
run("Select None");


numROIs = roiManager("count");
// ---------- tables setup
// creating MidPointCoord table
name = "[MidPointCoord]";
run("New... ", "name="+name+" type=Table");
mpc = name;
print(mpc, "\\Clear"); // clearing log
print(mpc, "cell_ID,x,y"); // column names

// creating All-Coordinates table
name = "[Tripoint_Coord]";
run("New... ", "name="+name+" type=Table");
tpc = name;
print(tpc, "\\Clear"); // clearing log
print(tpc, "cell_ID,idx,x,y"); // column names


for(i=0; i<numROIs;i++) 
	{ 
	selectImage(id); 
	roiManager("Select", i); 
	
	cropName = call("ij.plugin.frame.RoiManager.getName", i); // filename will be roi name
	Roi.getCoordinates(x, y); // x and y are arrays;
	
	// fill in tables
	print(mpc, "Cell_"+i+","+x[1]+","+y[1]); // fill in Midpoints table

	// fill in All-coord table
	for (o=0; o<x.length; o++) {
		print(tpc, "Cell_"+i+","+"Point_"+o+","+x[o]+","+y[o]);
	}
    	
	// cropping
	// make new rectangle ROI centered on 2nd point, marking the mother-bud-neck
	run("Specify...", "width=&CROPSIZE height=&CROPSIZE x="+x[1]+" y="+y[1]+" slice=1 centered"); 
	run("Duplicate...", "title=&cropName duplicate"); 
	selectWindow(cropName);
	saveAs("tiff", outputdir+File.separator+getTitle);
	close(); // close cropped image
	}

// saving ROI-sets
run("Select None");
roiManager("save",outputdir+File.separator+roiName);

// saving coordinates in .csv
selectWindow("MidPointCoord");
saveAs("text",  outputdir + "00_MidPoints_"+DatasetInfo+".csv"); 

selectWindow("Tripoint_Coord");
saveAs("text",  outputdir + "00_Tripoint_Coord_"+DatasetInfo+".csv"); 


// ---  FINISH UP
close(); // original image
roiManager("reset");
print("\\Close");
print(mpc, "\\Close");
print(tpc, "\\Close");

