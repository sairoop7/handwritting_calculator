import nbformat
from nbformat.validator import validate, ValidationError

filename = "cnn_model.ipynb"  # change if needed

try:
    with open(filename, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Validate
    validate(nb)
    print(f"✅ {filename} is a valid notebook!")

    # Optionally, rewrite to fix formatting
    with open("cnn_model_fixed.ipynb", "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("💾 Saved a cleaned version → cnn_model_fixed.ipynb")

except ValidationError as e:
    print(f"❌ Notebook is invalid: {e}")
