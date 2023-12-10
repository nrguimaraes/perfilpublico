from os.path import  exists
import datetime
from pytrends.request import TrendReq
import os
import pickle
import dash_trich_components as dtc
from dash import html
import modules.mongointerface as mi
import string


def getPhoto(author_name):
    filename=author_name.lower().replace(" ","")
    filename="".join([s for s in filename if s not in string.punctuation])
    extensions=[".png",".jpeg",".jpg"]
    for ext in extensions:

        path="assets/author_photos/"+filename+ext


        if(exists(path)):
            return path

    return "assets/author_photos/user.png"



def getTrends(limit=10):
    today=str(datetime.datetime.now().date())
    filepath="assets/trends_today.p"
    if(os.path.exists(filepath)):
        data=pickle.load(open(filepath,"rb"))
        if(data["date"]==today):
            return data["trends"]

    try:
        pt = TrendReq(hl="pt-PT")
        trends = pt.trending_searches(pn="portugal")[0]
        trends=trends[:limit]
        result={"date":today,"trends":list(trends)}
        pickle.dump(result,open(filepath, "wb"))
        return list(trends)
    except:
        return list(trends)

def generateCarousellTrends(trend_keyword):
    result = mi.searchSimilarTopics(trend_keyword)

    responsive = [
        {
            'breakpoint': 1500,
            'settings': {
                'slidesToShow': min(len(result),8),
                #'slidesToScroll': 8,
                'infinite': False,
                'dots': False
            }
        },

    {
            'breakpoint': 1200,
            'settings': {
                'slidesToShow': min(len(result),6),
                #'slidesToScroll': 8,
                'infinite': False,
                'dots': False
            }
        },


        {
            'breakpoint': 1024,
            'settings': {
                'slidesToShow': min(len(result),3),
                #'slidesToScroll': 3,
                'infinite': False,
                'dots': False
            }
        },
        {
            'breakpoint': 600,
            'settings': {
                'slidesToShow': min(len(result),2),
                #'slidesToScroll': 1,
                #'initialSlide': 2
                'infinite': False,
                'dots': False
            }
        },
        {
            'breakpoint': 480,
            'settings': {
                'slidesToShow':min(len(result),1),
                #'slidesToScroll': 1,
                'infinite': False,
                'dots': False
            }
        }
    ]

    carousel=dtc.Carousel( children=
                    [html.Div(className="carousel_div",children=[
                        html.Center(),
                        html.Center(html.A(children=[html.Img(src=getPhoto(item["author_name"]), style={"width": "161px", "height": "161px"}),item["author_name"]], className="author_name_car",
                                           href="/authortopicpage?id=" + str(item["author_id"]) + "&" + "topic="+trend_keyword ))]) for
                        item in result
                    ],
                    slides_to_show=min(len(result),10),
                    #slides_to_scroll=min(len(result),10),
                    #variable_width=True,
                    infinite=False,
                    #arrows=False,
                    #center_mode=True,
                    responsive=responsive

                    #center_padding="50px"

                )

    # html.Div(html.Img(src="assets/user.png")),
    return carousel,len(result)

