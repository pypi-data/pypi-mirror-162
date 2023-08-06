import DE_DataBase as D
import DE_Parametros as P
import tkinter as tk
import datetime as dt
import time as tm
import pandas as pd

class Form:
    def __init__(self):
        pass

    def OBTEM_FAMILIA_PARAMETROS(self):
        try:
            db = D.DATABASE()
            cnn = db.SQLITE("C:/Projetos/db/AKRON.db")
            PAR = {"conexao": cnn, "table": "parametros"}
            par = P.PARAMETROS(**PAR)
            PAR = par.APLICACAO_get(["TEMPLATE"])
        except Exception as error:
            PAR = error
        finally:
            cnn.close()
            return PAR

    def Monta_json(self, event = None):
        evento = event.keysym.lower()
        nomecaixa = event.widget.winfo_name()
        conteudocaixa = event.widget.get()
        print(f""" "{nomecaixa}": "{conteudocaixa}" """)

    def frmTemplate(self):
        try:
            frm = tk.Tk()
            frm.title("Cadastro Tabelas Candidatas")
            frm.geometry("850x600")

            df = pd.DataFrame(self.OBTEM_FAMILIA_PARAMETROS())
            #print(df)
            label = []
            entry = []
            linha = 0
            get = {}
            for index, row in df.iterrows():
                linha = linha + 1
                lbl = tk.Label(frm, text=row.val_parametro)
                lbl.grid(row=linha, column=0, padx=10, pady=3, sticky='nswe')
                #linha = linha + 1
                entry = tk.Entry(frm, width=50, name=row.val_parametro)
                entry.grid(row=linha, column=2, padx=10, pady=3, sticky='nswe')
                entry.bind("<Return>", self.Monta_json)
                entry.get()
            lbl = tk.Label(frm, text="Json")
            lbl.grid(row=linha+1, column=0, padx=10, pady=3, sticky='nswe', columnspan=2)
            txt = tk.Text(frm, height=12, width=30)
            txt.grid(row=linha+1, column=2)
            #txt.pack()
            btn = tk.Button(frm, text="Gerar Json")
            btn.place(x=150, y=410)
            #btn.pack()
            frm.mainloop()
        except Exception as error:
            print(error)
        finally:
            pass



# frm = tk.Tk()
# frm.title("Cadastro Tabelas Candidatas")
# frm.geometry("600x300")
#
# lbl_owner = tk.Label(text="Owner da tabela:")
# lbl_owner.grid(row=1, column=0, padx=10, pady=10, sticky='nswe', columnspan=4)
#
# get_owner = tk.Entry()
# get_owner.grid(row=2, column=0, padx=10, pady=10, sticky='nswe', columnspan=1)
#
#
# frm.mainloop()

if __name__ == "__main__":
    f = Form()
    f.frmTemplate()