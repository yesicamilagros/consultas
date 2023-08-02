from fastapi import FastAPI
import pandas as pd
import uvicorn 
from datetime import datetime
from scipy import spatial
from ast import literal_eval
import operator
#from starlette.responses import RedirectResponse

app=FastAPI(title='Consulta de FILMS')

@app.get("/")

def funcion():
  return "hola mundo"

def dayofweek(d, m, y):
    ''' funcion para hallar el numero de dia 0,1,2,3,4,5,6
    dic={1:'lunes',2:'martes',3:'miercoles',4:'jueves',5:'viernes',6:'sabado',0:'domingo'}'''
    t = [ 0, 3, 2, 5, 0, 3,
          5, 1, 4, 6, 2, 4 ]
    y -= m < 3
    return (( y + int(y / 4) - int(y / 100)
             + int(y / 400) + t[m - 1] + d) % 7)


pf22=pd.read_csv(r'dataset/get_actor.csv')
pf_titulo=pd.read_csv(r'dataset/score_titulo.csv')
pf_votos_titulo=pd.read_csv(r'dataset/votos_titulo.csv')
pf_date=pd.read_csv(r'dataset/cantidad_filmaciones_dia.csv')
pf_director=pd.read_csv(r'dataset/get_director.csv')
movies=pd.read_csv(r'dataset/movies1.csv')

@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):

    '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente'''
    qmes=mes.lower()
    meses=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    if qmes in meses:
        nmes = meses.index(qmes) + 1
    else:
        nmes=0    
    
    nmes = 9 if 'setiembre' in mes else nmes
    
    if nmes == 0:
        respuesta = {'mes no definido'}
        return respuesta  
    

    pf_date["release_month"] = pf_date["release_date"].apply(lambda x: x[5:7]).astype('int')
    respuesta = pf_date.loc[pf_date["release_month"] == nmes].shape[0]
    
    return {'mes':mes, 'cantidad de filmaciones':str(respuesta)} 

def Similarity(movieId1, movieId2): 
    a = movies.iloc[movieId1]
    b = movies.iloc[movieId2]
    genresA = a['genres_bin']
    genresB = b['genres_bin']
    
    genreDistance = spatial.distance.cosine(genresA, genresB)

    return genreDistance

@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia:str):
    '''Se ingresa el dia y la funcion retorna  la cantidad de películas que fueron estrenadas el día de la semana
       p.ej : dia :martes , out : {'dia':'martes, 'cantidad':3456}'''
    day=dia.lower() 
    dic={0:'domingo',1:'lunes',2:'martes',3:'miercoles',4:'jueves',5:'viernes',6:'sabado'}
    k=0
    if day in list(dic.values()):
      for i in pf_date['release_date']:
        if dic[dayofweek(datetime.strptime(i, "%Y-%m-%d").day,datetime.strptime(i, "%Y-%m-%d").month , datetime.strptime(i, "%Y-%m-%d").year)]==day:
            k=k+1
      return {'dia' : day, 'cantidad de filmaciones':k}
    else:
      return ' dia no  definida' 


@app.get('/score_titulo/{titulo_de_la_filmacion}') #aquie
def score_titulo(titulo_de_la_filmacion:str):   
  '''se ingresa  el titulo de la filmacion y la funcion retorna , titulo de la filmacion , año de estreno , score , p,ej. titulo_de_la_filmacion 
   :Jumanji ,out  'titulo':Jumanji,  'año de estreno':1995,  'score': 17.015539'''
  ti=titulo_de_la_filmacion.strip()
  for i in range(len(pf_titulo['title'])):
     if pf_titulo['title'][i]==ti:
        return {'titulo':ti ,'año de estreno':str(pf_titulo['release_year'][i]),'score':str(pf_titulo['popularity'][i])}  
    


@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):  
  '''Se ingresa el título de una filmación esperando como respuesta el título,
   la cantidad de votos y el valor promedio de las votaciones. '''
  t=titulo.strip()
  if t in list(pf_votos_titulo['title']):
        if pf_votos_titulo['vote_count_max'][list(pf_votos_titulo[pf_votos_titulo['title']==t].index.values)[0]]>2000:
           return {'nombre de la pelicula estrenada':t,'año': str(pf_votos_titulo['release_year'][list(pf_votos_titulo[pf_votos_titulo['title']==t].index.values)[0]]),'cantidad de votos':str(pf_votos_titulo['vote_count_max'][list(pf_votos_titulo[pf_votos_titulo['title']==t].index.values)[0]]),'voto promedio':str(pf_votos_titulo['vote_average_prom'][list(pf_votos_titulo[pf_votos_titulo['title']==t].index.values)[0]])}
        else:  
            return {'vote_count<=2000'}
  else:
        return 'no registrado'

@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor:str):  
  '''Se ingresa el título de una filmación esperando como respuesta el título,
   la cantidad de votos y el valor promedio de las votaciones. '''
  #pf2 limpio funcion para hallar la suma y retorn
  try:
       s=0
       h=0
       for i in range(len(pf22['actores'])):
          if pf22['actores'][i]==nombre_actor:
             s=s + pf22['promedio_return'][i]
             h=h+1
       return {'nombre del actor':nombre_actor ,'numero de filmaciones':h ,'retorno_total':s,'retorno_promedio': s/h}
  except:
         return {'actor no registrado'}

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):  
  '''Se ingresa el título de una filmación esperando como respuesta el título,
   la cantidad de votos y el valor promedio de las votaciones. '''
  try:
   p=0
   o=0
   l=[]
   for i in range(len(pf_director['directores'])):
      if pf_director['directores'][i]==nombre_director:
          l.append(dict(zip(['filmacion','fecha_estreno','retorno','costo','ganancia'],[pf_director['title'][i],pf_director['release_date'][i],pf_director['return'][i],pf_director['budget'][i],pf_director['revenue'][i]])))
          p=p+pf_director['return'][i]
          o=o+1
   return {'nombre del director':nombre_director,'retorno de exito':p/o,'filmaciones':l}  

  except:
         return {'director no registrado'}

# ML

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):  
  '''Se ingresa el título de una filmación esperando como respuesta el título,
   la cantidad de votos y el valor promedio de las votaciones. '''
  try:
   p=0
   o=0
   l=[]
   for i in range(len(pf_director['directores'])):
      if pf_director['directores'][i]==nombre_director:
          l.append(dict(zip(['filmacion','fecha_estreno','retorno','costo','ganancia'],[pf_director['title'][i],pf_director['release_date'][i],pf_director['return'][i],pf_director['budget'][i],pf_director['revenue'][i]])))
          p=p+pf_director['return'][i]
          o=o+1
   return {'nombre del director':nombre_director,'retorno de exito':p/o,'filmaciones':l}  

  except:
         return {'director no registrado'}

@app.get('/get_recomendacion/{titulo_film}')
def predict_score(titulo_film:str):  
  '''Se ingresa el título de una filmación esperando como respuesta similitudes con la filmacion . '''
    #name = input('Enter a movie title: ')
  movies['genres_bin'] = movies.genres_bin.apply(lambda x: literal_eval(str(x)))
  movies['genres'] = movies.genres.apply(lambda x: literal_eval(str(x)))
  new_movie = movies[movies['title'].str.contains(titulo_film)].iloc[0].to_frame().T
  print('eleccion de la pelicula: ',new_movie.title.values[0])
  def getNeighbors(baseMovie, K):
        distances = []
    
        for index, movie in movies.iterrows():
            if movie['new_id'] != baseMovie['new_id'].values[0]:
                dist = Similarity(baseMovie['new_id'].values[0], movie['new_id'])
                distances.append((movie['new_id'], dist))
    
        distances.sort(key=operator.itemgetter(1))
        neighbors = []
    
        for x in range(K):
            neighbors.append(distances[x])
        return neighbors
  K = 5
  avgRating = 0
  neighbors = getNeighbors(new_movie, K) 
  print('\n peliculas recomendadas: \n')
  for neighbor in neighbors:
      avgRating = avgRating+movies.iloc[neighbor[0]][2]  
      print( movies.iloc[neighbor[0]][0]+" | Generos: "+str(movies.iloc[neighbor[0]][1]).strip('[]').replace(' ','')+" | Rating: "+str(movies.iloc[neighbor[0]][2]))
   
 
  return {'pelculas recomendadas':[movies.iloc[neighbors[0]],movies.iloc[neighbors[1]],movies.iloc[neighbors[2]],movies.iloc[neighbors[3]],movies.iloc[neighbors[4]]]}
