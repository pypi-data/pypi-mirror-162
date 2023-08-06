import datetime as dt
import DE_DataBase as D
import pandas as pd
import json
import inspect


class PARAMETERS:

    NAME_CLASS = inspect.stack()[0].function

    def __init__(self, **kwargs):
        try:
            function_name = inspect.stack()[0].function
            db = D.DATABASE()
            self._cnn = db.SQLITE(kwargs["file_par"])
            self._nome_tabela = kwargs["nome_tabela"]
            self._PAR = self.coluna_get()
        except Exception as error:
            print(error)

    def coluna_get(self, coluna: str = None, valor: str = None, status: str = "A", now=dt.datetime.now()):
        df = None
        NAME_METHOD = inspect.stack()[0].function

        try:
            binds_var = {"status": status,
                         "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                         "column_name": coluna,
                         "column_value": valor
                         }

            if coluna is None:
                where_add = ""
            else:
                if valor is None:
                    binds_var["column_value"] = "Null"
                where_add = f"""and p.{binds_var["column_name"]} = ifnull({binds_var["column_value"]}, p.{binds_var["column_name"]})"""

            sql = f"""
                   select *
                     from {self._nome_tabela} p
                    where p.flg_status = '{binds_var["status"]}'
                      and '{binds_var["current_datetime"]}' between p.dat_ini_vigencia and p.dat_fim_vigencia
                      {where_add}
                  """
            df = pd.read_sql(con=self._cnn, sql=sql)
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Parametrs(s) obtido(s). linhas = {len(df)}"""
        except Exception as error:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar obter o(s) parametro(s) desejado.\nErro: {error}"""
        finally:
            return df

    def parametro_valor_hash(self, hash: str):
        valor_parametro = None
        NAME_METHOD = inspect.stack()[0].function
        try:
            index = self._PAR.index[self._PAR["hash"]==hash][0]
            #dfValor = self._PAR.loc[index, ["val_parametro", "par_datatype", "flg_nullable"]]
            VALOR = self._PAR.loc[index, "val_parametro"]
            DATATYPE = self._PAR.loc[index, "par_datatype"]
            NULLABLE = self._PAR.loc[index, "flg_nullable"]
            valor_parametro = self._parametro_datatype(value=VALOR, datatype=DATATYPE, nullable=NULLABLE)
        except Exception as error:
            valor_parametro = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar obter o valor para o hash: {hash}"""
        finally:
            return valor_parametro

    def _parametro_datatype(self, value=None, datatype: str = "STRING", nullable: str = 'N'):
        val_parametro = None
        NAME_METHOD = inspect.stack()[0].function
        try:
            if (value.strip() == "") or (value.strip() is None):
                if nullable == "S":
                    val_parametro = None
                else:
                    if datatype.upper() == "INTEGER":
                        val_parametro = 0
                    elif datatype.upper() == "REAL":
                        val_parametro = 0.0
                    elif datatype.upper() == "DATETIME":
                        val_parametro = dt.datetime.now()
                    elif datatype.upper() == "RECORD":
                        val_parametro = {}
                    elif datatype.upper() == "STRING":
                        val_parametro = {}
            else:
                if datatype.upper() == "INTEGER":
                    val_parametro = int(value)
                elif datatype.upper() == "REAL":
                    val_parametro = float(value)
                elif datatype.upper() == "DATETIME":
                    val_parametro = dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                elif datatype.upper() == "RECORD":
                    value = value.replace("\r\n", "")
                    value = value.replace("NONE", "null")
                    value = value.replace("None", "null")
                    value = value.replace("none", "null")
                    value = value.replace("NULL", "null")
                    #x = value.replace("\r\n", "").replace("Null", "null").replace("None", "null").replace("none", "null")
                    str_json = json.loads(value)
                    val_parametro = json.dumps(str_json, indent=2)
                elif datatype.upper() == "STRING":
                    val_parametro = str(value)
        except Exception as error:
            val_parametro = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar efetuar a conversao do datatype do valor do parametro: datatype={datatype}, valor={value}, flg_nullable = {nullable}\n{error}"""
        finally:
            return val_parametro

    def Update(self, par_dict):
        msg = None
        NAME_METHOD = inspect.stack()[0].function
        try:
            sql =   f"""Update {self._nome_tabela}
                           set val_parametro = :value
                         where hash = :hash
                           and flg_updateable = 'S'  
                    """
            cur = self._cnn.cursor()
            rows_count = cur.execute(sql, par_dict).rowcount
            if rows_count == 0:
                msg = f"""[hash: {par_dict["hash"]}, não localizado]. Nenhum linha alterada!"""
                raise Exception(msg)
            cur.close()
            self._cnn.commit()
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Parametro(s) atualizados!"""
        except self._cnn.DatabaseError as dbError:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Erro no banco de dados. {dbError}"""
        except Exception as error:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar atualizar (UPDATE) do parametro referenciado pelo hash: {par_dict["hash"]}, com o valor: {par_dict["value"]}\nErro: {error}"""
        finally:
            print(msg)
            return msg

    def Insert(self, record, commit: bool = true, commit_each_row: int = 1):
        try:
            pass
        except Exception as error:
            pass
        finally:
            pass

    def _insert_one(self, record: dict, commit: bool = True):
        msg = None
        NAME_METHOD = inspect.stack()[0].function
        try:
            sql = f"""Insert Into financialservices.akron_parametros
                                  (hash_parent
                                  ,des_parametro
                                  ,val_parametro
                                  ,des_datatype
                                  ,des_formato
                                  ,nom_parametro
                                  ,des_familia
                                  ,des_grupo
                                  ,nom_variavel
                                  ,flg_updateable
                                  ,flg_nullable
                                  ,flg_status
                                  ,dat_ini_vigencia
                                  ,dat_fim_vigencia
                                  ,dat_update
                                  ,des_comentarios)
                           values (:hash_parent
                                  ,:des_parametro
                                  ,:val_parametro
                                  ,:des_datatype
                                    ,:des_formato
                                  ,:nom_parametro
                                  ,:des_familia
                                  ,:des_grupo
                                  ,:nom_variavel
                                  ,:flg_updateable
                                  ,:flg_nullable
                                  ,:flg_status
                                  ,:dat_ini_vigencia
                                  ,:dat_fim_vigencia
                                  ,:dat_update
                                  ,:des_comentarios)
                  """
            cur = self._cnn.cursor()
            rows_count = cur.execute(sql, record).rowcount
            if rows_count == 0:
                msg = f"""[hash: {par_dict["hash"]}, não localizado]. Nenhum linha alterada!"""
                raise Exception(msg)
            cur.close()
            if commit:
                self._cnn.commit()
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Parametro(s) atualizados!"""
        except self._cnn.DatabaseError as dbError:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Erro no banco de dados. {dbError}"""
        except Exception as error:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar atualizar (UPDATE) do parametro referenciado pelo hash: {par_dict["hash"]}, com o valor: {par_dict["value"]}\nErro: {error}"""
        finally:
            return msg

    def _insert_many(self, record_list: list, commit_each_rows: int = 1):
        msg = None
        NAME_METHOD = inspect.stack()[0].function
        try:
            num_rows = 0
            for row in record_list:
                num_rows += 1
                if commit_each_rows == 1:
                    self.Insert(row) # commit a cada linha executada
                else:
                    if num_rows % commit_each_rows == 0:
                        self.Insert(row, commit=True)
                    else:
                        self.Insert(row, commit=False)

            if rows_count == 0:
                msg = f"""[hash: {par_dict["hash"]}, não localizado]. Nenhum linha alterada!"""
                raise Exception(msg)
            cur.close()
            self._cnn.commit()
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Parametro(s) atualizados!"""
        except self._cnn.DatabaseError as dbError:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Erro no banco de dados. {dbError}"""
        except Exception as error:
            msg = f"""[{self.NAME_CLASS}.{NAME_METHOD}]-Falha ao tentar atualizar (UPDATE) do parametro referenciado pelo hash: {par_dict["hash"]}, com o valor: {par_dict["value"]}\nErro: {error}"""
        finally:
            return msg

    @property
    def parametros_df(self):
        return self._PAR

    @property
    def DataTypes(self) -> list:
        return ["STRING", "RECORD", "INTEGER", "REAL", "DATETIME"]

if __name__ == "__main__":
    par = dict(file_par="c:/Projetos/db/AKRON.db", nome_tabela="Parametros_AKRON")
    p = PARAMETERS(**par)
    hash = 1
    #valor_parametro = p.parametro_valor_hash(hash)
    #print(valor_parametro)
    p.Update({"hash": hash, "value": "0"})

