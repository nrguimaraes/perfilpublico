

from WebApp.modules.mongointerface import getMetricsByAuthor
def buildCluster():
    df=getMetricsByAuthor()
    scatter = dict(
        mode = "markers",
        name = "y",
        type = "scatter3d",
        x = df['reading_value'], y = df['factual_value'], z = df['length'],
        marker = dict( size=2, color="rgb(23, 190, 207)" )
    )
    clusters = dict(
        alphahull = 7,
        name = "y",
        opacity = 0.1,
        type = "mesh3d",
        x = df['reading_value'], y = df['factual_value'], z = df['length']
    )
    layout = dict(
        title = '3d point clustering',
        scene = dict(
            xaxis = dict( zeroline=False ),
            yaxis = dict( zeroline=False ),
            zaxis = dict( zeroline=False ),
        )
    )
    fig = dict( data=[scatter, clusters], layout=layout )
    return fig