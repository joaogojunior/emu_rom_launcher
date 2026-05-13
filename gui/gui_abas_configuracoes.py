import sys
import copy
import os
from typing import cast, Optional
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QLabel,
                             QCheckBox, QTextEdit, QScrollArea, QInputDialog,
                             QMessageBox, QToolTip, QTabWidget, QFileDialog)
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtCore import QRegularExpression, Qt


# --- DADOS (STAND-ALONE) ---
class ValoresGlobais:
    def __init__(self):
        self.dados_tipo = {
            "Winrar": {"cmd": ["unrar.exe x -y ?a", "caminho:temp_dir"], "ext": [".rar"], "dos": False,
                       "extrai_tudo": True},
            "7Zip": {"cmd": ["7z.exe a ?A.7z"], "ext": [".7z", ".zip"], "dos": True, "extrai_tudo": False}
        }
        self.caminhos = {
            "temp_dir": "R:\\TEMP_RAM",
            "logs": "C:\\Windows\\Logs"
        }


valores_globais = ValoresGlobais()


# --- COMPONENTES ---

class MeuHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.fmt = QTextCharFormat()
        self.fmt.setForeground(QColor("blue"))
        self.fmt.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text: str):
        regex_string = r"\?\*[^*]*\*|caminho:[^\s]*|\?\S"
        re = QRegularExpression(regex_string)
        it = re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.fmt)


class CampoInteligente(QTextEdit):
    def __init__(self, texto: str, parent=None):
        super().__init__(parent)
        self.setPlainText(texto)
        self.setFixedHeight(24)
        self.setTabChangesFocus(True)
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.document().setDocumentMargin(3)
        self.highlighter = MeuHighlighter(self.document())

    def get_tooltip(self, selecao: str) -> str:
        if selecao.startswith("?*") and selecao.endswith("*") and len(selecao) > 3:
            return f"arquivo único que possua a substring: {selecao[2:-1]}"
        tooltips = {
            "?a": "alvo (extensao)", "?A": "alvo (sem extensao)",
            "?d": "dir relativo", "?D": "dir completo",
            "?t": "temp relativo", "?T": "temp completo",
            "?c": "caminho completo", "?u": "drive temp (sem /)", "?U": "drive temp (com /)"
        }
        if selecao.startswith("caminho:"):
            sufixo = selecao[8:]
            return f"Caminho mapeado: {valores_globais.caminhos.get(sufixo, 'Não encontrado')}"
        return tooltips.get(selecao, "")

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        re = QRegularExpression(r"\?\*[^*]*\*|caminho:[^\s]*|\?\S")
        matches = re.globalMatch(self.toPlainText())
        tooltip_final = ""
        while matches.hasNext():
            m = matches.next()
            if m.capturedStart() <= cursor.position() <= m.capturedEnd():
                tooltip_final = self.get_tooltip(m.captured())
                break
        if tooltip_final:
            QToolTip.showText(event.globalPosition().toPoint(), tooltip_final, self)
        else:
            QToolTip.hideText()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
        else:
            super().keyPressEvent(event)


# --- PÁGINA BASE ---

class PaginaBase(QWidget):
    def __init__(self):
        super().__init__()
        self.alterado = False
        self.carregando = False
        self.chave_atual: Optional[str] = None
        self.btn_salvar = QPushButton("Salvar")

    def set_alterado(self):
        if not self.carregando:
            self.alterado = True
            self.btn_salvar.setEnabled(True)


# --- ABA 1 ---

class PaginaComandos(PaginaBase):
    def __init__(self):
        super().__init__()
        self.dados_temp = copy.deepcopy(valores_globais.dados_tipo)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)

        h = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.ao_mudar_selecao)
        btn_nova = QPushButton("Nova");
        btn_nova.clicked.connect(self.nova_chave)
        btn_ren = QPushButton("Renomear");
        btn_ren.clicked.connect(self.renomear_chave)
        btn_del = QPushButton("Deletar");
        btn_del.setStyleSheet("color: red");
        btn_del.clicked.connect(self.deletar_chave)
        h.addWidget(QLabel("Chave:"));
        h.addWidget(self.combo, 1);
        h.addWidget(btn_nova);
        h.addWidget(btn_ren);
        h.addWidget(btn_del)
        layout.addLayout(h)

        self.scroll = QScrollArea();
        self.scroll.setWidgetResizable(True);
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.container = QWidget();
        self.layout_edicao = QVBoxLayout(self.container)
        self.layout_edicao.setContentsMargins(0, 0, 0, 0);
        self.layout_edicao.setSpacing(1)
        self.scroll.setWidget(self.container);
        layout.addWidget(self.scroll)

        self.btn_salvar = QPushButton("Salvar Alterações Comandos");
        self.btn_salvar.setEnabled(False)
        self.btn_salvar.clicked.connect(self.persistir_no_global);
        layout.addWidget(self.btn_salvar)

        self.chk_dos = QCheckBox("Modo DOS")
        self.chk_ext = QCheckBox("Extrair Tudo")

        self.atualizar_combo()

    def checar_salvamento(self) -> bool:
        if self.alterado:
            res = QMessageBox.question(self, "Salvar?", "Salvar alterações em Comandos?",
                                       QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if res == QMessageBox.StandardButton.Save:
                self.persistir_no_global();
                return True
            if res == QMessageBox.StandardButton.Discard:
                self.dados_temp = copy.deepcopy(valores_globais.dados_tipo)
                self.atualizar_combo();
                return True
            return False
        return True

    def carregar_dados(self, chave: str):
        self.carregando = True
        while self.layout_edicao.count():
            item = self.layout_edicao.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()

        self.chave_atual = chave
        if not chave or chave not in self.dados_temp:
            self.carregando = False;
            return

        info = self.dados_temp[chave]
        self.chk_dos = QCheckBox("Modo DOS");
        self.chk_dos.setChecked(info['dos']);
        self.chk_dos.stateChanged.connect(lambda: self.set_alterado())
        self.chk_ext = QCheckBox("Extrair Tudo");
        self.chk_ext.setChecked(info['extrai_tudo']);
        self.chk_ext.stateChanged.connect(lambda: self.set_alterado())
        self.layout_edicao.addWidget(self.chk_dos);
        self.layout_edicao.addWidget(self.chk_ext)

        for t, label in [('cmd', 'Comandos'), ('ext', 'Extensões')]:
            self.layout_edicao.addWidget(QLabel(f"<b>{label}:</b>"))
            for val in info[t]:
                linha, edit = self.criar_linha(val, t)
                self.layout_edicao.addWidget(linha)
                edit.textChanged.connect(self.set_alterado)
            b_add = QPushButton(f"+ {label}")
            b_add.clicked.connect(lambda _, b=b_add, tp=t: self.add_item_vazio(b, tp))
            self.layout_edicao.addWidget(b_add)

        self.layout_edicao.addStretch(1)
        QApplication.processEvents();
        self.alterado = False;
        self.btn_salvar.setEnabled(False);
        self.carregando = False

    def criar_linha(self, texto: str, tipo: str):
        w = QWidget();
        l = QHBoxLayout(w);
        l.setContentsMargins(0, 0, 0, 0);
        l.setSpacing(5)
        edit = CampoInteligente(texto);
        edit.setObjectName(f"{tipo}_field")
        btn = QPushButton("X");
        btn.setFixedWidth(30);
        btn.setFixedHeight(24)
        btn.clicked.connect(lambda: (w.hide(), self.set_alterado()))
        l.addWidget(edit);
        l.addWidget(btn)
        return w, edit

    def add_item_vazio(self, btn_ref: QPushButton, tipo: str):
        linha, edit = self.criar_linha("", tipo)
        self.layout_edicao.insertWidget(self.layout_edicao.indexOf(btn_ref), linha)
        edit.textChanged.connect(self.set_alterado);
        edit.setFocus();
        self.set_alterado()

    def persistir_no_global(self):
        if self.chave_atual:
            cmds, exts = [], []
            for i in range(self.layout_edicao.count()):
                item = self.layout_edicao.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    edit = cast(Optional[QTextEdit], item.widget().findChild(QTextEdit))
                    if edit:
                        txt = edit.toPlainText()
                        if edit.objectName() == "cmd_field":
                            cmds.append(txt)
                        elif edit.objectName() == "ext_field":
                            exts.append(txt)
            self.dados_temp[self.chave_atual].update(
                {'dos': self.chk_dos.isChecked(), 'extrai_tudo': self.chk_ext.isChecked(), 'cmd': cmds, 'ext': exts})
        valores_globais.dados_tipo = copy.deepcopy(self.dados_temp)
        self.alterado = False;
        self.btn_salvar.setEnabled(False)

    def ao_mudar_selecao(self):
        n = self.combo.currentText()
        if n == self.chave_atual or self.carregando: return
        if not self.checar_salvamento():
            self.combo.blockSignals(True);
            self.combo.setCurrentText(self.chave_atual if self.chave_atual else "");
            self.combo.blockSignals(False)
            return
        self.carregar_dados(n)

    def atualizar_combo(self, sel: Optional[str] = None):
        self.combo.blockSignals(True);
        self.combo.clear();
        self.combo.addItems(sorted(self.dados_temp.keys()))
        if sel: self.combo.setCurrentText(sel)
        self.combo.blockSignals(False);
        self.carregar_dados(self.combo.currentText())

    def nova_chave(self):
        if not self.checar_salvamento(): return
        n, ok = QInputDialog.getText(self, "Nova", "Nome:")
        if ok and n.strip():
            self.dados_temp[n.strip()] = {"cmd": [], "ext": [], "dos": False, "extrai_tudo": False}
            self.set_alterado();
            self.atualizar_combo(n.strip())

    def renomear_chave(self):
        ant = self.combo.currentText()
        if not ant or not self.checar_salvamento(): return
        n, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=ant)
        if ok and n.strip() and n.strip() != ant:
            self.dados_temp[n.strip()] = self.dados_temp.pop(ant)
            self.set_alterado();
            self.atualizar_combo(n.strip())

    def deletar_chave(self):
        c = self.combo.currentText()
        if c and QMessageBox.question(self, "Del", f"Excluir {c}?") == QMessageBox.StandardButton.Yes:
            if c in self.dados_temp:
                del self.dados_temp[c]
                self.chave_atual = None;
                self.set_alterado();
                self.atualizar_combo()


# --- ABA 2 ---

class AbaCaminhos(PaginaBase):
    def __init__(self):
        super().__init__()
        self.dados_temp = copy.deepcopy(valores_globais.caminhos)
        layout = QVBoxLayout(self);
        layout.setSpacing(2)
        self.scroll = QScrollArea();
        self.scroll.setWidgetResizable(True);
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.container = QWidget();
        self.layout_lista = QVBoxLayout(self.container)
        self.layout_lista.setContentsMargins(0, 0, 0, 0);
        self.layout_lista.setSpacing(1)
        self.scroll.setWidget(self.container);
        layout.addWidget(self.scroll)
        b_add = QPushButton("+ Adicionar Caminho");
        b_add.clicked.connect(self.add_linha_vazia)
        layout.addWidget(b_add)
        self.btn_salvar = QPushButton("Salvar Todos os Caminhos");
        self.btn_salvar.setEnabled(False);
        self.btn_salvar.clicked.connect(self.persistir_no_global)
        layout.addWidget(self.btn_salvar)
        self.carregar_dados()

    def checar_salvamento(self) -> bool:
        if self.alterado:
            res = QMessageBox.question(self, "Salvar?", "Salvar alterações nos Caminhos?",
                                       QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if res == QMessageBox.StandardButton.Save: self.persistir_no_global(); return True
            if res == QMessageBox.StandardButton.Discard:
                self.dados_temp = copy.deepcopy(valores_globais.caminhos)
                self.carregar_dados();
                return True
            return False
        return True

    def add_linha(self, k: str, v: str):
        w = QWidget();
        l = QHBoxLayout(w);
        l.setContentsMargins(0, 0, 0, 0);
        l.setSpacing(5)
        ec = CampoInteligente(k);
        ec.setFixedWidth(150);
        ec.setObjectName("k")
        ev = CampoInteligente(v);
        ev.setObjectName("v")
        btn_browse = QPushButton("...");
        btn_browse.setFixedWidth(30);
        btn_browse.setFixedHeight(24)
        btn_browse.clicked.connect(lambda: self.abrir_dialogo_diretorio(ev))
        btn_del = QPushButton("X");
        btn_del.setFixedWidth(25);
        btn_del.setFixedHeight(24)
        btn_del.clicked.connect(lambda: (w.hide(), self.set_alterado()))
        l.addWidget(ec);
        l.addWidget(ev, 1);
        l.addWidget(btn_browse);
        l.addWidget(btn_del)
        self.layout_lista.insertWidget(self.layout_lista.count() - 1, w)
        ec.textChanged.connect(self.set_alterado);
        ev.textChanged.connect(self.set_alterado)
        return ec

    def abrir_dialogo_diretorio(self, edit: QTextEdit):
        dir_sel = QFileDialog.getExistingDirectory(self, "Diretório", edit.toPlainText())
        if dir_sel:
            edit.setPlainText(os.path.normpath(dir_sel));
            self.set_alterado()

    def add_linha_vazia(self):
        self.add_linha("", "").setFocus(); self.set_alterado()

    def carregar_dados(self):
        self.carregando = True
        while self.layout_lista.count():
            item = self.layout_lista.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        for k, v in self.dados_temp.items(): self.add_linha(k, v)
        self.layout_lista.addStretch(1)
        QApplication.processEvents();
        self.alterado = False;
        self.btn_salvar.setEnabled(False);
        self.carregando = False

    def persistir_no_global(self):
        novos = {}
        for i in range(self.layout_lista.count()):
            item = self.layout_lista.itemAt(i)
            if item and item.widget() and item.widget().isVisible():
                ec = cast(Optional[QTextEdit], item.widget().findChild(QTextEdit, "k"))
                ev = cast(Optional[QTextEdit], item.widget().findChild(QTextEdit, "v"))
                if ec and ev:
                    k_txt = ec.toPlainText().strip()
                    if k_txt: novos[k_txt] = ev.toPlainText()
        valores_globais.caminhos = novos
        self.dados_temp = copy.deepcopy(valores_globais.caminhos)
        self.alterado = False;
        self.btn_salvar.setEnabled(False)


# --- MAIN ---

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(850, 650)
        self.tabs = QTabWidget();
        self.tabs.setDocumentMode(True)
        self.aba_cmd = PaginaComandos();
        self.aba_path = AbaCaminhos()
        self.tabs.addTab(self.aba_cmd, "Editar Comandos");
        self.tabs.addTab(self.aba_path, "Editar Caminhos")
        self.tabs.currentChanged.connect(self.ao_mudar_aba);
        self.setCentralWidget(self.tabs);
        self.idx_ant = 0

    def ao_mudar_aba(self, idx: int):
        if idx == self.idx_ant: return
        aba_v = self.tabs.widget(self.idx_ant)
        if isinstance(aba_v, PaginaBase) and not aba_v.checar_salvamento():
            self.tabs.blockSignals(True);
            self.tabs.setCurrentIndex(self.idx_ant);
            self.tabs.blockSignals(False)
        else:
            self.idx_ant = idx

    def closeEvent(self, event):
        if self.aba_cmd.checar_salvamento() and self.aba_path.checar_salvamento():
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv);
    win = JanelaPrincipal();
    win.show();
    sys.exit(app.exec())
