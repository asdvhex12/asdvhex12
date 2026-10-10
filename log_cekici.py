#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
import re
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import requests

# ================= API URL =================
BASE_API_URL = "https://solidarksystems.alwaysdata.net/log.php?url="


# ================= PARSE MOTORU =================
class LogParser:

  @staticmethod
  def parse_log(response_text):
    combos = []
    lines_to_check = []

    try:
      data = json.loads(response_text)

      def extract_values(obj):
        if isinstance(obj, dict):
          for k, v in obj.items():
            extract_values(v)
        elif isinstance(obj, list):
          for item in obj:
            extract_values(item)
        elif isinstance(obj, str):
          lines_to_check.extend(obj.split("\n"))

      extract_values(data)
    except:
      pass

    raw_lines = (
        response_text.replace("<br>", "\n").replace("<br/>", "\n").split("\n")
    )
    lines_to_check.extend(raw_lines)

    blacklist = {
        "host",
        "user-agent",
        "accept",
        "referer",
        "origin",
        "cookie",
        "date",
        "server",
        "content-type",
        "connection",
        "pragma",
        "cache-control",
        "authorization",
        "aranan_domain",
        "bulunan_kayit_sayisi",
        "auth",
        "sonuclar",
    }

    for line in lines_to_check:
      line = line.strip()
      if not line:
        continue

      line = re.sub(r'^[\[\]{}"\']+|[\[\]{}"\']+$', "", line).strip()

      if "://" in line:
        parts = line.split("://", 1)
        if len(parts) > 1:
          rem = parts[1]
          if ":" in rem:
            last_colon_idx = rem.rfind(":")
            if last_colon_idx != -1:
              sub_str = rem[:last_colon_idx]
              user_colon_idx = sub_str.rfind(":")
              if user_colon_idx != -1:
                u = sub_str[user_colon_idx + 1 :].strip().strip("\"'/\\")
                p = rem[last_colon_idx + 1 :].strip().strip("\"'/\\")
                if (
                    len(u) > 1
                    and len(p) > 0
                    and u.lower() not in blacklist
                ):
                  combos.append((u, p))
                  continue

      if ":" in line and "://" not in line:
        parts = line.split(":", 1)
        u = parts[0].strip().strip("\"'{},[]<>")
        p = parts[1].strip().strip("\"'{},[]<>")
        if (
            len(u) > 1
            and len(p) > 0
            and u.lower() not in blacklist
            and len(u.split()) < 3
        ):
          combos.append((u, p))

    return list(dict.fromkeys(combos))


# ================= THREADS =================
class FetchWorker(QThread):
  status_sig = pyqtSignal(str)
  result_sig = pyqtSignal(list, str)
  error_sig = pyqtSignal(str)

  def __init__(self, target):
    super().__init__()
    self.target = target

  def run(self):
    try:
      self.status_sig.emit(f"🌐 [ŞAHAN] Bağlanılıyor: {self.target}...")
      res = requests.get(BASE_API_URL + self.target, timeout=15)
      if res.status_code == 200:
        parsed = LogParser.parse_log(res.text)
        self.result_sig.emit(parsed, res.text)
        self.status_sig.emit(
            f"⚡ [ŞAHAN] Tarama bitti. Ayıklanan combo: {len(parsed)}"
        )
      else:
        self.error_sig.emit(f"HTTP Hatası: {res.status_code}")
    except Exception as e:
      self.error_sig.emit(str(e))


class BotWorker(QThread):
  status_sig = pyqtSignal(str)
  progress_sig = pyqtSignal(int, int)
  done_sig = pyqtSignal(list)

  def __init__(self, targets):
    super().__init__()
    self.targets = targets
    self.results = []

  def fetch(self, target):
    try:
      res = requests.get(BASE_API_URL + target, timeout=15)
      if res.status_code == 200:
        return {
            "target": target,
            "combos": LogParser.parse_log(res.text),
            "ok": True,
        }
    except:
      pass
    return {"target": target, "ok": False}

  def run(self):
    total = len(self.targets)
    completed = 0
    with ThreadPoolExecutor(max_workers=5) as exec:
      futures = [exec.submit(self.fetch, t) for t in self.targets]
      for f in as_completed(futures):
        res = f.result()
        if res["ok"]:
          self.results.append(res)
        completed += 1
        self.progress_sig.emit(completed, total)
    self.done_sig.emit(self.results)


# ================= YENİ ARAYÜZ (ŞAHAN FULL SUITE) =================
class SAHANDashboard(QMainWindow):

  def __init__(self):
    super().__init__()
    self.current_combos = []
    self.init_ui()
    self.apply_sahan_theme()

  def apply_sahan_theme(self):
    self.setStyleSheet("""
            QMainWindow { background-color: #08090c; }
            QWidget { font-family: 'Consolas', 'Segoe UI', monospace; color: #d1d5db; }
            
            /* Sol Menü / Sidebar */
            #sidebar {
                background-color: #0d0e12;
                border-right: 1px solid #1f222e;
            }
            #sidebar_title {
                color: #ef4444;
                font-size: 20px;
                font-weight: 900;
                letter-spacing: 1px;
                padding: 10px;
            }
            #sidebar_subtitle {
                color: #06b6d4;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            QPushButton.nav_btn {
                background-color: transparent;
                color: #9ca3af;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 12px 15px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton.nav_btn:hover {
                background-color: #161822;
                color: #f3f4f6;
                border-left: 3px solid #ef4444;
            }
            QPushButton.nav_btn:checked {
                background-color: #1a1d2b;
                color: #ef4444;
                border-left: 4px solid #ef4444;
            }

            /* Kartlar / Paneller */
            QFrame.card {
                background-color: #0f111a;
                border: 1px solid #1f222e;
                border-radius: 8px;
            }
            
            /* Butonlar */
            QPushButton.action_btn {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton.action_btn:hover { background-color: #dc2626; }
            QPushButton.action_btn:disabled { background-color: #27272a; color: #52525b; }
            
            QPushButton#btn_green { background-color: #10b981; }
            QPushButton#btn_green:hover { background-color: #059669; }
            
            QPushButton#btn_cyan { background-color: #06b6d4; color: #000; }
            QPushButton#btn_cyan:hover { background-color: #0891b2; color: #fff; }

            /* Girdiler */
            QLineEdit, QTextEdit {
                background-color: #141622;
                border: 1px solid #272a3b;
                border-radius: 6px;
                padding: 10px;
                color: #f3f4f6;
                font-size: 13px;
                selection-background-color: #ef4444;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #ef4444;
            }

            /* Tablo */
            QTableWidget {
                background-color: #0f111a;
                border: 1px solid #1f222e;
                gridline-color: #1a1d2a;
                color: #e5e7eb;
            }
            QHeaderView::section {
                background-color: #161824;
                color: #ef4444;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #ef4444;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #991b1b;
                color: #ffffff;
            }

            /* Progress Bar & Status */
            QProgressBar {
                background-color: #141622;
                border: 1px solid #272a3b;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk { background-color: #ef4444; }
            QStatusBar { background-color: #0d0e12; color: #6b7280; border-top: 1px solid #1f222e; }
        """)

  def init_ui(self):
    self.setWindowTitle("ŞAHAN VIP - Advanced OSINT & Log Extractor Suite")
    self.resize(1280, 800)

    # Ana Düzen
    main_widget = QWidget()
    self.setCentralWidget(main_widget)
    main_layout = QHBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # ================= SOL SIDEBAR =================
    sidebar = QFrame()
    sidebar.setObjectName("sidebar")
    sidebar.setFixedWidth(260)
    sidebar_layout = QVBoxLayout(sidebar)
    sidebar_layout.setContentsMargins(15, 20, 15, 20)

    lbl_logo = QLabel("ŞAHAN")
    lbl_logo.setObjectName("sidebar_title")
    lbl_sub = QLabel("VIP LOG EXTRACTOR v4.0")
    lbl_sub.setObjectName("sidebar_subtitle")

    sidebar_layout.addWidget(lbl_logo)
    sidebar_layout.addWidget(lbl_sub)

    self.btn_nav_single = QPushButton("⚡ Tekli URL Taraması")
    self.btn_nav_single.setCheckable(True)
    self.btn_nav_single.setChecked(True)
    self.btn_nav_single.setProperty("class", "nav_btn")
    self.btn_nav_single.clicked.connect(lambda: self.switch_page(0))

    self.btn_nav_bot = QPushButton("🤖 Multi-Thread Bot")
    self.btn_nav_bot.setCheckable(True)
    self.btn_nav_bot.setProperty("class", "nav_btn")
    self.btn_nav_bot.clicked.connect(lambda: self.switch_page(1))

    self.btn_nav_debug = QPushButton("🔍 Raw API Konsolu")
    self.btn_nav_debug.setCheckable(True)
    self.btn_nav_debug.setProperty("class", "nav_btn")
    self.btn_nav_debug.clicked.connect(lambda: self.switch_page(2))

    sidebar_layout.addWidget(self.btn_nav_single)
    sidebar_layout.addWidget(self.btn_nav_bot)
    sidebar_layout.addWidget(self.btn_nav_debug)
    sidebar_layout.addStretch()

    # Sol Menü Alt Bilgi
    info_box = QFrame()
    info_box.setProperty("class", "card")
    ib_layout = QVBoxLayout(info_box)
    ib_layout.addWidget(
        QLabel(
            "<b>Sistem İstatistiği:</b><br><font color='#10b981'>● VIP API"
            " Aktif</font><br><font color='#06b6d4'>● Thread Limit: 5</font>"
        )
    )
    sidebar_layout.addWidget(info_box)

    main_layout.addWidget(sidebar)

    # ================= SAĞ İÇERİK ALANI =================
    content_area = QWidget()
    content_layout = QVBoxLayout(content_area)
    content_layout.setContentsMargins(20, 20, 20, 20)

    # Üst İstatistik Kartları
    stats_grid = QGridLayout()

    card1 = QFrame()
    card1.setProperty("class", "card")
    c1_l = QVBoxLayout(card1)
    c1_l.addWidget(
        QLabel(
            "<font color='#9ca3af'>TOPLAM SAF COMBO</font>",
            alignment=Qt.AlignLeft,
        )
    )
    self.lbl_stat_combos = QLabel("0")
    self.lbl_stat_combos.setStyleSheet(
        "font-size: 28px; font-weight: bold; color: #ef4444;"
    )
    c1_l.addWidget(self.lbl_stat_combos)

    card2 = QFrame()
    card2.setProperty("class", "card")
    c2_l = QVBoxLayout(card2)
    c2_l.addWidget(
        QLabel(
            "<font color='#9ca3af'>SON SORGULANAN DOMAIN</font>",
            alignment=Qt.AlignLeft,
        )
    )
    self.lbl_stat_domain = QLabel("Yok")
    self.lbl_stat_domain.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #06b6d4;"
    )
    c2_l.addWidget(self.lbl_stat_domain)

    card3 = QFrame()
    card3.setProperty("class", "card")
    c3_l = QVBoxLayout(card3)
    c3_l.addWidget(
        QLabel(
            "<font color='#9ca3af'>ŞAHAN ENGINE STATUS</font>",
            alignment=Qt.AlignLeft,
        )
    )
    self.lbl_stat_status = QLabel("BEKLEMEDE")
    self.lbl_stat_status.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #10b981;"
    )
    c3_l.addWidget(self.lbl_stat_status)

    stats_grid.addWidget(card1, 0, 0)
    stats_grid.addWidget(card2, 0, 1)
    stats_grid.addWidget(card3, 0, 2)
    content_layout.addLayout(stats_grid)

    # Sayfalar için StackedWidget
    self.pages = QStackedWidget()

    # --- PAGE 0: TEKLİ TARAMA ---
    p0 = QWidget()
    p0_l = QVBoxLayout(p0)

    input_bar = QHBoxLayout()
    self.input_target = QLineEdit()
    self.input_target.setPlaceholderText(
        "ŞAHAN Hedef Domain Girin (Örn: zulaoyun.com)..."
    )
    self.input_target.returnPressed.connect(self.start_single)
    btn_scan = QPushButton("🚀 Comboları Ayıkla")
    btn_scan.setProperty("class", "action_btn")
    btn_scan.clicked.connect(self.start_single)

    input_bar.addWidget(self.input_target)
    input_bar.addWidget(btn_scan)
    p0_l.addLayout(input_bar)

    self.table_accounts = QTableWidget()
    self.table_accounts.setColumnCount(2)
    self.table_accounts.setHorizontalHeaderLabels(
        ["Kullanıcı / E-Posta", "Şifre"]
    )
    self.table_accounts.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.Stretch
    )
    self.table_accounts.horizontalHeader().setSectionResizeMode(
        1, QHeaderView.Stretch
    )
    self.table_accounts.setEditTriggers(QTableWidget.NoEditTriggers)
    p0_l.addWidget(self.table_accounts)

    actions = QHBoxLayout()
    btn_copy = QPushButton("📋 Panoya Kopyala (user:pass)")
    btn_copy.setProperty("class", "action_btn")
    btn_copy.setObjectName("btn_cyan")
    btn_copy.clicked.connect(self.copy_combos)

    btn_export = QPushButton("💾 CSV Formatında Dışa Aktar")
    btn_export.setProperty("class", "action_btn")
    btn_export.setObjectName("btn_green")
    btn_export.clicked.connect(self.export_csv)

    actions.addWidget(btn_copy)
    actions.addStretch()
    actions.addWidget(btn_export)
    p0_l.addLayout(actions)

    self.pages.addWidget(p0)

    # --- PAGE 1: MULTI BOT ---
    p1 = QWidget()
    p1_l = QVBoxLayout(p1)

    p1_l.addWidget(
        QLabel("<b>[ŞAHAN MULTI-THREAD BOT ENGINE]</b> Toplu Hedef Listesi:")
    )
    self.txt_bot_targets = QTextEdit()
    self.txt_bot_targets.setPlaceholderText(
        "Her satıra bir domain gelecek şekilde yazın:\nzulaoyun.com\nexample.com"
    )
    p1_l.addWidget(self.txt_bot_targets)

    self.bot_progress = QProgressBar()
    self.bot_progress.hide()
    p1_l.addWidget(self.bot_progress)

    self.btn_start_bot = QPushButton("⚡ Toplu Taramayı Başlat (ThreadPool)")
    self.btn_start_bot.setProperty("class", "action_btn")
    self.btn_start_bot.clicked.connect(self.start_bot)
    p1_l.addWidget(self.btn_start_bot)

    self.pages.addWidget(p1)

    # --- PAGE 2: RAW DEBUG ---
    p2 = QWidget()
    p2_l = QVBoxLayout(p2)
    p2_l.addWidget(QLabel("<b>[ŞAHAN LOG VIEWER]</b> API Ham Verisi:"))
    self.txt_debug = QTextEdit()
    self.txt_debug.setReadOnly(True)
    p2_l.addWidget(self.txt_debug)

    self.pages.addWidget(p2)

    content_layout.addWidget(self.pages)
    main_layout.addWidget(content_area)

    # Status Bar
    self.status = QStatusBar()
    self.setStatusBar(self.status)
    self.status.showMessage("ŞAHAN VIP System Ready.")

  def switch_page(self, index):
    self.pages.setCurrentIndex(index)
    self.btn_nav_single.setChecked(index == 0)
    self.btn_nav_bot.setChecked(index == 1)
    self.btn_nav_debug.setChecked(index == 2)

  def start_single(self):
    target = self.input_target.text().strip()
    if not target:
      return
    self.input_target.setEnabled(False)
    self.lbl_stat_domain.setText(target)
    self.lbl_stat_status.setText("TARANIYOR...")
    self.lbl_stat_status.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #ef4444;"
    )

    self.worker = FetchWorker(target)
    self.worker.status_sig.connect(self.status.showMessage)
    self.worker.error_sig.connect(self.on_error)
    self.worker.result_sig.connect(self.populate_ui)
    self.worker.start()

  def on_error(self, msg):
    self.status.showMessage(f"❌ ŞAHAN Hata: {msg}")
    self.lbl_stat_status.setText("HATA")
    QMessageBox.warning(self, "ŞAHAN Error", msg)
    self.input_target.setEnabled(True)

  def populate_ui(self, combos, raw_text):
    self.current_combos = combos
    self.lbl_stat_combos.setText(str(len(combos)))
    self.lbl_stat_status.setText("TAMAMLANDI")
    self.lbl_stat_status.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #10b981;"
    )
    self.txt_debug.setText(raw_text)

    self.table_accounts.setRowCount(0)
    for i, (u, p) in enumerate(combos):
      self.table_accounts.insertRow(i)
      self.table_accounts.setItem(i, 0, QTableWidgetItem(u))
      self.table_accounts.setItem(i, 1, QTableWidgetItem(p))

    self.input_target.setEnabled(True)

  def start_bot(self):
    targets = [
        t.strip()
        for t in self.txt_bot_targets.toPlainText().split("\n")
        if t.strip()
    ]
    if not targets:
      return
    self.btn_start_bot.setEnabled(False)
    self.bot_progress.setMaximum(len(targets))
    self.bot_progress.setValue(0)
    self.bot_progress.show()

    self.b_worker = BotWorker(targets)
    self.b_worker.progress_sig.connect(self.bot_progress.setValue)
    self.b_worker.done_sig.connect(self.on_bot_done)
    self.b_worker.start()

  def on_bot_done(self, results):
    self.btn_start_bot.setEnabled(True)
    self.bot_progress.hide()

    folder = "SAHAN_VIP_Combos_" + datetime.now().strftime("%H-%M-%S")
    os.makedirs(folder, exist_ok=True)
    total = 0
    for res in results:
      t_name = res["target"].replace("://", "_").replace("/", "_")
      total += len(res["combos"])
      with open(
          os.path.join(folder, f"{t_name}.txt"), "w", encoding="utf-8"
      ) as f:
        for u, p in res["combos"]:
          f.write(f"{u}:{p}\n")

    msg = (
        f"✅ ŞAHAN Bot tamamlandı! Toplam {total} saf combo"
        f" kaydedildi.\nKlasör: {folder}"
    )
    self.status.showMessage(msg)
    QMessageBox.information(self, "ŞAHAN Report", msg)

  def copy_combos(self):
    if not self.current_combos:
      return
    text = "\n".join([f"{u}:{p}" for u, p in self.current_combos])
    QApplication.clipboard().setText(text)
    self.status.showMessage("📋 ŞAHAN: Saf combolar panoya kopyalandı!")

  def export_csv(self):
    if not self.current_combos:
      return
    path, _ = QFileDialog.getSaveFileName(
        self, "CSV Kaydet", "SAHAN_Combos.csv", "CSV Dosyası (*.csv)"
    )
    if not path:
      return
    try:
      with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Kullanıcı Adı", "Şifre"])
        writer.writerows(self.current_combos)
      self.status.showMessage(f"💾 ŞAHAN Kaydedildi: {path}")
    except Exception as e:
      QMessageBox.critical(self, "Hata", str(e))


if __name__ == "__main__":
  app = QApplication(sys.argv)
  app.setStyle("Fusion")
  window = SAHANDashboard()
  window.show()
  sys.exit(app.exec_())
