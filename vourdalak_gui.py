import os
import sys
import json
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Add paths for internal module imports
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik"))
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory"))
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik" / "Toolchain" / "Proxy"))

class VourdalakGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vourdalak | Behavioral Context & OSINT Orchestrator")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        self.root_dir = Path(__file__).parent.absolute()
        self.okhotnik_cfg_path = self.root_dir / "01_Hunt" / "Okhotnik" / "okhotnik_config.json"
        self.smotrityel_cfg_path = self.root_dir / "01_Hunt" / "Smotrityel" / "smotrityel_config.json"
        
        self.load_configs()

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="VOURDALAK", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=20)

        self.btn_hunt = ctk.CTkButton(self.sidebar, text="Hunt Console", command=lambda: self.show_frame("hunt"))
        self.btn_hunt.pack(pady=10, padx=20)

        self.btn_vault = ctk.CTkButton(self.sidebar, text="Armory Vault", command=lambda: self.show_frame("vault"))
        self.btn_vault.pack(pady=10, padx=20)

        self.btn_network = ctk.CTkButton(self.sidebar, text="Network Hub", command=lambda: self.show_frame("network"))
        self.btn_network.pack(pady=10, padx=20)

        # Main Content Area
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.frames = {}
        self.setup_hunt_frame()
        self.setup_vault_frame()
        self.setup_network_frame()

        self.show_frame("hunt")

    def load_configs(self):
        try:
            with open(self.okhotnik_cfg_path, 'r') as f: self.ok_cfg = json.load(f)
            with open(self.smotrityel_cfg_path, 'r') as f: self.sm_cfg = json.load(f)
        except:
            messagebox.showerror("Error", "Configs not found. Run hunt_deploy.py first.")
            sys.exit()

    def show_frame(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # --- FRAME: HUNT CONSOLE ---
    def setup_hunt_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["hunt"] = f
        
        ctk.CTkLabel(f, text="OPERATIONAL CONSOLE", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        input_group = ctk.CTkFrame(f)
        input_group.pack(fill="x", pady=10)
        
        self.target_input = ctk.CTkEntry(input_group, placeholder_text="Target Name (e.g. John_Doe)", width=300)
        self.target_input.pack(side="left", padx=10, pady=10)
        
        self.alias_input = ctk.CTkEntry(input_group, placeholder_text="Known Aliases / Emails", width=400)
        self.alias_input.pack(side="left", padx=10, pady=10)

        # Tool Checklist
        self.tool_checks = {}
        checklist_group = ctk.CTkFrame(f)
        checklist_group.pack(fill="x", pady=5)
        ctk.CTkLabel(checklist_group, text="Enabled Tools:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        
        for tool_name in self.ok_cfg.get("tools", {}).keys():
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(checklist_group, text=tool_name.capitalize(), variable=var)
            cb.pack(side="left", padx=5)
            self.tool_checks[tool_name] = var

        ctrl_group = ctk.CTkFrame(f)
        ctrl_group.pack(fill="x", pady=5)
        
        self.btn_start_hunt = ctk.CTkButton(ctrl_group, text="INITIATE HUNT", fg_color="#e74c3c", hover_color="#c0392b", command=self.run_hunt_thread)
        self.btn_start_hunt.pack(side="left", padx=10, pady=10)
        
        self.btn_start_weave = ctk.CTkButton(ctrl_group, text="START WEAVING", fg_color="#2ecc71", hover_color="#27ae60", command=self.run_weave_thread)
        self.btn_start_weave.pack(side="left", padx=10, pady=10)

        self.log_output = ctk.CTkTextbox(f, height=400)
        self.log_output.pack(fill="both", expand=True, pady=10)

    # --- FRAME: ARMORY VAULT ---
    def setup_vault_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["vault"] = f
        ctk.CTkLabel(f, text="CREDENTIAL ARMORY", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        # Simple management view
        self.vault_display = ctk.CTkTextbox(f, height=300)
        self.vault_display.pack(fill="both", expand=True, pady=10)
        self.refresh_vault_display()
        
        add_group = ctk.CTkFrame(f)
        add_group.pack(fill="x", pady=10)
        
        self.acc_platform = ctk.CTkOptionMenu(add_group, values=["instagram", "twitter", "facebook", "gmail"])
        self.acc_platform.pack(side="left", padx=5)
        
        self.acc_user = ctk.CTkEntry(add_group, placeholder_text="Username")
        self.acc_user.pack(side="left", padx=5)
        
        self.acc_pass = ctk.CTkEntry(add_group, placeholder_text="Password", show="*")
        self.acc_pass.pack(side="left", padx=5)
        
        ctk.CTkButton(add_group, text="Add Account", command=self.add_vault_acc).pack(side="left", padx=5)

    # --- FRAME: NETWORK HUB ---
    def setup_network_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["network"] = f
        ctk.CTkLabel(f, text="NETWORK TOPOLOGY", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        self.tor_switch = ctk.CTkSwitch(f, text="ENABLE TOR IP OBSCURATION", command=self.toggle_tor)
        if self.ok_cfg.get("proxy_settings", {}).get("use_tor"): self.tor_switch.select()
        self.tor_switch.pack(pady=20, anchor="w")
        
        ctk.CTkLabel(f, text="Custom Proxy (HTTP/HTTPS):").pack(anchor="w")
        self.proxy_addr = ctk.CTkEntry(f, width=400)
        self.proxy_addr.insert(0, self.ok_cfg.get("proxy_settings", {}).get("http", ""))
        self.proxy_addr.pack(pady=5, anchor="w")
        
        ctk.CTkButton(f, text="Save Network Settings", command=self.save_network).pack(pady=10, anchor="w")

    # --- LOGIC ---
    def toggle_tor(self):
        enabled = self.tor_switch.get()
        self.ok_cfg["proxy_settings"]["enabled"] = bool(enabled)
        self.ok_cfg["proxy_settings"]["use_tor"] = bool(enabled)
        
    def save_network(self):
        addr = self.proxy_addr.get()
        self.ok_cfg["proxy_settings"]["http"] = addr
        self.ok_cfg["proxy_settings"]["https"] = addr
        with open(self.okhotnik_cfg_path, 'w') as f: json.dump(self.ok_cfg, f, indent=4)
        messagebox.showinfo("Success", "Network settings updated.")

    def refresh_vault_display(self):
        vault_path = self.root_dir / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory" / "armory_vault.json"
        if vault_path.exists():
            with open(vault_path, 'r') as f:
                data = json.load(f)
                self.vault_display.delete("1.0", "end")
                self.vault_display.insert("end", json.dumps(data, indent=4))

    def add_vault_acc(self):
        p, u, pw = self.acc_platform.get(), self.acc_user.get(), self.acc_pass.get()
        if p and u and pw:
            cmd = [sys.executable, str(self.root_dir / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory" / "vault_manager.py"), "--add", p, u, pw]
            subprocess.run(cmd)
            self.refresh_vault_display()
            self.acc_user.delete(0, "end"); self.acc_pass.delete(0, "end")

    def log(self, msg):
        self.log_output.insert("end", f"{msg}\n")
        self.log_output.see("end")

    def run_hunt_thread(self):
        target = self.target_input.get()
        aliases = self.alias_input.get()
        if not target: return
        
        enabled_tools = [t for t, var in self.tool_checks.items() if var.get()]
        if not enabled_tools:
            messagebox.showwarning("Warning", "No tools selected.")
            return

        self.btn_start_hunt.configure(state="disabled")
        threading.Thread(target=self.execute_hunt, args=(target, aliases, enabled_tools), daemon=True).start()

    def execute_hunt(self, target, aliases, enabled_tools):
        self.log(f"[*] INITIATING HUNT: {target}...")
        self.log(f"[*] ENABLED TOOLS: {', '.join(enabled_tools)}")
        
        tool_arg = ",".join(enabled_tools)
        
        proc = subprocess.Popen(
            [sys.executable, "01_Hunt/Okhotnik/okhotnik_core.py", target, aliases, "--tools", tool_arg],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(self.root_dir)
        )
        
        for line in iter(proc.stdout.readline, ""):
            self.log(line.strip())
        
        proc.wait()
        self.btn_start_hunt.configure(state="normal")
        self.log("[+] HUNT SEQUENCE TERMINATED.")

    def run_weave_thread(self):
        self.btn_start_weave.configure(state="disabled")
        threading.Thread(target=self.execute_weave, daemon=True).start()

    def execute_weave(self):
        self.log("[*] STARTING MULTIMODAL WEAVER...")
        proc = subprocess.Popen(
            [sys.executable, "01_Hunt/Smotrityel/smotrityel_core.py"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(self.root_dir)
        )
        for line in iter(proc.stdout.readline, ""):
            self.log(line.strip())
        proc.wait()
        self.btn_start_weave.configure(state="normal")
        self.log("[+] WEAVING COMPLETE.")

if __name__ == "__main__":
    app = VourdalakGUI()
    app.mainloop()
