from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QLabel,
                             QCheckBox, QTextEdit, QScrollArea, QInputDialog,
                             QMessageBox, QToolTip)
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt

from shutil import copyfile
from criador_json import criador_json
import valores_globais


class JanelaEditor(QMainWindow):
    chk_dos: QCheckBox
    chk_extrai: QCheckBox

    def __init__(self):
        super().__init__()
        self.carregando = False
        self.chave_atual = None
        self.alterado = False  # Flag para detectar mudanças não salvas

        self.setWindowTitle("Gerenciador de Configurações")
        self.setMinimumSize(600, 650)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout(self.central_widget)

        # --- CABEÇALHO ---
        layout_chaves = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.ao_mudar_selecao)  # Auto-load

        btn_nova = QPushButton("Nova")
        btn_nova.clicked.connect(self.nova_chave)

        btn_renomear = QPushButton("Renomear")
        btn_renomear.clicked.connect(self.renomear_chave)

        btn_deletar = QPushButton("Deletar")
        btn_deletar.setStyleSheet("color: red")
        btn_deletar.clicked.connect(self.deletar_chave)

        layout_chaves.addWidget(QLabel("Chave:"))
        layout_chaves.addWidget(self.combo, 1)
        layout_chaves.addWidget(btn_nova)
        layout_chaves.addWidget(btn_renomear)
        layout_chaves.addWidget(btn_deletar)
        self.layout_principal.addLayout(layout_chaves)

        # --- ÁREA DE EDIÇÃO ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container_edicao = QWidget()
        self.layout_edicao = QVBoxLayout(self.container_edicao)
        self.scroll.setWidget(self.container_edicao)
        self.layout_principal.addWidget(self.scroll)

        # --- RODAPÉ ---
        layout_rodape = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar Alterações")
        self.btn_salvar.clicked.connect(self.salvar_dados)
        self.btn_salvar.setEnabled(False)
        self.comando_label = QLabel("preview: ")
        layout_rodape.addWidget(self.comando_label)
        layout_rodape.addStretch()
        layout_rodape.addWidget(self.btn_salvar)
        self.layout_principal.addLayout(layout_rodape)

        self.atualizar_combo()

    def set_alterado(self):
        # self.alterado = True
        # self.btn_salvar.setEnabled(True)
        # Se estivermos carregando a interface, ignoramos o sinal de mudança
        if self.carregando:
            return
        self.alterado = True
        self.btn_salvar.setEnabled(True)

    def checar_salvamento(self):
        """Retorna True se puder prosseguir, False se o usuário cancelou."""
        if self.alterado:
            res = QMessageBox.question(
                self, "Alterações Pendentes",
                f"As alterações em '{self.chave_atual}' não foram salvas. Deseja salvar antes de sair?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if res == QMessageBox.StandardButton.Save:
                self.salvar_dados()
                return True
            elif res == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def ao_mudar_selecao(self):
        nova_chave = self.combo.currentText()
        if nova_chave == self.chave_atual: return

        if not self.checar_salvamento():
            # Bloqueia a mudança voltando o combo para a chave anterior silenciosamente
            self.combo.blockSignals(True)
            self.combo.setCurrentText(self.chave_atual)
            self.combo.blockSignals(False)
            return

        self.carregar_dados(nova_chave)

    def atualizar_combo(self, selecionar=None):
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(sorted(list(valores_globais.dados_tipo.keys())))
        if selecionar:
            self.combo.setCurrentText(selecionar)
            self.carregar_dados(selecionar)
        elif self.combo.count() > 0:
            self.carregar_dados(self.combo.currentText())
        self.combo.blockSignals(False)

    def criar_linha_lista(self, texto, tipo):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 2, 0, 2)

        edit = CampoInteligente(texto)
        edit.setObjectName(f"{tipo}_field")

        # Aplica o Highlight
        edit.highlighter = MeuHighlighter(edit.document())

        # Tooltip customizado ao pairar
        # edit.setToolTip("Dica: Use ?x para parâmetros ou caminho:p para diretórios")

        # ja que o lambdida tem problemas com a falta de retorno das funcoes
        def click_connect():
            container.deleteLater()
            self.set_alterado()

        btn_del = QPushButton("X")
        btn_del.setFixedWidth(30)
        btn_del.clicked.connect(click_connect)

        layout.addWidget(edit)
        layout.addWidget(btn_del)
        return container, edit

    def add_item_vazio(self, btn_origem, tipo):
        linha, edit = self.criar_linha_lista("", tipo)
        idx = self.layout_edicao.indexOf(btn_origem)
        self.layout_edicao.insertWidget(idx, linha)
        edit.setFocus()  # Foco automático
        self.set_alterado()

    def carregar_dados(self, chave):
        self.carregando = True  # Bloqueia o status de alterado
        self.limpar_layout_edicao()
        self.chave_atual = chave
        if not chave or chave not in valores_globais.dados_tipo: return

        info = valores_globais.dados_tipo[chave]
        self.alterado = False
        self.btn_salvar.setEnabled(False)

        # Booleans
        self.chk_dos = QCheckBox("Modo DOS")
        self.chk_dos.setChecked(info['dos'])
        self.chk_dos.stateChanged.connect(self.set_alterado)

        self.chk_extrai = QCheckBox("Extrair Tudo")
        self.chk_extrai.setChecked(info['extrai_tudo'])
        self.chk_extrai.stateChanged.connect(self.set_alterado)

        self.layout_edicao.addWidget(self.chk_dos)
        self.layout_edicao.addWidget(self.chk_extrai)

        # Seção CMD
        self.layout_edicao.addWidget(QLabel("<br><b>Comandos (CMD):</b>"))
        # for c in info['cmd']:
        #     linha, _ = self.criar_linha_lista(c, "cmd")
        #     self.layout_edicao.addWidget(linha)
        for c in info['cmd']:
            linha, edit = self.criar_linha_lista(c, "cmd")
            # Bloqueia o sinal durante a carga inicial para não marcar como "alterado"
            self.layout_edicao.addWidget(linha)
            edit.textChanged.connect(self.set_alterado)

        btn_add_cmd = QPushButton("+ Adicionar Comando")
        btn_add_cmd.clicked.connect(lambda: self.add_item_vazio(btn_add_cmd, "cmd"))
        self.layout_edicao.addWidget(btn_add_cmd)

        # previsualizacao do comando
        
        # Seção EXT
        self.layout_edicao.addWidget(QLabel("<br><b>Extensões (EXT):</b>"))
        for e in info['ext']:
            linha, edit = self.criar_linha_lista(e, "ext")
            self.layout_edicao.addWidget(linha)
            edit.textChanged.connect(self.set_alterado)

        btn_add_ext = QPushButton("+ Adicionar Extensão")
        btn_add_ext.clicked.connect(lambda: self.add_item_vazio(btn_add_ext, "ext"))
        self.layout_edicao.addWidget(btn_add_ext)

        self.layout_edicao.addStretch()

        # --- AQUI ESTÁ O PULO DO GATO ---
        # Forçamos a flag para False APÓS todos os campos serem criados e coloridos
        # double cat jump
        QApplication.processEvents()
        self.carregando = False
        self.alterado = False
        self.btn_salvar.setEnabled(False)

    def salvar_dados(self):
        if not self.chave_atual: return
        cmds, exts = [], []
        for i in range(self.layout_edicao.count()):
            item = self.layout_edicao.itemAt(i)  # Pega o item do layout
            if item is not None:
                w = item.widget()
                if w:
                    edit: QTextEdit = w.findChild(QTextEdit)
                    if edit:
                        texto = edit.toPlainText()
                        if edit.objectName() == "cmd_field":
                            cmds.append(texto)
                        elif edit.objectName() == "ext_field":
                            exts.append(texto)

        # atualmente so atualiza os dados carregados e nao persiste nada
        valores_globais.dados_tipo[self.chave_atual].update({
            'dos': self.chk_dos.isChecked(),
            'extrai_tudo': self.chk_extrai.isChecked(),
            'cmd': cmds,
            'ext': exts
        })
        self.alterado = False
        self.btn_salvar.setEnabled(False)
        print(f"Salvo: {self.chave_atual}")
        # faz backup do arquivo original
        copyfile('conf/dados_tipo.json', 'conf/dados_tipo.json.backup')
        # tenta sobreescrever o arquivo
        # recria o dicionario dados_tipo completo
        dados_tipo_completo = dict()
        # chave caminhos
        dados_tipo_completo['caminhos'] = valores_globais.caminhos
        # chave help
        dados_tipo_completo["help"] = valores_globais.dados_help
        dados_tipo_completo.update(valores_globais.dados_tipo)

        criador_json.escreve_json_padrao('conf/dados_tipo.json', dados_tipo_completo)


    def limpar_layout_edicao(self):
        while self.layout_edicao.count():
            item = self.layout_edicao.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if widget:
                    widget.deleteLater()


    # --- Funções de Chaves (CORRIGIDAS COM CHECAGEM) ---
    def nova_chave(self):
        # Verifica se a chave ATUAL tem alterações pendentes antes de criar uma nova
        if not self.checar_salvamento():
            return

        nome, ok = QInputDialog.getText(self, "Nova Chave", "Nome da configuração:")
        if ok and nome:
            nome = nome.strip()
            if not nome: return
            if nome in valores_globais.dados_tipo:
                QMessageBox.warning(self, "Erro", "Chave já existe!")
                return

            # Cria a nova chave com valores padrão
            valores_globais.dados_tipo[nome] = {"cmd": [""], "ext": [""], "dos": False, "extrai_tudo": False}
            self.alterado = False  # Reseta a flag para a nova chave
            self.atualizar_combo(nome)

    def renomear_chave(self):
        antiga = self.combo.currentText()
        if not antiga: return

        # Se houver mudanças, pergunta se quer salvar ANTES de renomear
        if not self.checar_salvamento():
            return

        nova, ok = QInputDialog.getText(self, "Renomear", f"Novo nome para '{antiga}':")
        if ok and nova:
            nova = nova.strip()
            if not nova or nova == antiga: return
            if nova in valores_globais.dados_tipo:
                QMessageBox.warning(self, "Erro", "Já existe uma configuração com este nome!")
                return

            # Transfere os dados para a nova chave
            valores_globais.dados_tipo[nova] = valores_globais.dados_tipo.pop(antiga)
            self.chave_atual = nova
            self.alterado = False
            self.atualizar_combo(nova)

    def deletar_chave(self):
        chave = self.combo.currentText()
        if not chave: return

        resp = QMessageBox.question(self, "Confirmar Exclusão",
                                    f"Tem certeza que deseja deletar '{chave}'?\nEsta ação não pode ser desfeita.")
        if resp == QMessageBox.StandardButton.Yes:
            del valores_globais.dados_tipo[chave]
            self.chave_atual = None
            self.alterado = False  # Força false para não perguntar ao limpar a tela
            self.atualizar_combo()

    def closeEvent(self, event):
        if self.checar_salvamento():
            event.accept()
        else:
            event.ignore()


class MeuHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.fmt = QTextCharFormat()
        self.fmt.setForeground(QColor("blue"))
        self.fmt.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text):
        # r"\?\*.*?\*" -> Pega do ?* até o próximo * (o .*? é não-guloso)
        # r"caminho:[^\s]*" -> Pega o padrão caminho
        # r"\?\S" -> Pega ? seguido de um caractere (ex: ?a)
        # outra versao r"\?\*[^*]*\*|caminho:[^\s]*|\?\S"
        regex_string = r"\?\*.*?\*|caminho:[^\s]*|\?\S"

        re = QRegularExpression(regex_string)
        it = re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.fmt)


def get_tooltip(selecao):
    # Caso especial para ?*substring*
    if selecao.startswith("?*") and selecao.endswith("*") and len(selecao) > 3:
        substring = selecao[2:-1]  # Remove o '?*' do início e o '*' do fim
        return f"arquivo único que possua a substring: {substring}"
    # Caso especial para caminho:
    if selecao.startswith("caminho:"):
        sufixo = selecao[8:]
        return f"Caminho mapeado: {valores_globais.caminhos.get(sufixo, 'Não encontrado')}"

    tooltips = {
        "?a": "alvo (nome do arquivo com extensão)",
        "?A": "alvo (nome do arquivo sem extensão)",
        "?d": "diretorio alvo relativo",
        "?D": "diretorio alvo completo",
        "?t": "diretorio temporario relativo",
        "?T": "diretorio temporario completo",
        "?c": "caminho completo com nome de arquivo",
        "?u": "drive temporário sem barra",
        "?U": "drive temporário com barra"
    }
    return tooltips.get(selecao, "")


class CampoInteligente(QTextEdit):
    def __init__(self, texto, parent=None):
        super().__init__(parent)  # Primeiro o init do pai
        self.setPlainText(texto)  # Depois define o texto
        self.setFixedHeight(30)
        self.setTabChangesFocus(True)
        self.setMouseTracking(True)

        # Correção das barras de rolagem
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Desativa o "Enter" para não criar novas linhas (comportamento de QLineEdit)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
        else:
            super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        cursor = self.cursorForPosition(pos)
        texto_todo = self.toPlainText()
        tooltip_final = ""

        # Procuramos por matches de ?*...* ou caminho: ou ?x no texto completo
        # e verificamos se a posição do mouse (cursor.position()) está dentro de algum match
        regex = QRegularExpression(r"\?\*.*?\*|caminho:[^\s]*|\?[\w]")
        matches = regex.globalMatch(texto_todo)

        while matches.hasNext():
            m = matches.next()
            if m.capturedStart() <= cursor.position() <= m.capturedEnd():
                tooltip_final = get_tooltip(m.captured())
                break

        if tooltip_final:
            QToolTip.showText(event.globalPosition().toPoint(), tooltip_final, self)
        else:
            QToolTip.hideText()

        super().mouseMoveEvent(event)
