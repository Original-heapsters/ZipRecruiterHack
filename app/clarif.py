from clarifai.rest import ClarifaiApp

app = ClarifaiApp()
app.tag_urls(['https://samples.clarifai.com/metro-north.jpg'])
