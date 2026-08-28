import base64
import json
import os
import ctypes
import tkinter as tk
from tkinter import Button, Entry, Frame, Label, Scrollbar, Tk, END, messagebox, ttk
import requests

CONFIG_FILE = "config.json"
selected_content = None
detected_extension = ""


def load_config():
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return {}


def save_config(token, filename=""):
  config = load_config()
  config["token"] = token
  if filename:
    config["last_filename"] = filename
  try:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      json.dump(config, f)
  except:
    pass


def native_save_file_dialog(default_filename=""):
  try:
    class OPENFILENAME(ctypes.Structure):
      _fields_ = [
          ("lStructSize", ctypes.c_ulong),
          ("hwndOwner", ctypes.c_void_p),
          ("hInstance", ctypes.c_void_p),
          ("lpstrFilter", ctypes.c_wchar_p),
          ("lpstrCustomFilter", ctypes.c_wchar_p),
          ("nMaxCustFilter", ctypes.c_ulong),
          ("nFilterIndex", ctypes.c_ulong),
          ("lpstrFile", ctypes.c_wchar_p),
          ("nMaxFile", ctypes.c_ulong),
          ("lpstrFileTitle", ctypes.c_wchar_p),
          ("nMaxFileTitle", ctypes.c_ulong),
          ("lpstrInitialDir", ctypes.c_wchar_p),
          ("lpstrTitle", ctypes.c_wchar_p),
          ("Flags", ctypes.c_ulong),
          ("nFileOffset", ctypes.c_ushort),
          ("nFileExtension", ctypes.c_ushort),
          ("lpstrDefExt", ctypes.c_wchar_p),
          ("lCustData", ctypes.c_void_p),
          ("lpfnHook", ctypes.c_void_p),
          ("lpTemplateName", ctypes.c_wchar_p),
          ("pvReserved", ctypes.c_void_p),
          ("dwReserved", ctypes.c_ulong),
          ("flagsEx", ctypes.c_ulong),
      ]

    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.hwndOwner = root.winfo_id()
    ofn.lpstrFilter = "All Files\0*.*\0M3U Files\0*.m3u\0Executables\0*.exe\0\0"
    
    # নতুন বাফারে একদম খালি বা ডিফল্ট নাম দিয়ে বাফার তৈরি যাতে অটো ক্রিয়েট না হয়
    buf = ctypes.create_unicode_buffer(default_filename, 512)
    ofn.lpstrFile = ctypes.cast(buf, ctypes.c_wchar_p)
    ofn.nMaxFile = 512
    ofn.lpstrTitle = "Save File As"
    # OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT | OFN_NOREADONLYRETURN
    ofn.Flags = 0x00000800 | 0x00000002 | 0x00008000

    if ctypes.windll.comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
      return ofn.lpstrFile
  except Exception:
    pass
  return ""


def native_open_file_dialog():
  try:
    class OPENFILENAME(ctypes.Structure):
      _fields_ = [
          ("lStructSize", ctypes.c_ulong),
          ("hwndOwner", ctypes.c_void_p),
          ("hInstance", ctypes.c_void_p),
          ("lpstrFilter", ctypes.c_wchar_p),
          ("lpstrCustomFilter", ctypes.c_wchar_p),
          ("nMaxCustFilter", ctypes.c_ulong),
          ("nFilterIndex", ctypes.c_ulong),
          ("lpstrFile", ctypes.c_wchar_p),
          ("nMaxFile", ctypes.c_ulong),
          ("lpstrFileTitle", ctypes.c_wchar_p),
          ("nMaxFileTitle", ctypes.c_ulong),
          ("lpstrInitialDir", ctypes.c_wchar_p),
          ("lpstrTitle", ctypes.c_wchar_p),
          ("Flags", ctypes.c_ulong),
          ("nFileOffset", ctypes.c_ushort),
          ("nFileExtension", ctypes.c_ushort),
          ("lpstrDefExt", ctypes.c_wchar_p),
          ("lCustData", ctypes.c_void_p),
          ("lpfnHook", ctypes.c_void_p),
          ("lpTemplateName", ctypes.c_wchar_p),
          ("pvReserved", ctypes.c_void_p),
          ("dwReserved", ctypes.c_ulong),
          ("flagsEx", ctypes.c_ulong),
      ]

    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.hwndOwner = root.winfo_id()
    ofn.lpstrFilter = "All Files\0*.*\0M3U Files\0*.m3u\0Executables\0*.exe\0\0"
    
    buf = ctypes.create_unicode_buffer(512)
    ofn.lpstrFile = ctypes.cast(buf, ctypes.c_wchar_p)
    ofn.nMaxFile = 512
    ofn.lpstrTitle = "Select Any File"
    ofn.Flags = 0x00080000 | 0x00001000 | 0x00001008

    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
      return ofn.lpstrFile
  except Exception:
    pass
  return ""


def browse_file():
  global selected_content, detected_extension
  file_path = native_open_file_dialog()
  if file_path:
    entry_source.delete(0, END)
    entry_source.insert(0, file_path)
    
    _, ext = os.path.splitext(file_path)
    detected_extension = ext.lower()
    base_name = os.path.basename(file_path)
    name_without_ext, _ = os.path.splitext(base_name)

    entry_filename.delete(0, END)
    entry_filename.insert(0, name_without_ext)

    try:
      with open(file_path, "rb") as f:
        file_bytes = f.read()
        selected_content = base64.b64encode(file_bytes).decode("utf-8")
      status_label.config(text=f"✨ File loaded! Extension: {detected_extension}", fg="#00e676")
    except Exception as e:
      status_label.config(text=f"Error reading file: {e}", fg="#ff5252")


def load_from_link():
  global selected_content, detected_extension
  url = entry_source.get().strip()
  if not url or not url.startswith("http"):
    messagebox.showerror("Error", "Please enter a valid HTTP/HTTPS link!")
    return

  try:
    status_label.config(text="📥 Downloading data from link...", fg="#00b0ff")
    root.update()
    response = requests.get(url)
    response.raise_for_status()
    selected_content = base64.b64encode(response.content).decode("utf-8")
    
    parsed_path = url.split("?")[0]
    _, ext = os.path.splitext(parsed_path)
    if ext:
      detected_extension = ext.lower()
      name_from_url = os.path.basename(parsed_path)
      name_without_ext, _ = os.path.splitext(name_from_url)
      entry_filename.delete(0, END)
      entry_filename.insert(0, name_without_ext)
    else:
      detected_extension = ".txt"

    status_label.config(text="✨ Online link loaded successfully!", fg="#00e676")
    messagebox.showinfo("Success", "Content loaded successfully from link!")
  except Exception as e:
    status_label.config(text="❌ Failed to fetch data from link!", fg="#ff5252")
    messagebox.showerror("Error", f"An error occurred: {e}")


def fetch_repositories():
  token = entry_token.get().strip()
  if not token:
    messagebox.showerror("Error", "Please enter your GitHub Token first!")
    return

  save_config(token)
  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
  }
  api_url = "https://api.github.com/user/repos?per_page=100"

  try:
    status_label.config(text="🔄 Loading repositories...", fg="#00b0ff")
    root.update()
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
      repos = response.json()
      repo_names = [repo["full_name"] for repo in repos]
      
      repo_combobox['values'] = repo_names
      if repo_names:
        repo_combobox.set(repo_names[0])
        fetch_repository_files()
      
      status_label.config(text="✨ Repositories loaded successfully!", fg="#00e676")
    else:
      err_msg = response.json().get("message", response.text)
      raise Exception(f"GitHub API Error ({response.status_code}): {err_msg}")

  except Exception as e:
    status_label.config(text="❌ Failed to load repositories!", fg="#ff5252")
    messagebox.showerror("Authentication Error", f"Please check if your token is valid: {e}")


def fetch_repository_files(event=None):
  token = entry_token.get().strip()
  repo_name = repo_combobox.get().strip()

  if not token or not repo_name:
    return

  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
  }
  api_url = f"https://api.github.com/repos/{repo_name}/contents/"

  try:
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
      for item in file_tree.get_children():
        file_tree.delete(item)
      contents = response.json()
      if isinstance(contents, list):
        for idx, item in enumerate(contents, start=1):
          if item["type"] == "file":
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            file_tree.insert("", END, values=(f"{idx}", f"  {item['name']}"), tags=(tag,))
    else:
      for item in file_tree.get_children():
        file_tree.delete(item)
  except Exception:
    pass


def upload_to_github():
  global selected_content, detected_extension
  token = entry_token.get().strip()
  repo_name = repo_combobox.get().strip()
  custom_name = entry_filename.get().strip()

  if not token or not repo_name or not custom_name:
    messagebox.showerror(
        "Error", "Please provide token, select a repository, and enter a filename!"
    )
    return

  if not selected_content:
    messagebox.showerror(
        "Error",
        "No content loaded to upload! Please provide a file or link.",
    )
    return

  if not custom_name.lower().endswith(detected_extension):
    file_path = custom_name + detected_extension
  else:
    file_path = custom_name

  try:
    status_label.config(
        text="🚀 Uploading to GitHub, please wait...", fg="#00b0ff"
    )
    root.update()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"

    get_resp = requests.get(api_url, headers=headers)
    sha = None
    if get_resp.status_code == 200:
      sha = get_resp.json().get("sha")

    data = {
        "message": (
            f"Update {file_path} via Pro Manager"
            if sha
            else f"Create {file_path} via Pro Manager"
        ),
        "content": selected_content,
    }
    if sha:
      data["sha"] = sha

    put_resp = requests.put(api_url, headers=headers, json=data)

    if put_resp.status_code in [200, 201]:
      save_config(token, custom_name)
      status_label.config(text="🎉 Successfully uploaded to GitHub!", fg="#00e676")
      messagebox.showinfo(
          "Success",
          f"File successfully uploaded/replaced as '{file_path}' on GitHub!",
      )
      fetch_repository_files()
    else:
      err_msg = put_resp.json().get("message", put_resp.text)
      raise Exception(f"GitHub API Error ({put_resp.status_code}): {err_msg}")

  except Exception as e:
    status_label.config(text="❌ Upload failed!", fg="#ff5252")
    messagebox.showerror("Connection Error", f"Failed to upload: {e}")


def download_selected_file(event=None):
  selected_items = file_tree.selection()
  if not selected_items:
    messagebox.showerror("Error", "Please select a file from the list to download!")
    return

  token = entry_token.get().strip()
  repo_name = repo_combobox.get().strip()
  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
  }

  for item in selected_items:
    filename = file_tree.item(item, "values")[1].strip()
    
    # প্রথমে উইন্ডোজের নিজস্ব সেভ ডায়ালগ কল করা হলো (ইউজার সেভ বা ক্যান্সেল করার জন্য)
    save_path = native_save_file_dialog(filename)
    
    # যদি ইউজার 'Cancel' করে বা ডায়ালগ বন্ধ করে দেয়, তবে save_path খালি আসবে এবং ডাউনলোড প্রক্রিয়া সম্পূর্ণ বাতিল হবে
    if not save_path:
      status_label.config(text="✨ Download cancelled", fg="#90caf9")
      return

    api_url = f"https://api.github.com/repos/{repo_name}/contents/{filename}"

    try:
      status_label.config(text=f"📥 Downloading '{filename}'...", fg="#00b0ff")
      root.update()

      response = requests.get(api_url, headers=headers)
      if response.status_code == 200:
        file_data = response.json()
        
        if "download_url" in file_data and file_data["download_url"]:
          download_url = file_data["download_url"]
          file_response = requests.get(download_url)
          if file_response.status_code == 200:
            file_content_bytes = file_response.content
          else:
            raise Exception("Failed to fetch file from direct download URL.")
        elif "content" in file_data:
          file_content_bytes = base64.b64decode(file_data["content"].replace("\n", ""))
        else:
          raise Exception("File content not found in repository response.")

        # ইউজার কনফার্ম করার পরেই কেবল ফাইল রাইট করা হবে
        with open(save_path, "wb") as f:
          f.write(file_content_bytes)
        
        actual_size_kb = len(file_content_bytes) / 1024
        status_label.config(text="✨ File downloaded successfully!", fg="#00e676")
        messagebox.showinfo(
            "Success", 
            f"File successfully downloaded!\nPath: {save_path}\nSize: {actual_size_kb:.2f} KB"
        )
      else:
        raise Exception(f"GitHub API Error: {response.status_code}")

    except Exception as e:
      status_label.config(text="❌ Download failed!", fg="#ff5252")
      messagebox.showerror("Error", f"Could not download file: {e}")


def delete_selected_files():
  selected_items = file_tree.selection()
  if not selected_items:
    messagebox.showerror(
        "Error", "Please select one or more files from the list to delete!"
    )
    return

  files_to_delete = []
  for item in selected_items:
    val = file_tree.item(item, "values")[1].strip()
    files_to_delete.append(val)
  
  if not messagebox.askyesno(
      "Confirmation",
      f"Are you sure you want to permanently delete the following file(s) from GitHub?\n\n" + "\n".join(files_to_delete),
  ):
    return

  token = entry_token.get().strip()
  repo_name = repo_combobox.get().strip()
  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
  }

  success_count = 0
  try:
    status_label.config(text="🗑️ Deleting selected files...", fg="#00b0ff")
    root.update()

    for filename in files_to_delete:
      api_url = f"https://api.github.com/repos/{repo_name}/contents/{filename}"
      get_resp = requests.get(api_url, headers=headers)
      if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")
        data = {"message": f"Delete {filename} via Pro Manager", "sha": sha}
        del_resp = requests.delete(api_url, headers=headers, json=data)
        if del_resp.status_code == 200:
          success_count += 1

    if success_count > 0:
      status_label.config(text="✨ Selected files deleted successfully!", fg="#00e676")
      messagebox.showinfo("Success", f"Files successfully deleted from GitHub!")
      fetch_repository_files()
    else:
      messagebox.showerror("Error", "Could not delete the selected files!")

  except Exception as e:
    status_label.config(text="❌ Deletion failed!", fg="#ff5252")
    messagebox.showerror("Error", f"An error occurred: {e}")


# UI Design
root = Tk()
root.title("IPTV M3U GitHub Manager Pro")
root.geometry("580x760")
root.config(bg="#1e1e2f")
root.minsize(520, 680)
root.resizable(True, True)

header_frame = Label(
    root,
    text="⚡ GitHub Universal File Manager Pro ⚡",
    bg="#2d2d44",
    fg="#00ffcc",
    font=("Segoe UI", 12, "bold"),
    pady=8,
)
header_frame.pack(fill="x")

form_frame = Label(root, bg="#1e1e2f")
form_frame.pack(pady=4)


def create_label(parent, text):
  return Label(
      parent,
      text=text,
      bg="#1e1e2f",
      font=("Segoe UI", 9, "bold"),
      fg="#cfd8dc",
      anchor="e",
  )


create_label(form_frame, "GitHub Token:").grid(
    row=0, column=0, sticky="e", padx=5, pady=3
)
entry_token = Entry(
    form_frame,
    width=34,
    show="*",
    font=("Segoe UI", 10),
    bg="#2d2d44",
    fg="#ffffff",
    insertbackground="white",
    relief="flat",
)
entry_token.grid(row=0, column=1, padx=5, pady=3, ipady=2)

Button(
    form_frame,
    text="🔄 Load",
    command=fetch_repositories,
    width=6,
    bg="#ab47bc",
    fg="white",
    font=("Segoe UI", 8, "bold"),
    relief="flat",
    cursor="hand2",
).grid(row=0, column=2, padx=4)

create_label(form_frame, "Select Repository:").grid(
    row=1, column=0, sticky="e", padx=5, pady=3
)

repo_combobox = ttk.Combobox(
    form_frame, width=32, font=("Segoe UI", 10), state="readonly"
)
repo_combobox.grid(row=1, column=1, columnspan=2, padx=5, pady=3, ipady=2)
repo_combobox.bind("<<ComboboxSelected>>", fetch_repository_files)

# Treeview Style Configuration
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#222233",
    foreground="#00ffcc",
    fieldbackground="#222233",
    font=("Segoe UI", 10),
    rowheight=30,
    borderwidth=1,
    relief="solid"
)

style.configure(
    "Treeview.Heading",
    background="#3f51b5",
    foreground="white",
    font=("Segoe UI", 9, "bold"),
    relief="raised",
    borderwidth=1
)

style.map(
    "Treeview",
    background=[('selected', '#1976d2'), ('active', '#1976d2')],
    foreground=[('selected', '#ffffff'), ('active', '#ffffff')],
)
style.map(
    "Treeview.Heading",
    background=[('active', '#303f9f')],
    foreground=[('active', '#ffffff')],
)

table_frame = Label(root, bg="#1e1e2f")
table_frame.pack(pady=3, padx=20, fill="both", expand=True)

file_tree = ttk.Treeview(
    table_frame, columns=("No", "Filename"), show="headings", selectmode="extended"
)
file_tree.heading("No", text="SL")
file_tree.heading("Filename", text="Repository File Name (Double click to Download)")

file_tree.column("No", width=55, anchor="center", stretch=False)
file_tree.column("Filename", width=435, anchor="w", stretch=True)

file_tree.tag_configure("oddrow", background="#222233", foreground="#00ffcc")
file_tree.tag_configure("evenrow", background="#2b2b40", foreground="#00ffcc")

file_tree.bind("<Double-1>", download_selected_file)

file_tree.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(table_frame, orient="vertical", command=file_tree.yview)
scrollbar.pack(side="right", fill="y")
file_tree.config(yscrollcommand=scrollbar.set)

action_btn_frame = Frame(root, bg="#1e1e2f")
action_btn_frame.pack(pady=3)

Button(
    action_btn_frame,
    text="📥 Download Selected",
    command=download_selected_file,
    width=18,
    bg="#0288d1",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    activebackground="#03a9f4",
    relief="flat",
    cursor="hand2",
).pack(side="left", padx=5, ipady=2)

Button(
    action_btn_frame,
    text="🗑️ Delete Selected",
    command=delete_selected_files,
    width=18,
    bg="#e53935",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    activebackground="#ef5350",
    relief="flat",
    cursor="hand2",
).pack(side="left", padx=5, ipady=2)

Label(
    root,
    text="📁 File Source (Local File or Online Link)",
    bg="#1e1e2f",
    font=("Segoe UI", 9, "bold"),
    fg="#ffeb3b",
).pack(pady=1)

source_frame = Label(root, bg="#1e1e2f")
source_frame.pack(pady=2)

Button(
    source_frame,
    text="📂 Browse",
    command=browse_file,
    width=10,
    bg="#3f51b5",
    fg="white",
    font=("Segoe UI", 8, "bold"),
    activebackground="#5c6bc0",
    relief="flat",
    cursor="hand2",
).grid(row=0, column=0, padx=4)

entry_source = Entry(
    source_frame,
    width=32,
    font=("Segoe UI", 9),
    bg="#2d2d44",
    fg="#ffffff",
    insertbackground="white",
    relief="flat",
)
entry_source.grid(row=0, column=1, padx=4, ipady=2)
entry_source.insert(0, "Enter local file path or URL")

Button(
    source_frame,
    text="🔗 Load Link",
    command=load_from_link,
    width=10,
    bg="#009688",
    fg="white",
    font=("Segoe UI", 8, "bold"),
    activebackground="#26a69a",
    relief="flat",
    cursor="hand2",
).grid(row=0, column=2, padx=4)

filename_frame = Label(root, bg="#1e1e2f")
filename_frame.pack(pady=3)

Label(
    filename_frame,
    text="Save File Name (Only Name):",
    bg="#1e1e2f",
    font=("Segoe UI", 9, "bold"),
    fg="#cfd8dc",
).pack(side="left", padx=5)

entry_filename = Entry(
    filename_frame,
    width=24,
    font=("Segoe UI", 10),
    bg="#2d2d44",
    fg="#ffffff",
    insertbackground="white",
    relief="flat",
)
entry_filename.pack(side="left", padx=5, ipady=2)

Button(
    root,
    text="🚀 Upload / Override to GitHub",
    font=("Segoe UI", 10, "bold"),
    command=upload_to_github,
    width=36,
    bg="#00c853",
    fg="white",
    activebackground="#69f0ae",
    activeforeground="#000000",
    relief="flat",
    cursor="hand2",
).pack(pady=4, ipady=3)

status_label = Label(
    root,
    text="✨ Ready",
    font=("Segoe UI", 9, "bold"),
    bg="#1e1e2f",
    fg="#90caf9",
)
status_label.pack(pady=2)

footer_label = Label(
    root,
    text="Developed by Tapas | Pro Manager Edition",
    font=("Segoe UI", 8, "italic"),
    bg="#1e1e2f",
    fg="#78909c",
)
footer_label.pack(side="bottom", pady=2)

saved_data = load_config()
if saved_data:
  if "token" in saved_data:
    entry_token.insert(0, saved_data["token"])
    fetch_repositories()
  if "last_filename" in saved_data:
    entry_filename.insert(0, saved_data["last_filename"])

root.mainloop()