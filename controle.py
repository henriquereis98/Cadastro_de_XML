#Importa todas as bibliotecas necessárias para a execução do código!
from PyQt5 import uic, QtWidgets, QtGui, QtCore
import mysql.connector
import datetime
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import resources_from_qt_rc
import os

try:
    #conexão com o banco de dados!
    banco = mysql.connector.connect(
    host="192.168.1.121",
    user="root",
    passwd="",
    database="cadastroxml"
)
except mysql.connector.Error as error:
    # Tratamento da exceção de conexão com o banco de dados
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(f"Erro ao conectar com o banco de dados: {str(error)}")
    msg.setWindowTitle("Erro de Conexão")
    msg.exec_()

def gerar_pdf(xml, conferente):
    cursor = banco.cursor()
    comando_SQL = "SELECT * FROM cadastroxml WHERE xml LIKE %s AND conferente LIKE %s"
    filter_values = ('%' + xml + '%', '%' + conferente + '%')
    cursor.execute(comando_SQL, filter_values)
    dados_lidos = cursor.fetchall()

    # Configuração do tamanho da página
    page_width, page_height = letter

    # Configuração das margens
    left_margin = 50
    bottom_margin = 50
    top_margin = 50

    # Obtém o caminho da pasta de área de trabalho
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # Define o caminho completo do arquivo PDF
    pdf_path = os.path.join(desktop_path, "relatorio_xml.pdf")

    # Organiza as informações filtradas no documento PDF
    y = page_height - top_margin
    line_height = 12
    records_per_page = 50  # Quantidade máxima de registros por página

    pdf = canvas.Canvas(pdf_path, pagesize=letter)

    pdf.setFont("Times-Bold", 25)
    pdf.drawString(left_margin, y, "Relatório de XML")

    pdf.setFont("Times-Bold", 10)
    y -= 50  # Espaço para o cabeçalho

    pdf.drawString(left_margin, y, "XML")
    pdf.drawString(left_margin + 250, y, "Conferente")
    pdf.drawString(left_margin + 350, y, "Outro")
    pdf.drawString(left_margin + 450, y, "Data de Entrada")

    y -= line_height

    for i, dados in enumerate(dados_lidos):
        if i != 0 and i % records_per_page == 0:
            # Adicionar nova página
            pdf.showPage()
            y = page_height - top_margin - line_height

            pdf.setFont("Times-Bold", 10)
            pdf.drawString(left_margin, y, "XML")
            pdf.drawString(left_margin + 250, y, "Conferente")
            pdf.drawString(left_margin + 350, y, "Outro")
            pdf.drawString(left_margin + 450, y, "Data de Entrada")

            y -= line_height

        pdf.setFont("Times-Roman", 10)
        pdf.drawString(left_margin, y, str(dados[0]))
        pdf.drawString(left_margin + 250, y, str(dados[1]))
        pdf.drawString(left_margin + 350, y, str(dados[2]))
        pdf.drawString(left_margin + 450, y, str(dados[3]))

        y -= line_height

    pdf.save()
    print("PDF salvo com sucesso!")

    QMessageBox.information(None, "Sucesso", "PDF salvo com sucesso em: " + pdf_path)

#Função principal(formulario.ui)!
def funcao_principal():
    linha1 = formulario.xml.text()
    selected_value = formulario.conferente.currentText()
    linha3 = formulario.outro.text()

    if linha1 and selected_value:  # Verifica se os campos obrigatórios estão preenchidos
        print("Código XML:", linha1)
        print("Conferente:", selected_value)

        #Exibir mensagem de erro caso o campo outro não seja preenchido!
        if selected_value == "Outro" and not linha3:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Digite o seu nome no campo 'Outro'!")
            msg.setWindowTitle("Erro")
            msg.exec_()
            return

        print("Outro:", linha3)

        cursor = banco.cursor()

        # Verificar se o XML já existe no banco de dados
        comando_verificar = "SELECT * FROM cadastroxml WHERE xml = %s"
        cursor.execute(comando_verificar, (linha1,))
        resultado = cursor.fetchall()
        if resultado:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("O XML já existe no banco de dados.")
            msg.setWindowTitle("Erro")
            msg.exec_()

            
            return

        # Adicionar a data atual
        data_atual = datetime.datetime.now()
        formato_data = "%d/%m/%Y"
        data_entrada = data_atual.strftime(formato_data)


        #Insere os dados no banco de dados!
        comando_SQL = "INSERT INTO cadastroxml (xml, conferente, outro, data_entrada) VALUES (%s, %s, %s, %s)"
        dados = (str(linha1), selected_value, str(linha3), data_entrada)
        cursor.execute(comando_SQL, dados)
        banco.commit()

        #Limpa os campos após salvar no banco de dados!
        formulario.xml.clear()
        formulario.conferente.setCurrentIndex(-1)
        formulario.outro.clear()

        #Exibe mensagem de sucesso após salvar os dados corretamente no banco de dados!
        success_msg = QtWidgets.QMessageBox()
        success_msg.setIcon(QtWidgets.QMessageBox.Information)
        success_msg.setText("XML salvo com sucesso.")
        success_msg.setWindowTitle("Sucesso")
        success_msg.exec_()

        formulario.xml.setFocus()

    #Exibe mensagem de erro caso tente salvar no banco de dados se preencher algum dos dois campos abaixo!
    else:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Os campos 'XML' e 'Conferente' são obrigatórios.")
        msg.setWindowTitle("Erro")
        msg.exec_()


#Função para validar a linha1(xml) no formulario.ui!
def validar_linha1():
    linha1 = formulario.xml.text()
    if linha1 and not linha1.isdigit():
        cursor_position = formulario.xml.cursorPosition()
        formulario.xml.setText(''.join(filter(str.isdigit, linha1)))
        formulario.xml.setCursorPosition(cursor_position - 1)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Digite apenas números no campo 'XML'.")
        msg.setWindowTitle("Erro")
        msg.exec_()

#Função para validar a linha3(outro) no formulario.ui!
def validar_linha3():
    linha3 = formulario.outro.text()
    if any(char.isdigit() for char in linha3):
        cursor_position = formulario.outro.cursorPosition()
        formulario.outro.setText(''.join(filter(str.isalpha, linha3)))
        formulario.outro.setCursorPosition(cursor_position - 1)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Digite apenas letras no campo 'Outro'.")
        msg.setWindowTitle("Erro")
        msg.exec_()

#Função para chamar a segunda tela(listar_dados)
def chama_segunda_tela():
    segunda_tela.show()

    cursor = banco.cursor()
    comando_SQL = "SELECT * FROM cadastroxml"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()
    
    segunda_tela.tableWidget.setRowCount(len(dados_lidos))
    segunda_tela.tableWidget.setColumnCount(6)
    
    for i in range(0, len(dados_lidos)):
        for j in range(0, 6):
            segunda_tela.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))
        

# Função para chamar o visto ao pressionar Enter
def keyPressEvent(event):
    if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
        linha1 = visto.xml.text()

    cursor = banco.cursor()
    comando_SQL = "SELECT visto FROM cadastroxml WHERE xml = %s"
    cursor.execute(comando_SQL, (linha1,))
    resultado = cursor.fetchone()

    if not resultado:
            # Exibe a mensagem de erro
            QMessageBox.critical(None, "Erro", "XML não cadastrado no banco de dados.")
            return
        

    if resultado and resultado[0] != '':
        # Um valor já está atribuído ao campo "Visto"
        QMessageBox.information(None, "Aviso", "O XML digitado já possui um Visto!")
        return

    visto_selecionado = ""  # Inicialização da variável visto_selecionado

    if visto.pietro.isChecked():
        visto_selecionado = "Pietro"
    elif visto.henrique.isChecked():
        visto_selecionado = "Henrique"

    data_atual = datetime.datetime.now()
    formato_data = "%Y-%m-%d %H:%M:%S"
    data_visto = data_atual.strftime(formato_data)

    comando_SQL = "UPDATE cadastroxml SET visto = %s, data_visto = %s WHERE xml = %s"
    dados = (visto_selecionado, data_visto, linha1)
    cursor.execute(comando_SQL, dados)
    banco.commit()

    visto.xml.setText("")
    visto.xml.setFocus()
    QMessageBox.information(None, "Sucesso", "Visto salvo com sucesso!")
    
#Função para chamar o visto!
def chama_visto():
    linha1 = visto.xml.text()

    cursor = banco.cursor()
    comando_SQL = "SELECT visto FROM cadastroxml WHERE xml = %s"
    cursor.execute(comando_SQL, (linha1,))
    resultado = cursor.fetchone()

    if not resultado:
            # Exibe a mensagem de erro
            QMessageBox.critical(None, "Erro", "XML não cadastrado no banco de dados.")
            return
        

    if resultado and resultado[0] != '':
        # Um valor já está atribuído ao campo "Visto"
        QMessageBox.information(None, "Aviso", "O XML digitado já possui um Visto!")
        return

    visto_selecionado = ""  # Inicialização da variável visto_selecionado

    if visto.pietro.isChecked():
        visto_selecionado = "Pietro"
    elif visto.henrique.isChecked():
        visto_selecionado = "Henrique"

    data_atual = datetime.datetime.now()
    formato_data = "%Y-%m-%d %H:%M:%S"
    data_visto = data_atual.strftime(formato_data)

    comando_SQL = "UPDATE cadastroxml SET visto = %s, data_visto = %s WHERE xml = %s"
    dados = (visto_selecionado, data_visto, linha1)
    cursor.execute(comando_SQL, dados)
    banco.commit()

    visto.xml.setText("")
    visto.xml.setFocus()
    QMessageBox.information(None, "Sucesso", "Visto salvo com sucesso!")


#Função para filtrar os dados conforme digitado nos campos!   
def filtrar_dados():
    xml = segunda_tela.xml.text()
    conferente = segunda_tela.conferente.text()

    cursor = banco.cursor()
    comando_SQL = "SELECT * FROM cadastroxml WHERE xml LIKE %s AND conferente LIKE %s"
    filter_values = ('%' + xml + '%', '%' + conferente + '%')
    cursor.execute(comando_SQL, filter_values)
    dados_lidos = cursor.fetchall()

    segunda_tela.tableWidget.setRowCount(len(dados_lidos))
    segunda_tela.tableWidget.setColumnCount(6)

    for i in range(0, len(dados_lidos)):
        for j in range(0, 6):
            segunda_tela.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))

# Responsável pela execução e loop do aplicativo
app = QtWidgets.QApplication([])

# Faz referência do formulário com a função
formulario = uic.loadUi("formulario.ui")
segunda_tela = uic.loadUi("listar_dados.ui")
visto = uic.loadUi("visto.ui")
visto.pietro.setChecked(True)


# Conecta o botão "Visto" ao método chama_visto
visto.visto.clicked.connect(chama_visto)

visto.keyPressEvent = keyPressEvent

# Cuida das execuções dos botões, tamanho dos campos, etc.
formulario.xml.setMaxLength(44)
formulario.conferente.setCurrentIndex(-1)
formulario.salvar.clicked.connect(funcao_principal)
formulario.pesquisar.clicked.connect(chama_segunda_tela)
formulario.visto.clicked.connect(visto.show)
formulario.xml.textChanged.connect(validar_linha1)
formulario.outro.textChanged.connect(validar_linha3)
segunda_tela.gerarpdf.clicked.connect(lambda: gerar_pdf(segunda_tela.xml.text(), segunda_tela.conferente.text()))

# Conecta o botão de pesquisa em listar_dados.ui à função filtrar_dados
segunda_tela.pesquisar.clicked.connect(filtrar_dados)

formulario.show()
app.exec()