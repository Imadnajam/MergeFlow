import os
import subprocess
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader, PdfWriter


def merge_pdf_files(input_files: list[str], output_file: str) -> int:
    """Merge input PDFs into output_file and return the total page count."""
    output_path = Path(output_file).resolve()
    source_paths = [Path(file_path).resolve() for file_path in input_files]
    if output_path in source_paths:
        raise ValueError(
            "Le fichier de sortie doit être différent des fichiers source."
        )

    writer = PdfWriter()
    temporary_path: Path | None = None
    try:
        total_pages = 0
        for source_path in source_paths:
            reader = PdfReader(source_path, strict=False)
            total_pages += len(reader.pages)
            writer.append(reader)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", dir=output_path.parent, delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        with temporary_path.open("wb") as temporary_file:
            writer.write(temporary_file)
        os.replace(temporary_path, output_path)
        temporary_path = None
        return total_pages
    finally:
        writer.close()
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


class PdfMergerApp:
    """Small desktop interface for selecting, ordering, and merging PDFs."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Fusionner des PDF")
        self.root.geometry("720x500")
        self.root.minsize(600, 420)
        self.root.configure(bg="#f4f6f8")

        self.pdf_files: list[str] = []
        self.last_output: Path | None = None
        self.status_var = tk.StringVar(value="Ajoutez des fichiers PDF pour commencer.")

        self._configure_style()
        self._build_interface()
        self._bind_shortcuts()
        self._update_buttons()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f4f6f8")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure(
            "Title.TLabel",
            background="#f4f6f8",
            foreground="#17202a",
            font=("Segoe UI", 19, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#f4f6f8",
            foreground="#5f6b76",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Card.TLabel",
            background="#ffffff",
            foreground="#25313c",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Status.TLabel",
            background="#f4f6f8",
            foreground="#52606d",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8)
        )
        style.configure("Action.TButton", font=("Segoe UI", 10), padding=(10, 7))

    def _build_interface(self) -> None:
        main = ttk.Frame(self.root, style="App.TFrame", padding=24)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        ttk.Label(main, text="Fusionner des PDF", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            main,
            text="Sélectionnez vos documents, arrangez-les, puis créez un seul fichier PDF.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        card = ttk.Frame(main, style="Card.TFrame", padding=16)
        card.grid(row=2, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(card, style="Card.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.add_button = ttk.Button(
            toolbar,
            text="Ajouter des PDF",
            style="Primary.TButton",
            command=self.add_pdfs,
        )
        self.add_button.pack(side="left")
        self.remove_button = ttk.Button(
            toolbar,
            text="Supprimer",
            style="Action.TButton",
            command=self.remove_selected,
        )
        self.remove_button.pack(side="left", padx=(10, 0))
        self.clear_button = ttk.Button(
            toolbar,
            text="Vider la liste",
            style="Action.TButton",
            command=self.clear_list,
        )
        self.clear_button.pack(side="left", padx=(10, 0))

        list_frame = ttk.Frame(card, style="Card.TFrame")
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.file_list = tk.Listbox(
            list_frame,
            height=12,
            activestyle="none",
            selectmode=tk.SINGLE,
            font=("Segoe UI", 10),
            bg="#fbfcfd",
            fg="#25313c",
            selectbackground="#2f80ed",
            selectforeground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#b8c7d6",
            highlightbackground="#dbe2e8",
        )
        self.file_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.file_list.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_list.configure(yscrollcommand=scrollbar.set)
        self.file_list.bind("<<ListboxSelect>>", lambda _event: self._update_buttons())

        order_frame = ttk.Frame(card, style="Card.TFrame")
        order_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self.move_up_button = ttk.Button(
            order_frame, text="Monter", style="Action.TButton", command=self.move_up
        )
        self.move_up_button.pack(side="left")
        self.move_down_button = ttk.Button(
            order_frame,
            text="Descendre",
            style="Action.TButton",
            command=self.move_down,
        )
        self.move_down_button.pack(side="left", padx=(8, 0))
        ttk.Label(
            order_frame,
            text="L’ordre affiché sera utilisé pour la fusion.",
            style="Card.TLabel",
        ).pack(side="right")

        footer = ttk.Frame(main, style="App.TFrame")
        footer.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.open_button = ttk.Button(
            footer,
            text="Ouvrir le dossier",
            style="Action.TButton",
            command=self.open_output_folder,
        )
        self.open_button.grid(row=0, column=1, padx=(10, 8))
        self.merge_button = ttk.Button(
            footer,
            text="Fusionner les PDF",
            style="Primary.TButton",
            command=self.merge_pdfs,
        )
        self.merge_button.grid(row=0, column=2)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-o>", lambda _event: self.add_pdfs())
        self.root.bind("<Delete>", lambda _event: self.remove_selected())
        self.root.bind("<Control-Up>", lambda _event: self.move_up())
        self.root.bind("<Control-Down>", lambda _event: self.move_down())

    def _update_buttons(self) -> None:
        has_files = bool(self.pdf_files)
        has_selection = bool(self.file_list.curselection())
        self.merge_button.configure(state="normal" if has_files else "disabled")
        self.open_button.configure(state="normal" if self.last_output else "disabled")
        self.remove_button.configure(state="normal" if has_selection else "disabled")
        self.clear_button.configure(state="normal" if has_files else "disabled")
        self.move_up_button.configure(state="normal" if has_selection else "disabled")
        self.move_down_button.configure(state="normal" if has_selection else "disabled")

    def add_pdfs(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Choisir les fichiers PDF",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
        )
        for file_path in selected:
            if file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                self.file_list.insert(tk.END, Path(file_path).name)
        if selected:
            self.file_list.selection_clear(0, tk.END)
            self.file_list.selection_set(tk.END)
            self.file_list.see(tk.END)
            self.last_output = None
            self.status_var.set(f"{len(self.pdf_files)} fichier(s) sélectionné(s).")
        self._update_buttons()

    def remove_selected(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        index = selection[0]
        self.file_list.delete(index)
        self.pdf_files.pop(index)
        if self.pdf_files:
            self.file_list.selection_set(min(index, len(self.pdf_files) - 1))
        self.status_var.set(f"{len(self.pdf_files)} fichier(s) dans la liste.")
        self._update_buttons()

    def clear_list(self) -> None:
        self.pdf_files.clear()
        self.file_list.delete(0, tk.END)
        self.last_output = None
        self.status_var.set("La liste a été vidée.")
        self._update_buttons()

    def move_up(self) -> None:
        self._move_selected(-1)

    def move_down(self) -> None:
        self._move_selected(1)

    def _move_selected(self, offset: int) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        current = selection[0]
        target = current + offset
        if not 0 <= target < len(self.pdf_files):
            return
        self.pdf_files[current], self.pdf_files[target] = (
            self.pdf_files[target],
            self.pdf_files[current],
        )
        label = self.file_list.get(current)
        self.file_list.delete(current)
        self.file_list.insert(target, label)
        self.file_list.selection_set(target)
        self.file_list.activate(target)
        self._update_buttons()

    def merge_pdfs(self) -> None:
        if not self.pdf_files:
            messagebox.showwarning(
                "Aucun PDF", "Sélectionnez au moins un fichier PDF avant de continuer."
            )
            return

        output_path = filedialog.asksaveasfilename(
            title="Enregistrer le PDF fusionné",
            defaultextension=".pdf",
            filetypes=[("Fichier PDF", "*.pdf")],
            initialfile="documents_fusionnes.pdf",
        )
        if not output_path:
            self.status_var.set("Enregistrement annulé.")
            return

        try:
            page_count = merge_pdf_files(self.pdf_files, output_path)
        except ValueError as error:
            messagebox.showwarning("Destination invalide", str(error))
            self.status_var.set(
                "Choisissez une destination différente des fichiers source."
            )
            return
        except Exception as error:
            messagebox.showerror(
                "Fusion impossible",
                f"Le PDF n’a pas pu être créé.\n\nDétail : {error}",
            )
            self.status_var.set("Une erreur est survenue pendant la fusion.")
            return

        self.last_output = Path(output_path)
        self.status_var.set(
            f"Fusion terminée : {self.last_output.name} ({page_count} pages)"
        )
        self._update_buttons()
        messagebox.showinfo(
            "Fusion terminée",
            f"{len(self.pdf_files)} PDF ont été fusionnés.\n\nFichier créé :\n{self.last_output}",
        )

    def open_output_folder(self) -> None:
        if not self.last_output:
            return
        folder = self.last_output.parent
        try:
            if sys.platform == "win32":
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)], check=False)
            else:
                subprocess.run(["xdg-open", str(folder)], check=False)
        except OSError as error:
            messagebox.showerror(
                "Ouverture impossible",
                f"Le dossier ne peut pas être ouvert.\n\nDétail : {error}",
            )


def main() -> None:
    root = tk.Tk()
    PdfMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
