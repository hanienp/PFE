function createGoogleSlidesWithGraph() {
  // Create a new Google Slides presentation
  var presentation = SlidesApp.create('Time Loss Causes Mapping');
  
  // Get the first slide
  var slide = presentation.getSlides()[0];
  
  // Add a title
  slide.insertTextBox('Time Loss Causes to Root Causes Mapping', 50, 50, 400, 50)
       .getText().getTextStyle().setFontSize(24).setBold(true);

  // The ID of the image file in Google Drive
  var imageId = 'YOUR_FILE_ID';
  
  // Get the image file from Google Drive
  var image = DriveApp.getFileById(imageId);
  
  // Add the image to the slide
  slide.insertImage(image.getBlob(), 50, 150, 700, 500);
}

