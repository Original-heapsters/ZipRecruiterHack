import json
import os
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import Config as cnf



def doStuffWithURL(imageURL):
    print 'ID: ' + cnf.ConfigVars['clarifai_id']
    print 'SECRET: ' + cnf.ConfigVars['clarifai_secret']
    app = ClarifaiApp(cnf.ConfigVars['clarifai_id'],cnf.ConfigVars['clarifai_secret'])
    os.environ['CLARIFAI_APP_ID'] = cnf.ConfigVars['clarifai_id']
    os.environ['CLARIFAI_APP_SECRET'] = cnf.ConfigVars['clarifai_secret']
    response = app.tag_files([imageURL])
    return response

def doStuff():
    print 'ID: ' + cnf.ConfigVars['clarifai_id']
    print 'SECRET: ' + cnf.ConfigVars['clarifai_secret']
    os.environ['CLARIFAI_APP_ID'] = cnf.ConfigVars['clarifai_id']
    os.environ['CLARIFAI_APP_SECRET'] = cnf.ConfigVars['clarifai_secret']
    app = ClarifaiApp(cnf.ConfigVars['clarifai_id'],cnf.ConfigVars['clarifai_secret'])
    #response = app.tag_urls(['https://samples.clarifai.com/metro-north.jpg'])
    #response = app.tag_urls(['https://s-media-cache-ak0.pinimg.com/originals/38/66/81/3866811a0fb059d23af7b522ba046d23.jpg'])
    #response = app.tag_urls(['http://demandware.edgesuite.net/sits_pod52/dw/image/v2/AAFF_PRD/on/demandware.static/-/Sites-masterCatalogTeva/default/dw101b8a41/images/grey/1003986-BLK_M1.jpg'])
    response = app.tag_urls(['https://s-media-cache-ak0.pinimg.com/736x/7d/c4/f0/7dc4f0009b51ac636dbc3449bdeca1b8.jpg'])
    #http://demandware.edgesuite.net/sits_pod52/dw/image/v2/AAFF_PRD/on/demandware.static/-/Sites-masterCatalogTeva/default/dw101b8a41/images/grey/1003986-BLK_M1.jpg
    #https://s-media-cache-ak0.pinimg.com/736x/7d/c4/f0/7dc4f0009b51ac636dbc3449bdeca1b8.jpg
    #response = app.tag_urls(['https://www.sashapua.com/wp-content/uploads/2010/10/hooker-610x360.jpg'])
    return response

def getConceptsWithConfidence(jsonObj):
    conceptsWConf = {}
    for key in jsonObj['outputs']:
        for item in key['data']['concepts']:
            for con in item:
                name = str(item['name'])
                value = str(item['value'])
                conceptsWConf[name] = value
    return conceptsWConf

def getImageURL(jsonObj):
    url = ''

    url = jsonObj['outputs'][0]['data'][0]['input']['data']['image']['url']
    # for key in jsonObj['outputs']:
    #     for item in key['data']['input']:
    #         for con in item:
    #             name = str(item['name'])
    #             value = str(item['value'])
    #             conceptsWConf[name] = value


    return url
