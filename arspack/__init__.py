from customtkinter import *
import subprocess
import threading
import sys
import os

# Görünüm ve tema ayarları
set_appearance_mode("system")
set_default_color_theme("blue")

class ARSPACK(CTk):
    def __init__(self):
        super().__init__()
        self.title("ARSPACK - Python Package Installer - ArsTech")
        self.setGUI()

    def setGUI(self):
        # Ekran boyutlarını hesapla ve ortala
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()

        self.frameWidth = int(self.screenWidth / 5 * 1.25)
        self.frameHeight = int(self.screenHeight / 5 * 1.5)

        self.frameX = int((self.screenWidth - self.frameWidth) / 2)
        self.frameY = int((self.screenHeight - self.frameHeight) / 2)
        
        self.minsize(width=500, height=400)

        self.geo = f"{self.frameWidth}x{self.frameHeight}+{self.frameX}+{self.frameY}"
        self.geometry(self.geo)

        # Üst başlık
        self.header_label = CTkLabel(self, text="ARSPACK", 
                                     font=("Sans Serif", 60, "bold"), anchor="center")
        self.header_label.pack(fill=X, padx=20, pady=30)

        # Paket ismi giriş alanı ve buton
        self.input_frame = CTkFrame(self, fg_color="transparent", bg_color="transparent")
        self.input_frame.pack(fill=X, padx=20, pady=(20, 0))

        self.package_entry = CTkEntry(self.input_frame, placeholder_text="Enter package name", height=37.5, corner_radius=7.5, font=("Sans Serif", 15))
        self.package_entry.pack(side="left", fill=X, expand=True, padx=(0, 20))
        self.package_entry.bind("<Return>", lambda event: self.handle_installation())

        self.install_button = CTkButton(self.input_frame, text="Install Package", 
                                        command=self.handle_installation, height=37.5, corner_radius=7.5)
        self.install_button.pack(side="right")

        # Yöntem seçenekleri (pip, conda)
        self.method_frame = CTkFrame(self, fg_color="transparent")
        self.method_frame.pack(pady=(20, 0), padx=10, fill="x")

        self.install_methods_ = ["pip", "conda"]
        self.install_methods = self.check_tool_existence(self.install_methods_)
        self.selected_method = "pip"
        self.buttons = {}

        # Butonları oluştur
        self.create_buttons()

        # Terminal benzeri durum mesajlarını gösteren textbox
        self.log_textbox = CTkTextbox(self, width=self.frameWidth, height=150, border_width=1, corner_radius=7.5, border_spacing=10)
        self.log_textbox.pack(fill=BOTH, expand=True, padx=20, pady=(20, 20), side=BOTTOM)
        self.log_textbox.configure(font=("Consolas", 15), fg_color="#1e1e1e", 
                                   text_color="#dcdcdc", wrap="none")
        self.log_textbox.insert("end", "Welcome to Python Package Installer\n")
        self.log_textbox.configure(state="disabled")  # Düzenlenemez hale getir

        # Varsayılan derleyiciyi seçiyoruz (sistemde yüklü olan varsayılan Python yorumlayıcısı)
        self.selected_compiler = sys.executable  # Burada varsayılan Python yorumlayıcısını alıyoruz

    def check_tool_existence(self, tool_name_):
        list = []
        for tool_name in tool_name_:
            try:
                # Komutu çalıştır ve çıktıyı kontrol et
                result = subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    # Çıktıyı güvenli şekilde decode et
                    output = result.stdout.decode("utf-8", errors="replace").strip()
                    list.append((tool_name))
            except FileNotFoundError: ...
        return list

    def create_buttons(self):
        for method in self.install_methods:
            button = CTkButton(
                self.method_frame,
                text=method,
                height=40,
                corner_radius=7.5,
                fg_color="#3b3b3b",
                text_color="white",
                command=lambda m=method: self.select_method(m),
                font=("Arial", 18)
            )
            button.pack(side="left", fill="x", expand=True, padx=10, pady=0)  # Butonlar yatayda genişleyecek
            self.buttons[method] = button

        # İlk seçim için rengi güncelle
        self.update_button_colors()

    def select_method(self, method):
        # Seçili yöntemi güncelle ve renk değiştir
        self.selected_method = method
        self.update_button_colors()

    def update_button_colors(self):
        # Tüm butonların renklerini ayarla
        for method, button in self.buttons.items():
            button.configure(fg_color="#1f6aa5" if method == self.selected_method else "#3b3b3b")

    def handle_installation(self):
        package_name = self.package_entry.get().strip()
        if not package_name:
            self.show_error()
            return

        # Paket kontrol ve yükleme işlemini ayrı bir thread ile başlat
        threading.Thread(target=self.install_package, args=(package_name,), daemon=True).start()

    def install_package(self, package_name):
        try:
            # Paket var mı kontrol et
            result = subprocess.run(
                [self.selected_compiler, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.update_terminal(f"'{package_name}' is already installed.", "green")
            else:
                # Paket yükle
                self.update_terminal(f"Installing '{package_name}'...", "blue")
                install_result = subprocess.run(
                    [self.selected_compiler, "-m", "pip", "install", package_name],
                    capture_output=True,
                    text=True
                )
                if install_result.returncode == 0:
                    self.update_terminal(f"'{package_name}' installed successfully!", "green")
                else:
                    self.update_terminal(f"Failed to install '{package_name}'.", "red")

                # Output'u terminale yazdırma
                if install_result.stdout:
                    self.update_terminal(install_result.stdout+f"\n'{package_name}' installed successfully!", "white")
                if install_result.stderr:
                    self.update_terminal(install_result.stderr, "red")
            self.package_entry.delete(0, END)
            self.focus()
        except Exception as e:
            self.update_terminal(f"An error occurred: {str(e)}", "red")

    def update_terminal(self, message, color="white"):
        # Textbox içine mesaj ekle
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")  # Otomatik olarak en son satıra kaydır

    def show_error(self):
        # CTkEntry'nin kenar rengini kırmızı yap
        self.package_entry.configure(border_color="#de6868")
        self.after(1000, lambda: self.package_entry.configure(border_color=""))

def main():
    app = ARSPACK()
    app.mainloop()

# Uygulamayı başlat
if __name__ == "__main__":
    main()