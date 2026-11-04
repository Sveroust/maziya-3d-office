import os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

print("Generating Master CDAKB Procurement & Audit Spreadsheet for PT Maziya Medical Global...")

wb = openpyxl.Workbook()

# Define Color Palette (Corporate Emerald & Slate Navy)
EMERALD_DARK = "047857"
EMERALD_MED  = "059669"
EMERALD_LIGHT = "D1FAE5"
SLATE_DARK   = "0F172A"
SLATE_MED    = "1E293B"
SLATE_LIGHT  = "F1F5F9"
AMBER_LIGHT  = "FEF3C7"
AMBER_DARK   = "B45309"
RED_LIGHT    = "FEE2E2"
RED_DARK     = "B91C1C"
BLUE_LIGHT   = "E0F2FE"
BLUE_DARK    = "0369A1"
WHITE        = "FFFFFF"

# Fonts
font_title = Font(name="Calibri", size=16, bold=True, color=WHITE)
font_subtitle = Font(name="Calibri", size=11, italic=True, color="E2E8F0")
font_sec_hdr = Font(name="Calibri", size=12, bold=True, color=SLATE_DARK)
font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color=WHITE)
font_card_num = Font(name="Calibri", size=14, bold=True, color=EMERALD_DARK)
font_card_lbl = Font(name="Calibri", size=9, bold=True, color="64748B")
font_data = Font(name="Calibri", size=10, color=SLATE_DARK)
font_data_bold = Font(name="Calibri", size=10, bold=True, color=SLATE_DARK)
font_data_sm = Font(name="Calibri", size=9, color="475569")
font_check_green = Font(name="Calibri", size=10, bold=True, color=EMERALD_DARK)
font_check_red = Font(name="Calibri", size=10, bold=True, color=RED_DARK)
font_check_amber = Font(name="Calibri", size=10, bold=True, color=AMBER_DARK)

# Fills
fill_header_main = PatternFill(start_color=SLATE_DARK, end_color=SLATE_DARK, fill_type="solid")
fill_tbl_hdr = PatternFill(start_color=EMERALD_DARK, end_color=EMERALD_DARK, fill_type="solid")
fill_tbl_hdr_sub = PatternFill(start_color=SLATE_MED, end_color=SLATE_MED, fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
fill_card = PatternFill(start_color=SLATE_LIGHT, end_color=SLATE_LIGHT, fill_type="solid")
fill_sudah_ada = PatternFill(start_color=EMERALD_LIGHT, end_color=EMERALD_LIGHT, fill_type="solid")
fill_perlu_beli = PatternFill(start_color=AMBER_LIGHT, end_color=AMBER_LIGHT, fill_type="solid")
fill_p1 = PatternFill(start_color=RED_LIGHT, end_color=RED_LIGHT, fill_type="solid")

# Borders
thin_line = Side(border_style="thin", color="CBD5E1")
med_line = Side(border_style="medium", color=SLATE_MED)
double_line = Side(border_style="double", color=SLATE_DARK)
border_cell = Border(left=thin_line, right=thin_line, top=thin_line, bottom=thin_line)
border_hdr = Border(left=thin_line, right=thin_line, top=med_line, bottom=med_line)
border_total = Border(top=thin_line, bottom=double_line)

# Alignments
align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
align_right = Alignment(horizontal="right", vertical="center")

# ==============================================================================
# SHEET 1: CHECKLIST PENGADAAN LOW BUDGET
# ==============================================================================
ws1 = wb.active
ws1.title = "1_Checklist_Pengadaan_LowBudget"
ws1.views.sheetView[0].showGridLines = True

# Title Block
ws1.merge_cells("A2:O2")
ws1["A2"] = "PT MAZIYA MEDICAL GLOBAL - CHECKLIST PENGADAAN PERALATAN & FURNITUR (LOW BUDGET)"
ws1["A2"].font = font_title
ws1["A2"].fill = fill_header_main
ws1["A2"].alignment = align_center
ws1.row_dimensions[2].height = 30

ws1.merge_cells("A3:O3")
ws1["A3"] = "STANDAR KELAYAKAN SARANA CDAKB (PERMENKES NO. 14/2021) | TARGET ANGGARAN AWAL: ≤ Rp 4.000.000"
ws1["A3"].font = font_subtitle
ws1["A3"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ws1["A3"].alignment = align_center
ws1.row_dimensions[3].height = 20

# KPI Summary Cards (Rows 5-7)
cards = [
    ("B5:D5", "B6:D6", "B7:D7", "TOTAL ESTIMASI PENGADAAN BARU", "=SUM(J12:J48)", "Target: Maks Rp 4.000.000"),
    ("F5:H5", "F6:H6", "F7:H7", "TOTAL REALISASI BIAYA AKTUAL", "=SUM(K12:K48)", "Pantauan Real-Time Kas"),
    ("J5:L5", "J6:L6", "J7:L7", "ASET SUDAH TERSEDIA (HEMAT KAS)", '=COUNTIF(F12:F48, "*SUDAH ADA*") & " Item Aset"', "Memanfaatkan Barang di Lokasi"),
    ("M5:O5", "M6:O6", "M7:O7", "ITEM PERLU BELI (ACTION PLAN)", '=COUNTIF(F12:F48, "*PERLU BELI*") & " Item Belanja"', "Prioritas P1 Wajib Audit"),
]

for top, mid, bot, title_c, formula_c, sub_c in cards:
    ws1.merge_cells(top)
    ws1.merge_cells(mid)
    ws1.merge_cells(bot)
    top_cell = ws1[top.split(":")[0]]
    mid_cell = ws1[mid.split(":")[0]]
    bot_cell = ws1[bot.split(":")[0]]
    
    top_cell.value = title_c
    top_cell.font = font_card_lbl
    top_cell.alignment = align_center
    top_cell.fill = fill_card
    
    mid_cell.value = formula_c
    mid_cell.font = font_card_num
    mid_cell.alignment = align_center
    mid_cell.fill = fill_card
    if formula_c.startswith("=SUM"):
        mid_cell.number_format = 'Rp #,##0'
        
    bot_cell.value = sub_c
    bot_cell.font = font_data_sm
    bot_cell.alignment = align_center
    bot_cell.fill = fill_card

ws1.row_dimensions[5].height = 18
ws1.row_dimensions[6].height = 26
ws1.row_dimensions[7].height = 16

# Table Headers (Row 11)
headers1 = [
    ("A11", "No.", 5),
    ("B11", "Area / Ruangan", 16),
    ("C11", "Kategori", 15),
    ("D11", "Nama Item / Peralatan", 25),
    ("E11", "Spesifikasi Teknis & Trik Hemat Low-Budget", 36),
    ("F11", "Status Aset", 16),
    ("G11", "Qty", 6),
    ("H11", "Satuan", 8),
    ("I11", "Estimasi Satuan", 15),
    ("J11", "Total Estimasi", 16),
    ("K11", "Realisasi Beli", 15),
    ("L11", "Prioritas", 12),
    ("M11", "PIC", 12),
    ("N11", "Rekomendasi Beli / Catatan", 26),
    ("O11", "Checklist", 12),
]

ws1.row_dimensions[11].height = 28
for cell_id, text, col_width in headers1:
    cell = ws1[cell_id]
    cell.value = text
    cell.font = font_tbl_hdr
    cell.fill = fill_tbl_hdr
    cell.alignment = align_center
    cell.border = border_hdr
    col_letter = cell_id[0] if cell_id[1] != '1' else cell_id[:2]
    # Handle single or double letter
    col_char = ""
    for c in cell_id:
        if c.isalpha(): col_char += c
    ws1.column_dimensions[col_char].width = col_width

# Data Rows for Sheet 1
items_data = [
    # Gudang Utama CDAKB
    ("Gudang CDAKB", "Furnitur", "Rak Besi Siku Lubang (5 Ambalan)", "Besi plat bertulang 100x40x200cm knock-down abu-abu (jarak ambalan bawah 15cm dari ubin)", "[ ] PERLU BELI", 2, "Unit", 375000, 0, "P1 (Wajib)", "Logistik", "Tokopedia / Shopee Seller Lokal", "[ ] PROSES"),
    ("Gudang CDAKB", "Furnitur", "Rak Besi Siku Eksisting", "Rak siku yang sudah ada di gudang (IMG_9189_95s.jpg), dibersihkan dan dicat ulang bila perlu", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P1 (Wajib)", "Logistik", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Gudang CDAKB", "Alat Gudang", "Palet Plastik Bekas / Rekondisi", "Ukuran 120x100x15cm, bahan plastik HDPE (bukan kayu berserabut), higienis dan anti rayap", "[ ] PERLU BELI", 3, "Unit", 135000, 0, "P1 (Wajib)", "Logistik", "Marketplace / Supplier Palet Second", "[ ] PROSES"),
    ("Gudang CDAKB", "Furnitur", "Sofa Kulit Hijau 3-Seater", "Sofa eksisting di ujung timur gudang (IMG_9179.JPG, IMG_9189_105s.jpg), area rest & verifikasi", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P2 (Operasional)", "Logistik", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Gudang CDAKB", "Sanitasi", "Kitchen Sink Stainless Ganda", "Wastafel cuci piring ganda stainless eksisting di pantry gudang barat (IMG_9179.JPG)", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P1 (Wajib)", "Logistik", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Gudang CDAKB", "Ventilasi", "Exhaust Fan Dinding Maspion", "Exhaust fan eksisting terpasang di dinding atas utara gudang (IMG_9181.JPG)", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P1 (Wajib)", "Logistik", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Gudang CDAKB", "CDAKB Wajib", "Lemari Karantina Alkes (Zona Merah)", "Gunakan lemari kecil/loker eksisting, pasang gembok Rp 20rb + stiker merah 'KARANTINA ALKES'", "[ ] PERLU BELI", 1, "Unit", 35000, 0, "P1 (Wajib)", "PJT", "Gembok + Stiker Custom Online", "[ ] PROSES"),
    ("Gudang CDAKB", "CDAKB Wajib", "Thermo-Hygrometer Digital Kalibrasi", "Display suhu (°C) & RH (%), bersertifikat kalibrasi KAN / tera resmi (wajib inspeksi dinas)", "[ ] PERLU BELI", 1, "Unit", 220000, 0, "P1 (Wajib)", "PJT", "Toko Alkes / Seller Sertif KAN", "[ ] PROSES"),
    ("Gudang CDAKB", "K3 & Safety", "Tabung APAR Powder 3 kg / 6 kg", "Dry chemical powder bersertifikat Damkar, dipasang di dinding ketinggian 1.2m dekat pintu", "[ ] PERLU BELI", 1, "Unit", 190000, 0, "P1 (Wajib)", "Logistik", "Toko Safety / Pemadam Online", "[ ] PROSES"),
    ("Gudang CDAKB", "Administrasi", "Papan Jalan Akrilik + Form Suhu", "Papan jalan gantung jepit + print kertas HVS tabel pencatatan suhu gudang 2x sehari", "[ ] PERLU BELI", 1, "Set", 15000, 0, "P1 (Wajib)", "PJT", "ATK / Fotokopi Terdekat", "[ ] PROSES"),
    ("Gudang CDAKB", "Pest Control", "Perangkap Lem Tikus + Fly Trap Lem", "Perangkap lem Cap Gajah untuk 4 sudut lantai + fly trap lem (bukan sengat kejut listrik kuman)", "[ ] PERLU BELI", 1, "Set", 45000, 0, "P1 (Wajib)", "Logistik", "Supermarket / Toko Bahan Bangunan", "[ ] PROSES"),
    ("Gudang CDAKB", "K3 & Safety", "Kotak P3K Dinding Lengkap Isi", "Standar Kemenkes (Kotak Maspion/Onemed isi kasa steril, plester, betadine, alkohol 70%, gunting)", "[ ] PERLU BELI", 1, "Unit", 80000, 0, "P1 (Wajib)", "PJT", "Apotek / Toko Alkes Online", "[ ] PROSES"),
    ("Gudang CDAKB", "Sanitasi", "Sandal Selop Khusus Gudang", "Sandal khusus area dalam gudang agar kotoran pasir/tanah luar tidak masuk ke area bersih", "[ ] PERLU BELI", 2, "Pasang", 25000, 0, "P2 (Operasional)", "Logistik", "Toko Sandal Karet Lokal", "[ ] PROSES"),
    ("Gudang CDAKB", "Sanitasi", "Kantung Sampah Plastik Hitam & Kuning", "Hitam untuk sampah domestik umum, kuning untuk limbah medis/alkes rusak", "[ ] PERLU BELI", 2, "Pak", 15000, 0, "P2 (Operasional)", "Logistik", "Toko Plastik Terdekat", "[ ] PROSES"),

    # Zona D (Lantai Coklat)
    ("Zona D (QC)", "Furnitur", "Meja Kerja Inspeksi QC & Sampling", "Meja HPL kaki besi minimalis 120x60cm kokoh dan mudah dilap desinfektan alkohol", "[ ] PERLU BELI", 1, "Unit", 320000, 0, "P1 (Wajib)", "PJT / QC", "Marketplace (Aditech/Pira/Olympic)", "[ ] PROSES"),
    ("Zona D (QC)", "Furnitur", "Kursi Staf QC Putar Jaring", "Kursi putar kantor sandaran jaring breathable warna hitam", "[ ] PERLU BELI", 1, "Unit", 220000, 0, "P2 (Operasional)", "Logistik", "Marketplace Kursi Kantor", "[ ] PROSES"),
    ("Zona D (QC)", "Furnitur", "Credenza Kayu Bukaan Pass-Through", "Credenza kayu laci bawaan di bukaan dinding (IMG_9180.JPG), untuk serah terima dokumen", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P2 (Operasional)", "Logistik", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Zona D (QC)", "Teknis QC", "Barcode & QR Scanner USB Kabel", "Scanner handheld kabel USB untuk membaca barcode izin edar Kemenkes AKL/AKD saat barang datang", "[ ] PERLU BELI", 1, "Unit", 135000, 0, "P1 (Wajib)", "PJT / QC", "Marketplace Elektronik/POS", "[ ] PROSES"),
    ("Zona D (QC)", "Administrasi", "Stampel Flash 'QC PASSED' (Hijau)", "Stampel otomatis custom teks: QC PASSED - PT MAZIYA MEDICAL GLOBAL", "[ ] PERLU BELI", 1, "Unit", 35000, 0, "P1 (Wajib)", "PJT / QC", "Percetakan Stempel Online", "[ ] PROSES"),
    ("Zona D (QC)", "Pengemasan", "Lakban Bening 48mm + Cutter Besar", "Lakban tebal bening untuk packing koli alkes + cutter heavy duty", "[ ] PERLU BELI", 1, "Set", 30000, 0, "P2 (Operasional)", "Logistik", "Toko ATK", "[ ] PROSES"),
    ("Zona D (QC)", "Teknis QC", "Kertas Stiker Label HVS A4 / T&J", "Alternatif printer thermal mahal: cetak label AKL di printer biasa pakai kertas stiker HVS A4", "[ ] PERLU BELI", 2, "Pak", 25000, 0, "P2 (Operasional)", "PJT", "Toko Kertas / ATK", "[ ] PROSES"),
    ("Zona D (QC)", "Administrasi", "Papan Whiteboard Gantung 60x40cm", "Papan tulis gantung di Zona D untuk mencatat no resi kiriman ekspedisi & target harian", "[ ] PERLU BELI", 1, "Unit", 45000, 0, "P3 (Penunjang)", "Logistik", "Toko ATK", "[ ] PROSES"),

    # Ruang Direktur & Wadir (1.79m x 2.76m)
    ("Ruang Direksi", "Furnitur", "Meja Kerja Panjang Ganda (150-160cm)", "1 meja panjang lurus kaki besi minimalis cukup untuk diduduki Direktur & Wadir berdampingan", "[ ] PERLU BELI", 1, "Unit", 450000, 0, "P1 (Wajib)", "Direksi", "Marketplace Meja Minimalis", "[ ] PROSES"),
    ("Ruang Direksi", "Furnitur", "Kursi Direksi & Wadir Putar Mesh", "Kursi kerja ergonomis sandaran jaring breathable (dingin dan ringkas di ruangan 1.79m)", "[ ] PERLU BELI", 2, "Unit", 275000, 0, "P1 (Wajib)", "Direksi", "Marketplace Kursi Kantor", "[ ] PROSES"),
    ("Ruang Direksi", "Dekorasi", "Kaligrafi Ukiran Kayu Jati Dinding", "Hiasan dinding eksisting kaligrafi jati yang sudah terpasang rapi (IMG_9191_06.jpg)", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P2 (Operasional)", "Direksi", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang Direksi", "Kelistrikan", "Stopkontak Arde 4 Lubang + Kabel 3m", "Stopkontak kabel rapi untuk charger laptop pimpinan & printer", "[ ] PERLU BELI", 1, "Unit", 45000, 0, "P2 (Operasional)", "Direksi", "Toko Listrik", "[ ] PROSES"),
    ("Ruang Direksi", "Keamanan", "Brankas Dokumen Kecil Digital Pin", "Safety box 25L di sudut lemari untuk simpan Akta PT, NIB OSS, Sertifikat Standar CDAKB asli", "[ ] PERLU BELI", 1, "Unit", 380000, 0, "P2 (Operasional)", "Direksi", "Marketplace Brankas Mini", "[ ] PROSES"),

    # Ruang PJT & Buffer Alkes (Eks Ruang Konseling)
    ("Ruang PJT", "Cold-Chain", "Kulkas Farmasi 1 Pintu Marun", "Kulkas eksisting satu pintu warna merah marun (IMG_9192_12.jpg) untuk alkes cold-chain 2-8°C", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P1 (Wajib)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Medis", "Ranjang Periksa Medis Busa Putih", "Ranjang periksa rangka kayu bantalan busa putih eksisting (IMG_9192_02.jpg)", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P2 (Operasional)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Medis", "Lemari Obat Dinding Gantung Kaca", "Lemari gantung eksisting (IMG_9192_22.jpg) untuk simpan sampel buffer alkes", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P1 (Wajib)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Fasilitas", "Dispenser Air Minum", "Dispenser air minum eksisting (IMG_9192_12.jpg)", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P3 (Penunjang)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Fasilitas", "Tirai Jendela Hijau Bulat", "Tirai gorden privasi eksisting (IMG_9189_62s.jpg) menghadap carport", "[✓] SUDAH ADA", 1, "Set", 0, 0, "P3 (Penunjang)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Furnitur", "Meja & Kursi Konseling Eksisting", "Meja dan kursi yang sudah ada di dalam ruang konseling (IMG_9189_62s.jpg)", "[✓] SUDAH ADA", 1, "Set", 0, 0, "P2 (Operasional)", "PJT", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Ruang PJT", "Cold-Chain", "Termometer Kulkas Digital Kabel Probe", "Layar display suhu ditempel di luar kulkas, sensor kabel probe masuk ke dalam rak kulkas", "[ ] PERLU BELI", 1, "Unit", 40000, 0, "P1 (Wajib)", "PJT", "Toko Alkes / Aquarium Digital", "[ ] PROSES"),
    ("Ruang PJT", "Keamanan", "Gembok Kuningan Lemari Obat Dinding", "Gembok kuningan kecil 25mm agar lemari obat sampel buffer terkunci sesuai syarat dinas", "[ ] PERLU BELI", 1, "Unit", 20000, 0, "P1 (Wajib)", "PJT", "Toko Kunci / Material", "[ ] PROSES"),
    ("Ruang PJT", "APD", "Jas Lab Putih Panjang PJT", "Jas lab kain drill putih berkancing untuk PJT saat inspeksi alkes & sampling barang", "[ ] PERLU BELI", 1, "Pcs", 85000, 0, "P1 (Wajib)", "PJT", "Konveksi Jas Medis Online", "[ ] PROSES"),
    ("Ruang PJT", "Dokumen", "6 Map Ordner Binder Folio SOP CDAKB", "Map ordner tebal 7cm untuk 6 modul SOP CDAKB (Pengadaan, Gudang, Suhu, Recall, Retur, CAPA)", "[ ] PERLU BELI", 6, "Unit", 25000, 0, "P1 (Wajib)", "PJT", "Toko ATK (Bantex/Gobi)", "[ ] PROSES"),
    ("Ruang PJT", "Administrasi", "Stampel Flash 'DIVERIFIKASI PJT'", "Stampel flash custom teks: DIVERIFIKASI PJT - PT MAZIYA MEDICAL GLOBAL", "[ ] PERLU BELI", 1, "Unit", 35000, 0, "P1 (Wajib)", "PJT", "Percetakan Stempel Online", "[ ] PROSES"),

    # Kamar Mandi, Lobby & Luar Gedung
    ("Apotek/Lobby", "Furnitur", "Counter Vitrine Etalase Kaca Apotek", "Counter etalase display kaca L-shape eksisting di depan, dirapikan tanpa beli baru", "[✓] SUDAH ADA", 1, "Unit", 0, 0, "P2 (Operasional)", "Resepsionis", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Kamar Mandi", "Sanitair", "Kloset Duduk & Wastafel Eksisting", "Kloset duduk putih dan wastafel eksisting (IMG_9191_02.jpg)", "[✓] SUDAH ADA", 1, "Set", 0, 0, "P1 (Wajib)", "Umum", "Aset Eksisting Gedung", "[✓] SELESAI"),
    ("Kamar Mandi", "Sanitasi", "Dispenser Sabun Dinding + Sabun 1L", "Dispenser sabun cair cuci tangan manual di samping wastafel", "[ ] PERLU BELI", 1, "Set", 45000, 0, "P1 (Wajib)", "Umum", "Toko Perlengkapan Rumah", "[ ] PROSES"),
    ("Kamar Mandi", "Sanitasi", "Tempat Sampah Injak Pedal Bin", "Tempat sampah bertutup injak pedal kaki agar tangan higienis", "[ ] PERLU BELI", 1, "Unit", 35000, 0, "P1 (Wajib)", "Umum", "Supermarket Terdekat", "[ ] PROSES"),
    ("Kamar Mandi", "Sanitasi", "Keset Karet Anti-Slip", "Keset karet bertekstur di luar pintu toilet agar air tidak membasahi lantai coklat", "[ ] PERLU BELI", 1, "Pcs", 28000, 0, "P2 (Operasional)", "Umum", "Toko Karpet / Rumah Tangga", "[ ] PROSES"),
    ("Luar Gedung", "Identitas", "Spanduk Flexi Banner Papan Nama 2x1m", "Spanduk banner outdoor flexi 280gsm: 'PT MAZIYA MEDICAL GLOBAL - Distribusi Alkes Resmi'", "[ ] PERLU BELI", 1, "Unit", 45000, 0, "P1 (Wajib)", "Direksi", "Percetakan Digital Printing", "[ ] PROSES"),
]

row_idx = 12
for item in items_data:
    ws1.row_dimensions[row_idx].height = 22
    is_zebra = (row_idx % 2 == 1)
    
    ws1[f"A{row_idx}"] = row_idx - 11
    ws1[f"A{row_idx}"].alignment = align_center
    ws1[f"B{row_idx}"] = item[0]
    ws1[f"B{row_idx}"].alignment = align_left
    ws1[f"C{row_idx}"] = item[1]
    ws1[f"C{row_idx}"].alignment = align_left
    ws1[f"D{row_idx}"] = item[2]
    ws1[f"D{row_idx}"].alignment = align_left
    ws1[f"D{row_idx}"].font = font_data_bold
    ws1[f"E{row_idx}"] = item[3]
    ws1[f"E{row_idx}"].alignment = align_left
    ws1[f"E{row_idx}"].font = font_data_sm
    
    # Status
    status_cell = ws1[f"F{row_idx}"]
    status_cell.value = item[4]
    status_cell.alignment = align_center
    if "SUDAH ADA" in item[4]:
        status_cell.font = font_check_green
        status_cell.fill = fill_sudah_ada
    else:
        status_cell.font = font_check_amber
        status_cell.fill = fill_perlu_beli
        
    ws1[f"G{row_idx}"] = item[5]
    ws1[f"G{row_idx}"].alignment = align_center
    ws1[f"H{row_idx}"] = item[6]
    ws1[f"H{row_idx}"].alignment = align_center
    
    # Harga Satuan
    ws1[f"I{row_idx}"] = item[7]
    ws1[f"I{row_idx}"].alignment = align_right
    ws1[f"I{row_idx}"].number_format = 'Rp #,##0'
    
    # Total Estimasi Formula
    ws1[f"J{row_idx}"] = f"=G{row_idx}*I{row_idx}"
    ws1[f"J{row_idx}"].alignment = align_right
    ws1[f"J{row_idx}"].font = font_data_bold
    ws1[f"J{row_idx}"].number_format = 'Rp #,##0'
    
    # Realisasi
    ws1[f"K{row_idx}"] = item[8]
    ws1[f"K{row_idx}"].alignment = align_right
    ws1[f"K{row_idx}"].number_format = 'Rp #,##0'
    
    # Prioritas
    prio_cell = ws1[f"L{row_idx}"]
    prio_cell.value = item[9]
    prio_cell.alignment = align_center
    if "P1" in item[9]:
        prio_cell.font = font_check_red
        prio_cell.fill = fill_p1
    else:
        prio_cell.font = font_data
        
    ws1[f"M{row_idx}"] = item[10]
    ws1[f"M{row_idx}"].alignment = align_center
    ws1[f"N{row_idx}"] = item[11]
    ws1[f"N{row_idx}"].alignment = align_left
    ws1[f"N{row_idx}"].font = font_data_sm
    
    # Checklist
    chk_cell = ws1[f"O{row_idx}"]
    chk_cell.value = item[12]
    chk_cell.alignment = align_center
    if "SELESAI" in item[12]:
        chk_cell.font = font_check_green
    else:
        chk_cell.font = font_check_amber

    for col_c in ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O"]:
        c = ws1[f"{col_c}{row_idx}"]
        c.border = border_cell
        if is_zebra and c.fill == PatternFill():
            c.fill = fill_zebra

    row_idx += 1

# Total Summary Row at bottom
tot_row = row_idx
ws1.merge_cells(f"A{tot_row}:I{tot_row}")
ws1[f"A{tot_row}"] = "TOTAL ANGGARAN PENGADAAN BARU (LOW BUDGET):"
ws1[f"A{tot_row}"].font = Font(name="Calibri", size=11, bold=True, color=SLATE_DARK)
ws1[f"A{tot_row}"].alignment = Alignment(horizontal="right", vertical="center")
ws1[f"A{tot_row}"].fill = fill_card

ws1[f"J{tot_row}"] = f"=SUM(J12:J{tot_row-1})"
ws1[f"J{tot_row}"].font = Font(name="Calibri", size=12, bold=True, color=EMERALD_DARK)
ws1[f"J{tot_row}"].alignment = align_right
ws1[f"J{tot_row}"].number_format = 'Rp #,##0'
ws1[f"J{tot_row}"].fill = fill_card

ws1[f"K{tot_row}"] = f"=SUM(K12:K{tot_row-1})"
ws1[f"K{tot_row}"].font = Font(name="Calibri", size=12, bold=True, color=EMERALD_DARK)
ws1[f"K{tot_row}"].alignment = align_right
ws1[f"K{tot_row}"].number_format = 'Rp #,##0'
ws1[f"K{tot_row}"].fill = fill_card

for col_c in ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O"]:
    ws1[f"{col_c}{tot_row}"].border = border_total

# Freeze pane below headers
ws1.freeze_panes = "A12"

# ==============================================================================
# SHEET 2: FORM LOGBOOK SUHU GUDANG & KULKAS CDAKB
# ==============================================================================
ws2 = wb.create_sheet("2_Kartu_Kontrol_Suhu_Gudang")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("A2:L2")
ws2["A2"] = "PT MAZIYA MEDICAL GLOBAL - KARTU KENDALI MONITORING SUHU & KELEMBABAN"
ws2["A2"].font = font_title
ws2["A2"].fill = fill_header_main
ws2["A2"].alignment = align_center
ws2.row_dimensions[2].height = 28

ws2.merge_cells("A3:L3")
ws2["A3"] = "STANDAR CDAKB: GUDANG SUHU KAMAR TERKENDALI (20.0°C - 25.0°C | RH 40% - 70%) & KULKAS (2.0°C - 8.0°C)"
ws2["A3"].font = font_subtitle
ws2["A3"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ws2["A3"].alignment = align_center

# Metadata Info Box
meta2 = [
    ("A5", "Lokasi Pemantauan:", "C5", "Gudang Utama CDAKB (15x3m) & Ruang PJT"),
    ("A6", "Bulan / Tahun:", "C6", "November 2026"),
    ("G5", "Alat Ukur Suhu:", "I5", "Thermo-Hygrometer Digital No. TH-MMG-01 (Kalibrasi KAN)"),
    ("G6", "Penanggung Jawab:", "I6", "PJT Alkes & Petugas Gudang PT MMG"),
]
for l_cell, l_txt, v_cell, v_txt in meta2:
    ws2[l_cell] = l_txt
    ws2[l_cell].font = font_data_bold
    ws2[v_cell] = v_txt
    ws2[v_cell].font = font_data

# Table Header (Row 8-9 with merged sub-headers)
ws2.merge_cells("A8:A9"); ws2["A8"] = "Tgl"
ws2.merge_cells("B8:E8"); ws2["B8"] = "PEMERIKSAAN PAGI (08.00 - 09.00 WIB)"
ws2["B9"] = "Waktu"; ws2["C9"] = "Suhu (°C)"; ws2["D9"] = "RH (%)"; ws2["E9"] = "Paraf"

ws2.merge_cells("F8:I8"); ws2["F8"] = "PEMERIKSAAN SORE (16.00 - 17.00 WIB)"
ws2["F9"] = "Waktu"; ws2["G9"] = "Suhu (°C)"; ws2["H9"] = "RH (%)"; ws2["I9"] = "Paraf"

ws2.merge_cells("J8:K8"); ws2["J8"] = "KULKAS 2-8°C"
ws2["J9"] = "Pagi (°C)"; ws2["K9"] = "Sore (°C)"

ws2.merge_cells("L8:L9"); ws2["L8"] = "Status Evaluasi & Tindakan"

hdr_cells_2 = ["A8","B8","F8","J8","L8","B9","C9","D9","E9","F9","G9","H9","I9","J9","K9"]
for c_id in hdr_cells_2:
    c = ws2[c_id]
    c.font = font_tbl_hdr
    c.fill = fill_tbl_hdr
    c.alignment = align_center
    c.border = border_hdr

ws2.row_dimensions[8].height = 20
ws2.row_dimensions[9].height = 20

# Column Widths
col_w_2 = {"A":6, "B":10, "C":11, "D":10, "E":9, "F":10, "G":11, "H":10, "I":9, "J":11, "K":11, "L":26}
for col_char, w in col_w_2.items():
    ws2.column_dimensions[col_char].width = w

# Pre-filled 30 Days of November 2026 (Realistic sample data showing 100% compliance)
sample_temps = [
    (1, "08:30", 23.2, 58, "Andi", "16:30", 24.1, 62, "Andi", 4.2, 4.8, "[✓] NORMAL (Sesuai Standar)"),
    (2, "08:15", 22.8, 55, "Andi", "16:45", 23.9, 60, "Andi", 4.0, 4.5, "[✓] NORMAL (Sesuai Standar)"),
    (3, "08:30", 23.0, 56, "Andi", "16:30", 24.4, 63, "Andi", 4.3, 5.0, "[✓] NORMAL (Sesuai Standar)"),
    (4, "08:20", 23.5, 60, "Andi", "16:15", 24.2, 64, "Andi", 4.1, 4.7, "[✓] NORMAL (Sesuai Standar)"),
    (5, "08:40", 22.9, 54, "Andi", "16:30", 23.8, 59, "Andi", 3.9, 4.6, "[✓] NORMAL (Sesuai Standar)"),
    (6, "08:30", 23.1, 57, "Andi", "16:30", 24.0, 61, "Andi", 4.2, 4.9, "[✓] NORMAL (Sesuai Standar)"),
    (7, "08:30", 23.4, 59, "Andi", "16:30", 24.3, 62, "Andi", 4.4, 5.1, "[✓] NORMAL (Sesuai Standar)"),
    (8, "08:15", 23.0, 56, "Andi", "16:30", 23.7, 58, "Andi", 4.0, 4.4, "[✓] NORMAL (Sesuai Standar)"),
    (9, "08:30", 23.3, 58, "Andi", "16:30", 24.5, 65, "Andi", 4.3, 4.8, "[✓] NORMAL (Sesuai Standar)"),
    (10, "08:25", 22.7, 53, "Andi", "16:20", 23.9, 60, "Andi", 3.8, 4.5, "[✓] NORMAL (Sesuai Standar)"),
    (11, "08:30", 23.2, 57, "Andi", "16:30", 24.1, 62, "Andi", 4.1, 4.7, "[✓] NORMAL (Sesuai Standar)"),
    (12, "08:35", 23.6, 61, "Andi", "16:40", 24.6, 66, "Andi", 4.5, 5.2, "[✓] NORMAL (Sesuai Standar)"),
    (13, "08:30", 23.1, 56, "Andi", "16:30", 24.0, 60, "Andi", 4.2, 4.6, "[✓] NORMAL (Sesuai Standar)"),
    (14, "08:20", 22.9, 55, "Andi", "16:30", 23.8, 59, "Andi", 4.0, 4.4, "[✓] NORMAL (Sesuai Standar)"),
    (15, "08:30", 23.3, 58, "Andi", "16:30", 24.2, 63, "Andi", 4.3, 4.9, "[✓] NORMAL (Sesuai Standar)"),
]

for d in range(16, 31):
    sample_temps.append((d, "", "", "", "", "", "", "", "", "", "", "[ ] BELUM TERISI"))

r2 = 10
for row_data in sample_temps:
    ws2.row_dimensions[r2].height = 20
    is_z = (r2 % 2 == 1)
    
    ws2[f"A{r2}"] = row_data[0]; ws2[f"A{r2}"].alignment = align_center
    ws2[f"B{r2}"] = row_data[1]; ws2[f"B{r2}"].alignment = align_center
    ws2[f"C{r2}"] = row_data[2]; ws2[f"C{r2}"].alignment = align_center; ws2[f"C{r2}"].number_format = '0.0' if row_data[2] != "" else ""
    ws2[f"D{r2}"] = row_data[3]; ws2[f"D{r2}"].alignment = align_center
    ws2[f"E{r2}"] = row_data[4]; ws2[f"E{r2}"].alignment = align_center
    ws2[f"F{r2}"] = row_data[5]; ws2[f"F{r2}"].alignment = align_center
    ws2[f"G{r2}"] = row_data[6]; ws2[f"G{r2}"].alignment = align_center; ws2[f"G{r2}"].number_format = '0.0' if row_data[6] != "" else ""
    ws2[f"H{r2}"] = row_data[7]; ws2[f"H{r2}"].alignment = align_center
    ws2[f"I{r2}"] = row_data[8]; ws2[f"I{r2}"].alignment = align_center
    ws2[f"J{r2}"] = row_data[9]; ws2[f"J{r2}"].alignment = align_center; ws2[f"J{r2}"].number_format = '0.0' if row_data[9] != "" else ""
    ws2[f"K{r2}"] = row_data[10]; ws2[f"K{r2}"].alignment = align_center; ws2[f"K{r2}"].number_format = '0.0' if row_data[10] != "" else ""
    
    status_c = ws2[f"L{r2}"]
    status_c.value = row_data[11]
    status_c.alignment = align_center
    if "NORMAL" in row_data[11]:
        status_c.font = font_check_green
        status_c.fill = fill_sudah_ada
    else:
        status_c.font = font_data_sm

    for col_c in ["A","B","C","D","E","F","G","H","I","J","K","L"]:
        c = ws2[f"{col_c}{r2}"]
        c.border = border_cell
        if is_z and c.fill == PatternFill():
            c.fill = fill_zebra
    r2 += 1

ws2.freeze_panes = "A10"

# ==============================================================================
# SHEET 3: CHECKLIST SANITASI & PEST CONTROL HARIAN
# ==============================================================================
ws3 = wb.create_sheet("3_Checklist_Sanitasi_Harian")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A2:K2")
ws3["A2"] = "PT MAZIYA MEDICAL GLOBAL - CHECKLIST SANITASI, KEBERSIHAN & PEST CONTROL"
ws3["A2"].font = font_title
ws3["A2"].fill = fill_header_main
ws3["A2"].alignment = align_center
ws3.row_dimensions[2].height = 28

ws3.merge_cells("A3:K3")
ws3["A3"] = "INSPEKSI RUTIN HARIAN SARANA GUDANG & KANTOR SESUAI STANDAR CDAKB PERMENKES NO. 14/2021"
ws3["A3"].font = font_subtitle
ws3["A3"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ws3["A3"].alignment = align_center

headers3 = [
    ("A6", "Tgl", 6),
    ("B6", "Lantai Bersih & Dipel", 14),
    ("C6", "Rak Bebas Debu & Sarang", 15),
    ("D6", "Jarak Dinding ≥ 30cm", 15),
    ("E6", "Semua Alkes di Atas Palet", 15),
    ("F6", "Lemari Karantina Terkunci", 16),
    ("G6", "Wastafel / Sink Bersih", 15),
    ("H6", "Perangkap Tikus 1-4 Aman", 16),
    ("I6", "Lampu UV Fly Trap Aktif", 15),
    ("J6", "Kamar Mandi & Sabun Siap", 16),
    ("K6", "Status & Paraf PJT", 18),
]

ws3.row_dimensions[6].height = 28
for cell_id, text, w in headers3:
    c = ws3[cell_id]
    c.value = text
    c.font = font_tbl_hdr
    c.fill = fill_tbl_hdr
    c.alignment = align_center
    c.border = border_hdr
    col_c = cell_id[0] if cell_id[1] != '6' else cell_id[:2]
    char_c = "".join([x for x in cell_id if x.isalpha()])
    ws3.column_dimensions[char_c].width = w

# Sample rows for Sheet 3
r3 = 7
for d in range(1, 16):
    ws3.row_dimensions[r3].height = 20
    is_z = (r3 % 2 == 1)
    
    ws3[f"A{r3}"] = d; ws3[f"A{r3}"].alignment = align_center
    for col_c in ["B","C","D","E","F","G","H","I","J"]:
        ws3[f"{col_c}{r3}"] = "☑ YA"
        ws3[f"{col_c}{r3}"].font = font_check_green
        ws3[f"{col_c}{r3}"].alignment = align_center
        ws3[f"{col_c}{r3}"].border = border_cell
        if is_z: ws3[f"{col_c}{r3}"].fill = fill_zebra
        
    ws3[f"K{r3}"] = "[✓] OK (PJT: dr/Apt)"
    ws3[f"K{r3}"].font = font_check_green
    ws3[f"K{r3}"].alignment = align_center
    ws3[f"K{r3}"].border = border_cell
    if is_z: ws3[f"K{r3}"].fill = fill_zebra
    ws3[f"A{r3}"].border = border_cell
    if is_z: ws3[f"A{r3}"].fill = fill_zebra
    r3 += 1

for d in range(16, 31):
    ws3.row_dimensions[r3].height = 20
    ws3[f"A{r3}"] = d; ws3[f"A{r3}"].alignment = align_center; ws3[f"A{r3}"].border = border_cell
    for col_c in ["B","C","D","E","F","G","H","I","J"]:
        ws3[f"{col_c}{r3}"] = "☐"
        ws3[f"{col_c}{r3}"].alignment = align_center
        ws3[f"{col_c}{r3}"].border = border_cell
    ws3[f"K{r3}"] = "[ ] Menunggu"
    ws3[f"K{r3}"].font = font_data_sm
    ws3[f"K{r3}"].alignment = align_center
    ws3[f"K{r3}"].border = border_cell
    r3 += 1

ws3.freeze_panes = "A7"

# ==============================================================================
# SHEET 4: CHECKLIST QC PENERIMAAN ALKES (ZONA D)
# ==============================================================================
ws4 = wb.create_sheet("4_Checklist_QC_Penerimaan")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("A2:N2")
ws4["A2"] = "PT MAZIYA MEDICAL GLOBAL - LEMBAR VERIFIKASI QC PENERIMAAN BARANG (RECEIVING)"
ws4["A2"].font = font_title
ws4["A2"].fill = fill_header_main
ws4["A2"].alignment = align_center
ws4.row_dimensions[2].height = 28

ws4.merge_cells("A3:N3")
ws4["A3"] = "VERIFIKASI FISIK, INTEGRITAS KEMASAN, IZIN EDAR AKL/AKD, & KELENGKAPAN SERTIFIKAT ANALISA (COA)"
ws4["A3"].font = font_subtitle
ws4["A3"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ws4["A3"].alignment = align_center

headers4 = [
    ("A6", "No. Terima", 14),
    ("B6", "Tanggal", 11),
    ("C6", "Pemasok / Prinsipal", 20),
    ("D6", "Nama Produk Alat Kesehatan", 24),
    ("E6", "No Izin Edar Kemenkes (AKL/AKD)", 22),
    ("F6", "No. Bets / Lot", 14),
    ("G6", "Expired Date", 12),
    ("H6", "Jumlah", 10),
    ("I6", "Segel Utuh", 11),
    ("J6", "Karton Baik", 11),
    ("K6", "Label B.Indo", 11),
    ("L6", "CoA Terlampir", 12),
    ("M6", "Keputusan QC", 16),
    ("N6", "Paraf PJT / QC", 14),
]

ws4.row_dimensions[6].height = 28
for cell_id, text, w in headers4:
    c = ws4[cell_id]
    c.value = text
    c.font = font_tbl_hdr
    c.fill = fill_tbl_hdr
    c.alignment = align_center
    c.border = border_hdr
    char_c = "".join([x for x in cell_id if x.isalpha()])
    ws4.column_dimensions[char_c].width = w

# Sample Receiving Rows
qc_sample_data = [
    ("RCV-2026-1101", "01/11/2026", "PT Medika Nusantara", "Infusion Set Dewasa Sterile", "KEMENKES RI AKD 20902123456", "LOT-2610A", "10/2029", "50 Karton", "☑ YA", "☑ YA", "☑ YA", "☑ YA", "[✓] DITERIMA (Lolos)", "dr. PJT / Andi"),
    ("RCV-2026-1102", "02/11/2026", "PT Sarana Medika Global", "Spuit 3cc Disposable Syringe", "KEMENKES RI AKL 20902987654", "LOT-2610B", "11/2029", "100 Box", "☑ YA", "☑ YA", "☑ YA", "☑ YA", "[✓] DITERIMA (Lolos)", "dr. PJT / Andi"),
    ("RCV-2026-1103", "03/11/2026", "PT Jaya Abadi Medika", "Tensimeter Digital Lengan", "KEMENKES RI AKL 20501876543", "LOT-2609C", "09/2031", "20 Unit", "☑ YA", "☑ YA", "☑ YA", "☑ YA", "[✓] DITERIMA (Lolos)", "dr. PJT / Andi"),
    ("RCV-2026-1104", "05/11/2026", "PT Prima Reagen Husada", "Rapid Test Diagnostic Kit", "KEMENKES RI AKL 20303765432", "LOT-2610D", "04/2028", "30 Kit", "☑ YA", "☑ YA", "☑ YA", "☑ YA", "[✓] DITERIMA (Cold Chain)", "dr. PJT / Andi"),
    ("RCV-2026-1105", "08/11/2026", "PT Kimia Farma Trading", "Kasa Steril Hidrofil 16x16", "KEMENKES RI AKD 10901654321", "LOT-2608E", "08/2029", "80 Karton", "☑ YA", "☑ YA", "☑ YA", "☑ YA", "[✓] DITERIMA (Lolos)", "dr. PJT / Andi"),
    ("RCV-2026-1106", "10/11/2026", "PT Sumber Sehat Alkes", "Jarum Bedah Surgical Needle", "KEMENKES RI AKL 10902543210", "LOT-2607F", "07/2029", "15 Box", "☒ Rusak", "☒ Basah", "☑ YA", "☒ Tidak", "[✕] DITOLAK (Karantina)", "dr. PJT / Andi"),
]

r4 = 7
for row_d in qc_sample_data:
    ws4.row_dimensions[r4].height = 22
    is_z = (r4 % 2 == 1)
    
    ws4[f"A{r4}"] = row_d[0]; ws4[f"A{r4}"].alignment = align_center; ws4[f"A{r4}"].font = font_data_bold
    ws4[f"B{r4}"] = row_d[1]; ws4[f"B{r4}"].alignment = align_center
    ws4[f"C{r4}"] = row_d[2]; ws4[f"C{r4}"].alignment = align_left
    ws4[f"D{r4}"] = row_d[3]; ws4[f"D{r4}"].alignment = align_left; ws4[f"D{r4}"].font = font_data_bold
    ws4[f"E{r4}"] = row_d[4]; ws4[f"E{r4}"].alignment = align_left; ws4[f"E{r4}"].font = font_data_sm
    ws4[f"F{r4}"] = row_d[5]; ws4[f"F{r4}"].alignment = align_center
    ws4[f"G{r4}"] = row_d[6]; ws4[f"G{r4}"].alignment = align_center
    ws4[f"H{r4}"] = row_d[7]; ws4[f"H{r4}"].alignment = align_center
    
    for idx_c, col_c in enumerate(["I","J","K","L"]):
        ws4[f"{col_c}{r4}"] = row_d[8 + idx_c]
        ws4[f"{col_c}{r4}"].alignment = align_center
        if "YA" in row_d[8 + idx_c]:
            ws4[f"{col_c}{r4}"].font = font_check_green
        else:
            ws4[f"{col_c}{r4}"].font = font_check_red
            
    # Keputusan QC
    qc_dec_cell = ws4[f"M{r4}"]
    qc_dec_cell.value = row_d[12]
    qc_dec_cell.alignment = align_center
    if "DITERIMA" in row_d[12]:
        qc_dec_cell.font = font_check_green
        qc_dec_cell.fill = fill_sudah_ada
    else:
        qc_dec_cell.font = font_check_red
        qc_dec_cell.fill = fill_p1
        
    ws4[f"N{r4}"] = row_d[13]; ws4[f"N{r4}"].alignment = align_center; ws4[f"N{r4}"].font = font_data_sm

    for col_c in ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]:
        c = ws4[f"{col_c}{r4}"]
        c.border = border_cell
        if is_z and c.fill == PatternFill():
            c.fill = fill_zebra
    r4 += 1

# Blank rows for future entries
for i in range(7, 20):
    ws4.row_dimensions[r4].height = 20
    ws4[f"A{r4}"] = f"RCV-2026-11{i:02d}"; ws4[f"A{r4}"].alignment = align_center; ws4[f"A{r4}"].font = font_data_sm
    for col_c in ["B","C","D","E","F","G","H"]:
        ws4[f"{col_c}{r4}"].alignment = align_center
    for col_c in ["I","J","K","L"]:
        ws4[f"{col_c}{r4}"] = "☐"; ws4[f"{col_c}{r4}"].alignment = align_center
    ws4[f"M{r4}"] = "[ ] Menunggu"; ws4[f"M{r4}"].alignment = align_center; ws4[f"M{r4}"].font = font_data_sm
    for col_c in ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]:
        ws4[f"{col_c}{r4}"].border = border_cell
    r4 += 1

ws4.freeze_panes = "A7"

# Save Workbook
out_path_1 = "/Users/user/Downloads/maziya-3d-office/Checklist_Pengadaan_dan_Audit_CDAKB_PT_MMG.xlsx"
out_path_2 = "/Users/user/Downloads/PT Maziya Medical Global/09 Denah 3D Kantor dan Gudang (maziya-3d-office)/Checklist_Pengadaan_dan_Audit_CDAKB_PT_MMG.xlsx"

wb.save(out_path_1)
print(f"Saved: {out_path_1} ({os.path.getsize(out_path_1)/1024:.1f} KB)")

folder_mmg = "/Users/user/Downloads/PT Maziya Medical Global/09 Denah 3D Kantor dan Gudang (maziya-3d-office)"
if os.path.exists(folder_mmg):
    wb.save(out_path_2)
    print(f"Saved to PT MMG folder: {out_path_2}")

print("Spreadsheet generation complete!")
