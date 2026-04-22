import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# CONFIGURACIÓN DE ACTIVOS (RUTAS DINÁMICAS)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_LOGO_LIGHT = os.path.join(BASE_DIR, "claro.png")
RUTA_LOGO_DARK = os.path.join(BASE_DIR, "oscuro.png")

DATA_ICG = {
    "140 kg/cm2": {"cem": 7.01, "are": 0.51, "pie": 0.64, "agu": 0.184, "prop": "1:2.5:3.5"},
    "175 kg/cm2": {"cem": 8.43, "are": 0.54, "pie": 0.55, "agu": 0.185, "prop": "1:2.5:2.5"},
    "210 kg/cm2": {"cem": 9.73, "are": 0.52, "pie": 0.53, "agu": 0.186, "prop": "1:2:2"},
    "245 kg/cm2": {"cem": 11.50, "are": 0.50, "pie": 0.51, "agu": 0.187, "prop": "1:1.5:1.5"},
    "280 kg/cm2": {"cem": 13.34, "are": 0.45, "pie": 0.51, "agu": 0.189, "prop": "1:1:1.5"}
}

class ConcreteAppV8(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SISTEMA DE CÁLCULO DE MATERIALES | CORP. IC360 SAC")
        self.geometry("1280x850")
        self.minsize(1100, 750)
        ctk.set_appearance_mode("Dark")
        
        self.logo_empresa = None
        self.main_container = ctk.CTkFrame(self, fg_color=("#f0f0f0", "#0d1117"), corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        self.configurar_logo()
        self.show_home()

    def configurar_logo(self):
        try:
            if os.path.exists(RUTA_LOGO_LIGHT) and os.path.exists(RUTA_LOGO_DARK):
                img_l, img_d = Image.open(RUTA_LOGO_LIGHT), Image.open(RUTA_LOGO_DARK)
                self.logo_empresa = ctk.CTkImage(light_image=img_l, dark_image=img_d, size=(220, 70))
        except: pass

    def alternar_tema(self):
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    def clear_container(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def insertar_encabezado(self):
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=15)
        if self.logo_empresa:
            lbl = ctk.CTkLabel(header, image=self.logo_empresa, text="")
            lbl.pack(side="left")
            lbl._image = self.logo_empresa
        else:
            ctk.CTkLabel(header, text="CORPORACIÓN IC360 SAC", font=("Orbitron", 22, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Tema", command=self.alternar_tema, width=100).pack(side="right")

    def show_home(self):
        self.clear_container()
        self.insertar_encabezado()
        
        f = ctk.CTkFrame(self.main_container, fg_color=("#ffffff", "#161b22"), corner_radius=15, border_width=1)
        f.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.75)

        ctk.CTkLabel(f, text="Cálculo de Materiales", font=("Orbitron", 32, "bold"), text_color="#58a6ff").pack(pady=(30, 10))
        ctk.CTkLabel(f, text="Ing. Frank Falla Rojas", font=("Arial", 16), text_color="#8b949e").pack(pady=(0, 20))

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(pady=10, padx=50, fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1)

        # --- ETIQUETAS E INPUTS DE ENTRADA ---
        ctk.CTkLabel(grid, text="Resistencia f'c requerida:", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=15, sticky="w")
        self.combo_fc = ctk.CTkComboBox(grid, values=list(DATA_ICG.keys()), height=40, font=("Arial", 14))
        self.combo_fc.grid(row=1, column=0, padx=15, pady=(5, 20), sticky="ew")
        self.combo_fc.set("210 kg/cm2")
        
        ctk.CTkLabel(grid, text="Volumen Neto a vaciar (m3):", font=("Arial", 13, "bold")).grid(row=0, column=1, padx=15, sticky="w")
        self.ent_vol = ctk.CTkEntry(grid, placeholder_text="Ej: 5.5", height=40, font=("Arial", 14))
        self.ent_vol.grid(row=1, column=1, padx=15, pady=(5, 20), sticky="ew")

        ctk.CTkLabel(grid, text="Factor de Desperdicio (%):", font=("Arial", 13, "bold")).grid(row=2, column=0, padx=15, sticky="w")
        self.ent_desp = ctk.CTkEntry(grid, placeholder_text="%", height=40, font=("Arial", 14))
        self.ent_desp.insert(0, "5")
        self.ent_desp.grid(row=3, column=0, padx=15, pady=(5, 20), sticky="ew")

        ctk.CTkLabel(grid, text="Tipo de Aditivo:", font=("Arial", 13, "bold")).grid(row=2, column=1, padx=15, sticky="w")
        self.combo_adi = ctk.CTkComboBox(grid, values=["Ninguno", "Plastificante", "Superplastificante"], height=40, font=("Arial", 14))
        self.combo_adi.grid(row=3, column=1, padx=15, pady=(5, 20), sticky="ew")
        self.combo_adi.set("Ninguno")

        ctk.CTkButton(f, text="CALCULAR", fg_color="#238636", hover_color="#2ea043", height=60, font=("Arial", 16, "bold"), command=self.procesar_y_mostrar).pack(pady=30, padx=100, fill="x")

    def procesar_y_mostrar(self):
        try:
            fc, vol, desp = self.combo_fc.get(), float(self.ent_vol.get()), float(self.ent_desp.get())/100
            v_t = vol * (1 + desp); d = DATA_ICG[fc]
            cem = v_t * d['cem']
            
            tipo_adi = self.combo_adi.get()
            ml_p_bolsa = 500 if "Super" in tipo_adi else (250 if "Plastificante" == tipo_adi else 0)
            cant_aditivo = (cem * ml_p_bolsa) / 1000

            self.data_reporte = {
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "fc": fc, "vol_n": vol, "v_f": v_t, "desp": desp*100,
                "cem": cem, "prop": d['prop'], "are_b": (v_t * d['are']) * 37, "are_m3": v_t * d['are'],
                "pie_b": (v_t * d['pie']) * 37, "pie_m3": v_t * d['pie'], "agu_l": v_t * d['agu'] * 1000, "agu_m3": v_t * d['agu'],
                "adi": cant_aditivo, "adi_t": tipo_adi
            }
            self.clear_container(); self.build_results_ui()
        except: messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos.")

    def build_results_ui(self):
        self.insertar_encabezado()
        nav = ctk.CTkFrame(self.main_container, fg_color=("#e1e4e8", "#161b22"), height=70)
        nav.pack(fill="x")
        ctk.CTkLabel(nav, text=f"RESULTADOS: f'c {self.data_reporte['fc']}", font=("Orbitron", 18, "bold"), text_color="#448996").pack(side="left", padx=40)
        ctk.CTkButton(nav, text="EXPORTAR PDF", fg_color="#d73a49", width=150, command=self.exportar_pdf).pack(side="right", padx=10)
        ctk.CTkButton(nav, text="NUEVO CÁLCULO", fg_color="#18991c", width=140, command=self.show_home).pack(side="right", padx=10)

        grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Configuración de 3 columnas para albergar las 5 tarjetas proporcionalmente
        grid_container.columnconfigure((0, 1, 2), weight=1)
        grid_container.rowconfigure((0, 1), weight=1)

        self.create_card(grid_container, "CEMENTO", f"{self.data_reporte['cem']:.2f}", "BOLSAS", "#1f6aa5", 0, 0)
        self.create_card(grid_container, "ARENA GRUESA", f"{self.data_reporte['are_b']:.1f} Baldes", f"{self.data_reporte['are_m3']:.2f} m3", "#c0392b", 0, 1)
        self.create_card(grid_container, "PIEDRA CHANCADA", f"{self.data_reporte['pie_b']:.1f} Baldes", f"{self.data_reporte['pie_m3']:.2f} m3", "#d35400", 0, 2)
        
        self.create_card(grid_container, "AGUA TOTAL", f"{self.data_reporte['agu_l']:.1f} Litros", f"{self.data_reporte['agu_m3']:.3f} m3", "#2980b9", 1, 0)
        
        # TARJETA DE ADITIVO INTEGRADA
        color_adi = "#8e44ad" if self.data_reporte['adi'] > 0 else "#7f8c8d"
        self.create_card(grid_container, f"ADITIVO {self.data_reporte['adi_t'].upper()}", f"{self.data_reporte['adi']:.2f}", "LITROS", color_adi, 1, 1)

    def create_card(self, master, title, val, unit, color, r, c):
        card = ctk.CTkFrame(master, border_width=2, border_color=color, corner_radius=15)
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True)
        ctk.CTkLabel(inner, text=title, font=("Arial", 15, "bold"), text_color=color).pack(pady=5)
        ctk.CTkLabel(inner, text=val, font=("Orbitron", 42, "bold")).pack(pady=5)
        ctk.CTkLabel(inner, text=unit, font=("Arial", 16, "bold"), text_color="#8b949e").pack(pady=5)

    def exportar_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Documento PDF", "*.pdf")])
        if not path: return
        doc = SimpleDocTemplate(path, pagesize=letter)
        content = []
        styles = getSampleStyleSheet()
        content.append(Paragraph(f"REPORTE TÉCNICO - CORP. IC360 SAC", styles['Title']))
        content.append(Paragraph(f"<b>Responsable:</b> Ing. Frank Falla Rojas | <b>f'c:</b> {self.data_reporte['fc']}", styles['Normal']))
        content.append(Spacer(1, 20))
        data = [['MATERIAL', 'CANTIDAD COMERCIAL', 'VOLUMEN (m3)'],
                ['Cemento Portland', f"{self.data_reporte['cem']:.2f} Bolsas", "-"],
                ['Arena Gruesa', f"{self.data_reporte['are_b']:.1f} Baldes", f"{self.data_reporte['are_m3']:.3f}"],
                ['Piedra Chancada', f"{self.data_reporte['pie_b']:.1f} Baldes", f"{self.data_reporte['pie_m3']:.3f}"],
                ['Agua Potable', f"{self.data_reporte['agu_l']:.1f} Litros", f"{self.data_reporte['agu_m3']:.3f}"],
                [f"Aditivo {self.data_reporte['adi_t']}", f"{self.data_reporte['adi']:.2f} Litros", "-"]]
        t = Table(data, colWidths=[160, 160, 160])
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1c2e")),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        content.append(t)
        doc.build(content)
        messagebox.showinfo("PDF", "Reporte generado y guardado.")

if __name__ == "__main__":
    app = ConcreteAppV8()
    app.mainloop()