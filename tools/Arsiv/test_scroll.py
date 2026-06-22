import customtkinter as ctk
app=ctk.CTk()
app.geometry('800x600')
sf=ctk.CTkScrollableFrame(app)
sf.pack(fill='both', expand=True)
for i in range(10): sf.grid_columnconfigure(i, weight=0); sf.grid_rowconfigure(i, weight=0)
sf.grid_columnconfigure(0, weight=1); sf.grid_columnconfigure(1, weight=1)
satir=0; sutun=0
for idx in range(20):
 kart=ctk.CTkFrame(sf, height=150, fg_color='red')
 kart.grid(row=satir, column=sutun, padx=12, pady=12, sticky='nsew')
 kart.grid_propagate(False)
 sutun+=1
 if sutun>=2: sutun=0; satir+=1
def res(e): pass
sf.bind('<Configure>', res)
app.update_idletasks()
print('bbox:', sf._parent_canvas.bbox('all'))
print('cget:', sf._parent_canvas.cget('scrollregion'))
