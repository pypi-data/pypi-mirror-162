import DE_DataBase as D
import DE_LibUtil as U


utl = U.LIB()
db = D.DATABASE()


file_parametros =r"C:/Projetos/db/AKRON.db"

cnnPAR = db.SQLITE(file_parametros)

dfPAR = utl.get_parametros_geral(cnnPAR)

for index, row in dfPAR.iterrows():
    utl.s
    print(f"""Nome: {row.nom_parametro}, "valor: {row.val_parametro}""")

