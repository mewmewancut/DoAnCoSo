import os
import subprocess
import sys

def compile_po_to_mo(po_file, mo_file):
    try:
        import polib
    except ImportError:
        print("Installing polib...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "polib"])
        import polib
    
    try:
        po = polib.pofile(po_file)
        po.save_as_mofile(mo_file)
        print(f"[OK] Compiled {po_file} -> {mo_file}")
        return True
    except Exception as e:
        print(f"[ERROR] Error compiling {po_file}: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_dir = os.path.join(base_dir, "locale")
    
    languages = ["en", "vi"]
    
    for lang in languages:
        po_file = os.path.join(locale_dir, lang, "LC_MESSAGES", "django.po")
        mo_file = os.path.join(locale_dir, lang, "LC_MESSAGES", "django.mo")
        
        if os.path.exists(po_file):
            compile_po_to_mo(po_file, mo_file)
        else:
            print(f"[ERROR] File not found: {po_file}")

if __name__ == "__main__":
    main()

