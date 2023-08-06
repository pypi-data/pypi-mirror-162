import DE_DataBase as D
import DE_LibUtil as U
import DE_LogEventos as L
import json
import ast


utl = U.LIB()
db = D.DATABASE()

log_par = r"C:/Projetos/db/AKRON.db"

log = {"device_out": ["screen", "file"],
       "nome_tabela_log": None,
       "nome_tabela_log_evento": None,
       "conexao_log": None,
       "file": r"c:\Projetos\files\LogFiles\Teste_DBConnect.log"}
log = L.LOG(**log)

#-----------------------------------------------------
logger = log.Inicializa()

cnnPAR = db.SQLITE(log_par)
dfPAR = utl.get_parametros_geral(conexao=cnnPAR)
print(dfPAR.info())
dfFamilia = utl.get_parametros_familia(dfPAR, "GERAL")
dfGrupo = utl.get_parametros_grupo(dfPAR, "path")
token = utl.get_parametro_valor(dfPAR, "TOKEN_DB")
path = utl.get_parametro_valor(dfPAR, "PATH")
path_list = ast.literal_eval(path)
log.Finaliza(logger)
#-----------------------------------------------------






