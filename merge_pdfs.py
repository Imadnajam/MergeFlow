from pathlib import Path
from pypdf import PdfWriter

# Dossier où se trouvent tes PDF
folder = Path("pdfs")

# Nom du fichier final
output = Path("merged.pdf")

writer = PdfWriter()

# Récupérer tous les PDF du dossier
pdf_files = sorted(folder.glob("*.pdf"))

if not pdf_files:
    print("Aucun fichier PDF trouvé.")
    exit()

for pdf in pdf_files:
    print(f"Ajout : {pdf.name}")
    writer.append(str(pdf))

# Créer le PDF final
with open(output, "wb") as f:
    writer.write(f)

writer.close()

print(f"\nTerminé ! {len(pdf_files)} PDF ont été fusionnés.")
print(f"Fichier créé : {output.absolute()}")