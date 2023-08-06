import datetime as dt
import DE_DataBase as D
import DE_LibUtil as U
import pandas as pd
import json
import inspect
import ast
import datetime as dt

class PARAMETROS:

    NAME_CLASS = inspect.stack()[0].function

    def __init__(self, **kwargs):
        msg = None
        function_name = inspect.stack()[0].function
        try:
            db = D.DATABASE()
            #self._cnn = db.SQLITE(kwargs["database"])
            self._cnn = kwargs["conexao"]
            self._nome_tabela = kwargs["table"]
        except Exception as error:
            pass
        finally:
            pass

    def _insert_rows(self, rows: list, commit: bool = True):
        msg = None
        function_name = inspect.stack()[0].function
        utl = U.LIB()
        try:
            dml =   f"""
                    Insert into {self._nome_tabela}
                                (hash            
                                ,hash_parent     
                                ,num_ordem       
                                ,des_aplicacao     
                                ,des_grupo       
                                ,nom_parametro   
                                ,nom_variavel    
                                ,val_parametro   
                                ,des_datatype    
                                ,des_parametro   
                                ,flg_status      
                                ,flg_nullable    
                                ,flg_updateable  
                                ,dat_ini_vigencia
                                ,dat_fim_vigencia
                                ,dat_update)
                         values (:hash            
                                ,:hash_parent     
                                ,:num_ordem       
                                ,:des_aplicacao     
                                ,:des_grupo       
                                ,:nom_parametro   
                                ,:nom_variavel    
                                ,:val_parametro   
                                ,:des_datatype    
                                ,:des_parametro   
                                ,:flg_status      
                                ,:flg_nullable    
                                ,:flg_updateable  
                                ,:dat_ini_vigencia
                                ,:dat_fim_vigencia
                                ,:dat_update)
                    """
            cur = self._cnn.cursor()
            cur.executemany(dml, rows)
            cur.close()
            if commit:
                self._cnn.commit()

            msg = f"""Registro(s) incluido(s) com sucesso!"""
        except Exception as error:
            msg = f"""Não foi possivel incluir o(s) registro(s). Motivo: {error}"""
        finally:
            return msg

    def _update_row(self, row: dict, commit: bool = True):
        msg = None
        function_name = inspect.stack()[0].function
        utl = U.LIB()
        try:
            dml =  f"""UPDATE {self._nome_tabela} SET %s = '%s'" %(.join({row.keys()}), .join({row.values()}))"""
            dml =   f"""
                      Update {self._nome_tabela}
                         set hash_parent        = :hash_parent          
                            ,num_ordem       	= :num_ordem       
                            ,des_aplicacao        = :des_aplicacao     
                            ,des_grupo          = :des_grupo       
                            ,nom_parametro      = :nom_parametro   
                            ,nom_variavel       = :nom_variavel    
                            ,val_parametro      = :val_parametro   
                            ,des_datatype       = :des_datatype    
                            ,des_parametro      = :des_parametro   
                            ,flg_status         = :flg_status      
                            ,flg_nullable       = :flg_nullable    
                            ,flg_updateable     = :flg_updateable  
                            ,dat_ini_vigencia   = :dat_ini_vigencia
                            ,dat_fim_vigencia   = :dat_fim_vigencia
                            ,dat_update         = :dat_update
                       where hash = :hash 
                    """
            cur = self._cnn.cursor()
            cur.execute(dml, row)
            cur.close()
            if commit:
                self._cnn.commit()
            msg = f"""Registro alterado com sucesso!"""
        except Exception as error:
            msg = f"""Não foi possivel alterar o registro. Motivo: {error}"""
        finally:
            return msg

    def _delete_row(self, hash: str, commit: bool = True):
        msg = None
        function_name = inspect.stack()[0].function
        utl = U.LIB()
        try:
            dml = f"""
                      Delete from {self._nome_tabela}                             
                       where hash = '{hash}'
                    """
            cur = self._cnn.cursor()
            cur.execute(dml)
            if commit:
                self._cnn.commit()
            cur.close()
            msg = f"""Registro deletado com sucesso!"""
        except Exception as error:
            msg = f"""Não foi possivel deletar o registro. Motivo: {error}"""
        finally:
            return msg

    def APLICACAO_get(self, des_aplicacao: list = None) -> dict:
        result, where_add = None, None
        try:
            utl = U.LIB()
            now = dt.datetime.now()
            separador_listas = "|"
            if des_aplicacao is None:
                where_add = ""
            else:
                where_add = f"""and p.des_aplicacao in ('{"','".join(des_aplicacao)}')"""
            stmt =  f"""
                    Select *
                      from {self._nome_tabela} p
                     where dat_fim_vigencia = '31-12-9999 23:59:59'
                       and p.Dat_ini_vigencia <= '{now.strftime("%Y-%m-%d %H:%M:%S")}'
                       and p.flg_status = 'A'
                       {where_add}
                     order by p.des_aplicacao
                    """
            cur = self._cnn.cursor()
            cur.execute(stmt)
            columns = [column[0] for column in cur.description]
            rs = []
            PAR = {}
            # populando o ResultSet (rs)
            for row in cur.fetchall():
                #rs.append(dict(zip(columns, row)))
                rs.append(dict(zip(columns, row)))
                #PAR.append(rs["nom_variavel"]}] = rs["val_parametro"]
            # avalidando os DataTypes para o ResultSet
            for row in rs:
                if row["flg_encrypt"] == "S":
                    token_string = self.VARIAVEL_get(["GERAL_TOKEN_BASE"])[0]
                    row["val_parametro"] = utl.CRYPTOGRAPHY(word=row["val_parametro"], token=token_string)
                if row["des_datatype"] == "DATETIME":
                    row["val_parametro"] = dt.datetime.strptime(utl.iif(row["val_parametro"] is None, "", row["val_parametro"]), "%Y-%m-%d %H:%M:%S")
                elif row["des_datatype"] == "DATE":
                    row["val_parametro"] = dt.datetime.strptime(utl.iif(row["val_parametro"] is None, "", row["val_parametro"]), "%Y-%m-%d")
                elif row["des_datatype"] == "TIME":
                    row["val_parametro"] = dt.datetime.strptime(utl.iif(row["val_parametro"] is None, "", row["val_parametro"]), "%H:%M:%S")
                elif row["des_datatype"] == "INTEGER":
                    row["val_parametro"] = int(utl.iif(row["val_parametro"] is None, "0", row["val_parametro"]))
                elif row["des_datatype"] == "LIST":
                    row["val_parametro"] = row["val_parametro"].split(separador_listas)
                elif row["des_datatype"] == "JSON":
                    row["val_parametro"] = ast.literal_eval(row["val_parametro"])
                elif row["des_datatype"] == "LIST/JSON":
                    row["val_parametro"] = row["val_parametro"].split(separador_listas)
                    for i in range(len(row["val_parametro"])):
                        row["val_parametro"][i] = ast.literal_eval(row["val_parametro"][i])
        except Exception as error:
            rs = f"""Falha na obtenção dos parametros para a FAMILIA de PARAMETROS: {des_aplicacao}.\nErro: {error}"""
        finally:
            return rs

    def VARIAVEL_get(self, nom_parametro: list) -> list:
        result, where_add, values = None, None, None
        try:
            now = dt.datetime.now()
            if nom_parametro is None:
                where_add = ""
            else:
                where_add = f"""and p.nom_parametro in ('{"','".join(nom_parametro)}')"""
            stmt =  f"""
                    Select *
                      from {self._nome_tabela} p
                     where dat_fim_vigencia is Null
                       and p.Dat_ini_vigencia <= '{now.strftime("%Y-%m-%d %H:%M:%S")}'
                       and p.flg_status = 'A'
                       {where_add}
                     order by p.nom_parametro
                    """
            cur = self._cnn.cursor()
            cur.execute(stmt)
            columns = [column[0] for column in cur.description]
            rs = []
            # populando o ResultSet (rs)
            for row in cur.fetchall():
                rs.append(dict(zip(columns, row)))
            # avalidando os DataTypes para o ResultSet
            values = []
            for row in rs:
                if row["des_datatype"] == "JSON":
                    row["val_parametro"] = ast.literal_eval(row["val_parametro"])
                if isinstance(row["val_parametro"], bytes):
                    values.append(row["val_parametro"].decode())
                else:
                    values.append(row["val_parametro"])
        except Exception as error:
            values = f"""Falha na obtenção dos parametros para a nom_parametro: {nom_parametro}.\nErro: {error}"""
        finally:
            return values

    def REPLICA_APLICACAO(self, des_aplicacao_origem: str, des_aplicacao_destino: str, commit: bool = True):
        try:
            stmt = f"""Select *
                         from {self._nome_tabela}
                        where nom_familia = :nom_familia  
                   """
            cur = self._cnn.cursor()
            cur.execute(stmt)
            rows = cur.fetchmany()
            for row in rows:
                pass
            cur.close()
            if commit:
                self._cnn.commit()
        except Exception as error:
            pass
        finally:
            pass

    def INSERT_ROWS(self, row: list):
        msg = self._insert_rows(row)
        return msg

    def UPDATE_ROW(self, row: dict):
        msg = self._update_row(row)
        return msg

    def DELETE_ROW(self, hash: str):
        msg = self._delete_row(hash)
        return msg

    def _oracle_DDL(self):
        try:
            stmt = f"""
                    (hash               VARCHAR2(256)   PRIMARY KEY NOT NULL UNIQUE,
                    hash_parent         VARCHAR2(256),
                    num_ordem           VARCHAR (10)   DEFAULT ('0'),
                    des_aplicacao         VARCHAR (30)   NOT NULL,
                    des_grupo           VARCHAR (30)   NOT NULL,
                    nom_parametro       VARCHAR2(256)  UNIQUE NOT NULL,
                    nom_variavel        VARCHAR2 (256) NOT NULL
                    val_parametro       CLOB,
                    des_datatype        STRING         NOT NULL,
                    des_parametro       VARCHAR2 (500),
                    flg_status          VARCHAR (10)   NOT NULL DEFAULT ('A'),
                    flg_nullable        VARCHAR (10)   NOT NULL DEFAULT ('N'),
                    flg_updateable      VARCHAR (10)   DEFAULT ('N') NOT NULL,
                    dat_ini_vigencia    DATE           DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                    dat_fim_vigencia    DATE,
                    dat_update          TIMESTAMP      NOT NULL DEFAULT (CURRENT_TIMESTAMP) 
                    """
            cur = self._cnn.cursor()
            cur.execute(stmt)
            cur.close()
        except Exception as error:
            pass
        finally:
            pass

    def _sqlite_DDL(self):
        try:
            stmt =  f"""
                    CREATE TABLE {self._nome_tabela} 
                    (hash               TEXT    PRIMARY KEY NOT NULL UNIQUE,
                    hash_parent         TEXT,
                    num_ordem           VARCHAR (10)   DEFAULT ('0'),
                    des_aplicacao         VARCHAR (30),
                    des_grupo           VARCHAR (30),
                    nom_parametro       TIME (256),
                    nom_variavel        VARCHAR2 (256) UNIQUE NOT NULL,
                    val_parametro       TEXT,
                    des_datatype        STRING  NOT NULL,
                    des_parametro       VARCHAR2 (500),
                    flg_status          VARCHAR (10)   NOT NULL DEFAULT ('A'),
                    flg_nullable        VARCHAR (10)   NOT NULL DEFAULT ('N'),
                    flg_updateable      VARCHAR (10)   DEFAULT ('N') NOT NULL,
                    dat_ini_vigencia    DATETIME       DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                    dat_fim_vigencia    DATETIME,
                    dat_update          DATETIME       NOT NULL DEFAULT (CURRENT_TIMESTAMP) 
                    )
                    """
            cur = self._cnn.cursor()
            cur.execute(stmt)
            cur.close()
        except Exception as error:
            pass
        finally:
            pass


