from tkinter import ttk

class CustomizedLabelFrame(ttk.LabelFrame):

    def __init__(self, *args, **kvargs):
        ttk.LabelFrame.__init__(self, *args, **kvargs)

    def enable(self, enabled):
        for child in self.winfo_children():
            wtype = child.winfo_class()
            print(wtype)
            if wtype not in ('Frame','Labelframe','TSeparator'):
                child.configure(state=('normal' if enabled else 'disable'))
